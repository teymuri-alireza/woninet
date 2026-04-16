import socket
import time
import threading
from datetime import datetime
from typing import List, Dict
from utilities.logger import logger_function
from utilities.arguments import args

# Global Variables
SOCKET = "8.8.8.8"

# Get Logger Configuration
rootLogger = logger_function()

argument = args()

# The --version Argument
if argument.version:
    from utilities.version import show_version
    print(show_version())
    exit(0)

# Set Verbosity
if argument.verbose:
    from logging import DEBUG
    rootLogger.setLevel(DEBUG)

# Fetch The Local IP Address
try:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect((SOCKET, 80))
        local_ip = s.getsockname()[0]
except OSError:
    rootLogger.error("Network is unreachable. Quitting.")
    exit(1)
except Exception as e:
    rootLogger.error(f"Error at socket connection in main.py: {e}")
    exit(1)

# Data Models
class Device:
    def __init__(self, ip: str):
        self.ip = ip
        self.last_seen = None
        self.metrics = {} # Bandwidth, CPU, etc
    
    def update_seen(self):
        self.last_seen = datetime.now()


class MetricRecord:
    def __init__(self, device_ip: str, metric: str, value: float, timestamp=None):
        self.device_ip = device_ip
        self.metric = metric
        self.value = value
        self.timestamp = timestamp or datetime.now()

# Collectors
class BaseCollector:
    interval = 10

    def collect(self, devices: Dict[str, Device]) -> List[MetricRecord]:
        raise NotImplementedError

    def run(self, devices: Dict[str, Device], store_callback):
        while True:
            result = self.collect(devices)
            store_callback(result)
            time.sleep(self.interval)


class PingCollector(BaseCollector):
    interval = 5

    def collect(self, devices: Dict[str, Device]) -> List[MetricRecord]:
        results = []
        for ip, dev in devices.items():
            latency = self.ping(ip)
            dev.update_seen()
            results.append(MetricRecord(ip, "latency_ms", latency))
        return results

    @staticmethod
    def ping(ip):
        # Requires Logic
        return 1000

# Device Discovery
class DiscoveryEngine:
    def scan_subnet(self, ip_addr: str) -> Dict[str, Device]:
        ip_split = ip_addr.split(".")
        subnet = f"{ip_split[0]}.{ip_split[1]}.{ip_split[2]}"
        devices = {}
        for i in range(1, 255):
            ip = f"{subnet}.{i}"
            devices[ip] = Device(ip)
        return devices

# Storage
class StorageEngine:
    def __init__(self):
        self.history: List[MetricRecord] = []

    def store(self, metrics: List[MetricRecord]):
        self.history.extend(metrics)

    def get_history(self, ip: str, metric: str) -> List[MetricRecord]:
        return [m for m in self.history if m.device_ip == ip and m.metric == metric]

# Alert
class AlertRule:
    def __init__(self, metric: str, threshold: float, duration: int):
        self.metric = metric
        self.threshold = threshold
        self.duration = duration


class AlertEngine:
    def __init__(self, storage: StorageEngine, rules: List[AlertRule]):
        self.storage = storage
        self.rules = rules

    def evaluate(self):
        for rule in self.rules:
            for record in self.storage.history:
                if record.metric == rule.metric and record.value > rule.threshold:
                    print(f"[ALERT] {record.device_ip} exceeded {rule.metric}: {record.value}")

# Main Collector
class NetworkMonitorCore:
    def __init__(self, ip_addr: str):
        self.discovery = DiscoveryEngine()
        self.storage = StorageEngine()

        self.devices = self.discovery.scan_subnet(ip_addr)

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
        for collector in self.collectors:
            thread = threading.Thread(
                target=collector.run,
                args=(self.devices, self.storage.store),
                daemon=True
            )
            thread.start()

        while True:
            self.alert_engine.evaluate()
            time.sleep(3)


if __name__ == "__main__":
    monitor = NetworkMonitorCore(ip_addr=local_ip)
    monitor.start()
