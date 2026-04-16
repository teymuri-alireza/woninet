import socket
import time
import ping3
from datetime import datetime
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor
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

    def collect(self, devices: Dict[str, Device], ip_addr: str) -> List[MetricRecord]:
        raise NotImplementedError

    def run(self, devices: Dict[str, Device], ip_addr, store_callback):
        # while True:
            result = self.collect(devices, ip_addr=ip_addr)
            store_callback(result)
            # time.sleep(self.interval)


class PingCollector(BaseCollector):
    interval = 5

    def collect(self, devices: Dict[str, Device], ip_addr: str) -> List[MetricRecord]:
        results = []
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = {}

            for ip, dev in devices.items():
                future = executor.submit(self.ping, ip, ip_addr)
                futures[future] = (ip, dev)
            
            for future in futures:
                ip, dev = futures[future]
                dev.update_seen()

                try:
                    latency = future.result()
                except Exception as e:
                    rootLogger.error(f"Error at PingCollector class: {e}")
                    latency = None

                results.append(MetricRecord(ip, "latency_ms", latency))
        
        return results

    @staticmethod
    def ping(ip, src_addr):
        response = ping3.ping(src_addr=src_addr, dest_addr=ip.strip(), timeout=1, ttl=64)
        if response is None or response is False:
            return None # Unreachable
        latency = response * 1000 # Convert to milliseconds
        rootLogger.debug(f"ip address: {ip} - latency: {latency:.2f} ms")
        return latency

# Device Discovery
class DiscoveryEngine:
    def scan_subnet(self, ip_addr: str) -> Dict[str, Device]:
        ip_split = ip_addr.split(".")
        subnet = f"{ip_split[0]}.{ip_split[1]}.{ip_split[2]}"
        rootLogger.debug(f"Discover subnet base on {subnet}.x")
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
    
    def clear_history(self):
        self.history: List[MetricRecord] = []

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
                if record.value is not None and record.value is not False:
                    if record.metric == rule.metric and record.value > rule.threshold:
                        rootLogger.warning(f"[ALERT] {record.device_ip} exceeded {rule.metric}: {record.value:.2f}")
        self.storage.clear_history()

# Main Collector
class NetworkMonitorCore:
    def __init__(self, ip_addr: str):
        rootLogger.info(f"Initializing network monitor for {ip_addr}")
        
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

        while True:
            for collector in self.collectors:
                collector.run(self.devices, local_ip, self.storage.store)
                self.alert_engine.evaluate()
            time.sleep(5)


if __name__ == "__main__":
    try:
        monitor = NetworkMonitorCore(ip_addr=local_ip)
        monitor.start()
    except KeyboardInterrupt:
        rootLogger.info("Keyboard Interrupted. Wait for shutting down.")
    except Exception as e:
        rootLogger.error(f"Error occured: {e}")
        exit(1)