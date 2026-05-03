import time
import logging
import threading
from datetime import datetime
from sqlalchemy import text, inspect
from sqlalchemy.exc import SQLAlchemyError
from icmplib import SocketPermissionError, SocketAddressError
from woninet.core.models import Device
from woninet.core.collectors import PingCollector
from woninet.core.storage import StorageEngine
from woninet.core.alerts import AlertEngine, AlertRule
from woninet.core.subnet_enumerator import SubnetEnumerator
from woninet.database.engine import SessionLocal, init_db, engine

core_logger = logging.getLogger("core")


class NetworkMonitorCore:
    """
    Central controller coordinating discovery, collectors,
    storage, and alert processing.
    """

    def __init__(self, ip_addr: str, arp_noise_limit: float) -> None:
        """
        Initialize the monitor core.

        Args:
            ip_addr: Source IP address used to send packets.
            arp_noise_limit: Parameter which sets a limit to filter the ARP delay noise.
        """
        self._running: bool = False
        self._thread: threading.Thread | None = None
        self._stop_event: threading.Event = threading.Event()
        self._start_uptime = datetime.now()
        self._engine = engine

        self.ip_addr: str = ip_addr
        self.arp_noise_limit: float = arp_noise_limit

        # Initialize database
        init_db()

        core_logger.info(f"Initializing network monitor for {self.ip_addr}")

        self.subnet_enumerator = SubnetEnumerator()
        self.storage = StorageEngine(session_factory=SessionLocal)

        self.devices = self.subnet_enumerator.scan_subnet(self.ip_addr)

        self.collectors = [
            PingCollector(),
        ]

        self.alert_engine = AlertEngine(
            storage=self.storage,
            rules=[
                AlertRule("latency_ms", 100, 10),
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
                for collector in self.collectors:
                    if not self._running or self._stop_event.is_set():
                        break

                    collector.run(
                        self.devices,
                        self.ip_addr,
                        self.storage,
                        stop_event=self._stop_event,
                        arp_noise_limit=self.arp_noise_limit,
                    )
                    self.alert_engine.evaluate()
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

    def get_devices(self) -> list[Device]:
        """
        Return all devices in the history.
        """
        return self.storage.get_history()

    def get_history_count(self) -> tuple[int, int]:
        """
        Return number of devices and metrics in the history.
        """
        return self.storage.get_database_count()

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

        Returns a dictionary with two keys:

        - 'connection': 'ok' if executing `SELECT 1` succeeds, otherwise 'error'.
        - 'schema': 'ok' if database table inspection succeeds, otherwise 'error'.
        If the database connection fails, this value is 'unknown'.

        Returns:
            dict[str,str]: A dictionary containing the connection and schema
            health status.
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
