import time
import threading
from icmplib import SocketPermissionError, SocketAddressError
from typing import List
from woninet.core.models import Device
from woninet.core.collectors import PingCollector
from woninet.core.storage import StorageEngine
from woninet.core.alerts import AlertEngine, AlertRule
from woninet.core.subnet_enumerator import SubnetEnumerator
from woninet.utilities.logger import get_core_logger

core_logger = get_core_logger()


class NetworkMonitorCore:
    """
    Central controller coordinating discovery, collectors,
    storage, and alert processing.
    """

    def __init__(self, ip_addr: str):
        self._running = False
        self._thread = None
        self._stop_event = threading.Event()

        self.ip_addr = ip_addr

        core_logger.info(f"Initializing network monitor for {self.ip_addr}")

        self.subnet_enumerator = SubnetEnumerator()
        self.storage = StorageEngine()

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

    def start(self):
        """
        Starts the monitoring worker thread.
        """
        if self._running:
            return

        self._running = True
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self.worker_loop, name="woninet-worker", daemon=False
        )
        self._thread.start()

    def stop(self):
        """
        Stops the monitoring worker thread.
        """
        if not self._running:
            return

        self._running = False
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=3)

    def wait(self) -> None:
        """
        Blocks until the worker thread finishes.
        """
        if self._thread:
            self._thread.join()

    def worker_loop(self) -> None:
        """
        Main monitoring loop.
        Starts the collectors and evaluate alerts.
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

    def get_devices(self) -> List[Device]:
        """
        Return the stored history.
        """
        return self.storage.get_history()
