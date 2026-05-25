import time
import logging
import threading
from datetime import datetime
from typing import Any
from sqlalchemy import text, inspect
from sqlalchemy.exc import SQLAlchemyError
from icmplib import SocketPermissionError, SocketAddressError
from woninet.core.models import Device, MetricRecord
from woninet.core.collectors import PingCollector
from woninet.core.storage import StorageEngine
from woninet.core.alerts import AlertEngine, AlertRule
from woninet.core.subnet_enumerator import SubnetEnumerator
from woninet.core.manual_ip_enumerator import ManualIPEnumerator
from woninet.database.engine import DatabaseEngine
from woninet.database.tables import AlertEventTable
from woninet.utilities.ip_validator import is_device_ip_valid
from woninet.utilities.detect_ip_range import detect_ip_range

core_logger = logging.getLogger("core")


class NetworkMonitorCore:
    """
    Central controller coordinating database initialization, telemetry
    collection, persistence, and heuristic alert processing.

    This class acts as the orchestrator for the network monitoring lifecycle,
    managing thread pools for asynchronous ICMP polling and interfacing with
    the SQLite persistence layer via SQLAlchemy.

    Attributes:
        local_ip (str): The source interface IP used for packet origination.
        arp_noise_limit (float): Statistical threshold for filtering jitter
            in ARP resolution timings.
        max_thread_workers (int): The concurrency limit for the
            `ThreadPoolExecutor` handling ICMP probes.
        database_engine (DatabaseEngine): The high-level wrapper for
            SQLAlchemy engine configuration.
        storage (StorageEngine): The Data Access Object (DAO) layer for
            CRUD operations on network metrics.
        alert_engine (AlertEngine): Logic processor for evaluating
            latency-based threshold breaches.
        candidate_devices (list): A list of IP addresses identified during
            the initial enumeration phase.
        _stop_event (threading.Event): Primitive used to signal graceful
            shutdown to the background worker thread.
    """

    def __init__(
        self,
        local_ip: str,
        target_ip: str,
        arp_noise_limit: float,
        database_path: str,
        max_thread_workers: int,
    ) -> None:
        """
        Initialize the monitor core and prepare the persistence layer.

        Args:
            local_ip (str): Source IP address used to send packets.
            target_ip (str): User-provided IP address or range to scan.
            arp_noise_limit (float): Threshold in milliseconds above which ARP
                fluctuations are treated as noise.
            database_path (str): Path to SQLite database.
            max_thread_workers (int): Maximum number of thread workers used to send ICMP pings.
        """
        self._running: bool = False
        self._thread: threading.Thread | None = None
        self._stop_event: threading.Event = threading.Event()
        self._start_uptime = datetime.now()

        self.local_ip: str = local_ip
        self.arp_noise_limit: float = arp_noise_limit
        self.max_thread_workers: int = max_thread_workers
        self.consecutive_checks: dict[str, int] = {
            "latency_ms": 2,
            "packet_loss": 0,
        }

        # Initialize database
        self.database_engine = DatabaseEngine(database_path=database_path)
        self.database_engine.init_db()
        self._engine = self.database_engine.get_database_enigne()
        self.session_factory = self.database_engine.get_session_factory()

        core_logger.info(f"Initializing network monitor for {self.local_ip}")

        self.subnet_enumerator = SubnetEnumerator()
        self.manual_ip_enumerator = ManualIPEnumerator()
        self.storage = StorageEngine(session_factory=self.session_factory)

        self.candidate_devices = self.enumerate_candidate_devices(target_ip)

        self.ping_collector = PingCollector()

        self.alert_engine = AlertEngine(
            storage=self.storage,
            rules=[
                AlertRule("latency_ms", 100, self.consecutive_checks["latency_ms"]),
                AlertRule("packet_loss", 0.0, self.consecutive_checks["packet_loss"]),
            ],
        )

    def start(self) -> None:
        """
        Start the monitoring worker thread.
        """
        if self._running:
            return

        self._running = True
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self.worker_loop, name="woninet-worker", daemon=False
        )
        self._thread.start()

    def stop(self) -> None:
        """
        Stop the monitoring worker thread.
        """
        if not self._running:
            return

        self._running = False
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=3)

    def wait(self) -> None:
        """
        Block until the worker thread finishes.
        """
        if self._thread:
            self._thread.join()

    def worker_loop(self) -> None:
        """
        Main monitoring loop.
        Start the collectors and evaluate alerts.
        """
        try:
            while self._running and not self._stop_event.is_set():
                if not self._running or self._stop_event.is_set():
                    break

                for result in self.ping_collector.collect(
                    candidate_devices=self.candidate_devices,
                    local_ip=self.local_ip,
                    device_records=self.get_device_history(),
                    stop_event=self._stop_event,
                    arp_noise_limit=self.arp_noise_limit,
                    max_thread_workers=self.max_thread_workers,
                ):
                    try:
                        device, latency_metric, packet_loss_metric = result
                        self.submit_to_history(
                            device=device, metrics=[latency_metric, packet_loss_metric]
                        )
                        if device is not None:
                            self.alert_engine.evaluate(
                                ip=device.ip,
                                metrics_list=[latency_metric, packet_loss_metric],
                                default_consecutive_checks={
                                    "latency_ms": self.consecutive_checks["latency_ms"],
                                    "packet_loss": self.consecutive_checks[
                                        "packet_loss"
                                    ],
                                },
                            )
                    except ValueError:
                        # If the tuple doesn't have enough values to unpack
                        pass
                time.sleep(1)
        except (PermissionError, SocketPermissionError):
            core_logger.error("woninet requires root privileges to scan.")
            self._running = False
            self._stop_event.set()
        except SocketAddressError:
            core_logger.error("Network connection failed. Quitting.")
            self._running = False
            self._stop_event.set()
        except Exception as e:
            core_logger.error(f"Unexpected error in NetworkMonitorCore: {e}")
            self._running = False
            self._stop_event.set()
        finally:
            self._running = False
            self._stop_event.set()

    def is_alive(self) -> bool:
        """
        Return the running state of monitor.
        """
        return self._running

    def get_device_history(self) -> list[Device]:
        """
        Return a list of all devices in the history.
        """
        return self.storage.list_device_history()

    def get_device_info(
        self, ip: str
    ) -> tuple[Device | None, dict[str, str] | None, list[AlertEventTable]]:
        """
        Retrieve device information and related alert data for a given IP address.

        Args:
            ip (str): IP address of the device to search for.

        Returns:
            tuple[Device|None,dict[str,str]|None,list[AlertEventTable]]:
                A tuple containing

                1. The found device, or `None` if no device exists for the given IP.
                2. The current alert state as `(metric_name, value)`, or `None` if no state exists.
                3. The last 10 alert events for the device, or an empty list if none exist.
        """
        device_info = self.storage.fetch_device_info(ip=ip)
        device_alert_state = self.storage.get_device_alert_state(ip=ip)
        recent_device_alert_events = self.storage.get_recent_device_alert_events(ip=ip)
        return (device_info, device_alert_state, recent_device_alert_events)

    def classify_recent_alert_events(self) -> list[dict[str, Any]]:
        """
        Re-order and organize the recent alert events
        dictionary keys and values.
        """
        result = []
        for event in self.storage.get_recent_alert_events():
            result.append(
                {
                    "device_ip": event.device_ip,
                    "id": event.id,
                    "metric": event.metric,
                    "event_type": event.event_type,
                    "value": event.value,
                    "timestamp": event.timestamp,
                }
            )
        return result

    def count_resources(self) -> tuple[int, int]:
        """
        Return number of devices and metrics in the history.
        """
        return self.storage.count_devices_and_metrics()

    def submit_to_history(self, device: str, metrics: list[MetricRecord]) -> None:
        """
        Handle storing new devices and metrics in history.
        """
        if isinstance(device, Device):
            self.storage.store_device(device=device)
        for metric in metrics:
            if isinstance(metric, MetricRecord):
                self.storage.store_metric(metric=metric)

    def enumerate_candidate_devices(self, target_ip: str | None) -> dict[str, Device]:
        """
        Control enumeration based on user-provided IP address. Use range enumeration
        if IP range is detected, otherwise use the single IP address. Enumerate on the
        /24 subnet if no target IP address is provided.

        Args:
            target_ip (str|None): Target IP address to create candidate devices on.

        Returns:
            dict[str,Device]: Candidate devices.

        Raises:
            ValueError: If IP addresses are not valid.
        """
        if target_ip is not None:
            if detect_ip_range(ip=target_ip):
                candidate_devices = self.manual_ip_enumerator.enumerate_range(target_ip)
            else:
                candidate_devices = {target_ip: Device(ip=target_ip)}
        else:
            candidate_devices = self.subnet_enumerator.enumerate(self.local_ip)
        if not is_device_ip_valid(candidate_devices):
            raise ValueError("IP address is not valid")
        return candidate_devices

    def uptime(self) -> int:
        """
        Calculate the uptime of program from the initialization of the
        NetworkMonitorCore class.

        Returns:
            int: Uptime in seconds.
        """
        uptime_seconds = datetime.now() - self._start_uptime
        return uptime_seconds.seconds

    def database_health(self) -> dict[str, str]:
        """
        Check the health status of the database.

        Returns:
            dict[str,str]: A dictionary with two keys

            - 'connection': 'ok' if executing `SELECT 1` succeeds, otherwise 'error'.
            - 'schema': 'ok' if database table inspection succeeds, otherwise 'error'.
            If the database connection fails, this value is 'unknown'.
        """
        result = {
            "connection": "error",
            "schema": "unknown",
        }
        try:
            # Check connection
            with self._engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            result["connection"] = "ok"

            # Check tables existence
            inspect_engine = inspect(self._engine)
            tables = inspect_engine.get_table_names()
            required = {"devices", "metrics"}
            if required.issubset(set(tables)):
                result["schema"] = "ok"
            else:
                result["schema"] = "error"
        except SQLAlchemyError:
            # Keep default values
            pass

        return result
