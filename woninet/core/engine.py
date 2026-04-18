import time
from .collectors import PingCollector
from .storage import StorageEngine
from .alerts import AlertEngine, AlertRule
from .subnet_enumerator import SubnetEnumerator
from ..utilities.logger import logger_function

rootLogger = logger_function()

class NetworkMonitorCore:
    """
    Central controller coordinating discovery, collectors,
    storage, and alert processing.
    """
    def __init__(self, ip_addr: str):
        self.ip_addr = ip_addr

        rootLogger.info(f"Initializing network monitor for {self.ip_addr}")
        
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
            ]
        )

    def start(self):
        """
        Start the collectors and continuously evaluate alerts.
        """
        while True:
            for collector in self.collectors:
                collector.run(self.devices, self.ip_addr, self.storage.store)
                self.alert_engine.evaluate()
            time.sleep(5)