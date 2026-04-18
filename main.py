import socket
import time
import ping3
import re
import subprocess
import logging
from datetime import datetime
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor
from utilities.logger import logger_function, TRACE_LEVEL
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
if argument.verbose == 0:
    pass
elif argument.verbose == 1:
    rootLogger.setLevel(logging.DEBUG)
else:
    rootLogger.setLevel(TRACE_LEVEL)

# Fetch The Local IP Address
try:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        rootLogger.trace(f"Sending a dummy UDP request to {SOCKET}:80")
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
    """
    Represents a discovered network device.
    Stores identity information and the latest known metrics and state.
    """
    def __init__(self, ip: str):
        self.ip: str = ip
        self.last_seen: Optional[datetime] = None
        self.metrics: Dict[str, float] = {} # Bandwidth, CPU, etc
    
        self.exists: bool = False # True if ARP has seen this IP
        self.reachable: bool = False # True if ICMP is sane and within latency threshold
        self.mac: Optional[str] = None # MAC address from ARP table
        self.latency: Optional[float] = None
    def update_seen(self):
        """
        Update timestamp indicating the device responded recently.
        """
        self.last_seen = datetime.now()


class MetricRecord:
    """
    Represents a single collected metric measurement
    for a specific device at a specific time.
    """
    def __init__(self, device_ip: str, metric: str, value: float, timestamp=None):
        self.device_ip = device_ip
        self.metric = metric
        self.value = value
        self.timestamp = timestamp or datetime.now()

# ARP and ICMP detection
class HostStatus:
    """
    Combined ARP + ICMP status for a given IP
    """
    def __init__(self, ip: str, exists: bool = False, reachable: bool = False, latency: Optional[float] = None, mac: Optional[str] = None):
        self.ip = ip
        self.exists = exists
        self.reachable = reachable
        self.latency = latency # in milliseconds
        self.mac = mac


def get_arp_mac(ip: str) -> Optional[str]:
    """
    Return MAC address from ARP table for the given IP, or None if not present.

    Notes:
        - Uses `arp -an` output and parses it.
        - Works on most Unix-like systems. If fails, it simply returns None and rely on ICMP only.
    """
    try:
        # Suppress strerr to avoid clutter when ARP table is empty or limited
        output = subprocess.check_output(["arp", "-an"], stderr=subprocess.DEVNULL)
        output = output.decode()
    except Exception as e:
        rootLogger.debug(f"Failed to read ARP table: {e}")
        return None

    regex = rf"\({re.escape(ip)}\)\s+at\s+([0-9a-fA-F:]+)\s"
    match = re.search(regex, output)
    if match:
        return match.group(1)
    return None


def detect_host(ip: str, src_addr: str, timeout: float = 1.0) -> HostStatus:
    """
    Combined ARP + ICMP detection for accurate device status.

    Rules:
        - If ARP_FAIL and ICMP_FAIL -> Host does NOT exist (exists=False, reachable=False)
        - If ARP_OK and ICMP_FAIL -> Host exists but unreachable / ICMP blocked
        - If ARP_OK and ICMP_OK < 300 ms -> Host is reachable
        - If ARP_OK and ICMP_OK >= 300 ms -> Treat as ARP-timeout noise (unreachable)
    """
    status = HostStatus(ip=ip)

    # Skip source ip to prevent confusion.
    if ip == src_addr:
        status.exists = None
        status.reachable = None
        status.mac = None
        status.latency = None
        return status

    # ARP check
    mac = get_arp_mac(ip=ip)
    if mac:
        status.exists = True
        status.mac = mac
    
    # ICMP check
    try:
        response = ping3.ping(src_addr=src_addr, dest_addr=ip.strip(), timeout=timeout, ttl=64)
    except PermissionError:
        raise
    except Exception as e:
        rootLogger.error(f"Error during ICMP ping at detect_host function, to {ip}: {e}")
        response = None
    
    latency: Optional[float] = None
    if response is not None and response is not False:
        latency = response * 1000 # Convert to milliseconds

    status.latency = latency

    # Classification logic
    if not mac and latency is None:
        # Host is not in ARP table and doesn't respond to ICMP
        status.exists = False
        status.reachable = False
        return status
    
    if mac and latency is None:
        # Device exists but doesn't respond to ICMP
        status.exists = True
        status.reachable = False
        return status

    if latency is not None:
        if latency < 300.0:
            # Acceptable latency (reachable)
            status.exists = bool(mac)
            status.reachable = True
        else:
            # High-latency ICMP, often ARP resolution noise (unreachable)
            status.exists = bool(mac)
            status.reachable = False

    return status


# Collectors
class BaseCollector:
    """
    Abstract base class for all monitoring collectors.
    Each collector periodically gathers metrics from devices.
    """
    interval = 10

    def collect(self, devices: Dict[str, Device], ip_addr: str) -> List[MetricRecord]:
        """
        Collect metrics from devices.
        Must be implemented by subclasses.
        """
        raise NotImplementedError

    def run(self, devices: Dict[str, Device], ip_addr, store_callback):
        """
        Main execution loop for the collector.
        Runs forever and periodically sends collected metrics to storage.
        """
        result = self.collect(devices, ip_addr=ip_addr)
        store_callback(result)


class PingCollector(BaseCollector):
    """
    Collector that measures ICMP latency to devices,
    enhanced with ARP-based existence detection.
    """
    interval = 5

    def collect(self, devices: Dict[str, Device], ip_addr: str) -> List[MetricRecord]:
        """
        For each device:
            - Use ARP + ICMP to determine existence and reachability.
            - Update Device fields.
            - Record latency metric only when reachable and latency is sane.
        """
        results: List[MetricRecord] = []

        def worker(ip: str, dev: Device) -> MetricRecord:
            try:
                status = detect_host(ip=ip, src_addr=ip_addr, timeout=1)
            except PermissionError:
                raise

            # Update device state from status
            dev.exists = status.exists
            dev.reachable = status.reachable
            dev.mac = status.mac
            dev.latency = status.latency

            if status.reachable:
                # Only consider reachable hosts as recently seen
                dev.update_seen()
            
            value = status.latency if status.reachable else None

            if value is not None:
                rootLogger.debug(
                    f"Device {ip}: exists={dev.exists}, reachable={dev.reachable}, "
                    f"MAC={dev.mac}, latency={value:.2f} ms"
                )
            else:
                if dev.exists:
                    rootLogger.debug(
                        f"Device {ip}: exists={dev.exists}, reachable={dev.reachable}, "
                        f"MAC={dev.mac}, latency=None"
                    )
                else:
                    rootLogger.trace(
                        f"Device {ip}: exists={dev.exists}, reachable={dev.reachable}, "
                        f"MAC={dev.mac}, latency=None"
                    )
                pass
            
            return MetricRecord(ip, "latency_ms", value)

        with ThreadPoolExecutor(max_workers=20) as executor:
            future_to_ip = {
                executor.submit(worker, ip, dev): ip
                for ip, dev in devices.items()
            }

            for future in future_to_ip:
                try:
                    metric = future.result()
                except PermissionError:
                    rootLogger.error("pymonitor requires sudo to scan.")
                    exit(1)
                except Exception as e:
                    ip = future_to_ip[future]
                    rootLogger.error(f"Error in PingCollector for {ip}: {e}")
                    continue
                else:
                    results.append(metric)

        return results

# Device Discovery
class SubnetEnumerator:
    """
    Build a dictionary of candidate devices within the local /24 subnet.

    Note:
        This does NOT confirm reachability; it only enumerates IPs.
        Logic in PingCollector will determine existence and reachability.
    """
    def scan_subnet(self, ip_addr: str) -> Dict[str, Device]:
        ip_split = ip_addr.split(".")
        subnet = f"{ip_split[0]}.{ip_split[1]}.{ip_split[2]}"
        rootLogger.debug(f"Building a dictionaty of IP addresses base on {subnet}.x")
        devices = {}
        for i in range(1, 255):
            ip = f"{subnet}.{i}"
            devices[ip] = Device(ip)
        return devices

# Storage
class StorageEngine:
    """
    Stores collected metric data.
    """
    def __init__(self):
        self.history: List[MetricRecord] = []

    def store(self, metrics: List[MetricRecord]):
        """
        Persist newly collected metrics.
        """
        self.history.extend(metrics)

    def get_history(self, ip: str, metric: str) -> List[MetricRecord]:
        """
        Retrieve historical metric records for a device.
        """
        return [m for m in self.history if m.device_ip == ip and m.metric == metric]
    
    def clear_history(self):
        """
        Clears history to prevent confusion in Alert section.
        """
        self.history = []

# Alert
class AlertRule:
    """
    Defines a monitoring rule that triggers an alert
    when a metric exceeds a defined threshold.
    """
    def __init__(self, metric: str, threshold: float, duration: int):
        self.metric = metric
        self.threshold = threshold
        self.duration = duration


class AlertEngine:
    """
    Evaluates stored metrics against alert rules
    and generates alerts when conditions are violated.
    """
    def __init__(self, storage: StorageEngine, rules: List[AlertRule]):
        self.storage = storage
        self.rules = rules

    def evaluate(self):
        """
        Scan stored metrics and trigger alerts
        when thresholds are exceeded.
        """
        for rule in self.rules:
            for record in self.storage.history:
                if record.value is not None and record.value is not False:
                    if record.metric == rule.metric and record.value > rule.threshold:
                        rootLogger.warning(f"[ALERT] {record.device_ip} exceeded {rule.metric}: {record.value:.2f}")
        self.storage.clear_history()

# Main Collector
class NetworkMonitorCore:
    """
    Central controller coordinating discovery, collectors,
    storage, and alert processing.
    """
    def __init__(self, ip_addr: str):
        rootLogger.info(f"Initializing network monitor for {ip_addr}")
        
        self.subnet_enumerator = SubnetEnumerator()
        self.storage = StorageEngine()

        self.devices = self.subnet_enumerator.scan_subnet(ip_addr)

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
                collector.run(self.devices, local_ip, self.storage.store)
                self.alert_engine.evaluate()
            time.sleep(5)


if __name__ == "__main__":
    try:
        monitor = NetworkMonitorCore(ip_addr=local_ip)
        monitor.start()
    except KeyboardInterrupt:
        rootLogger.info("Keyboard Interrupted. Wait for shutting down.")
    except PermissionError:
        rootLogger.error("pymonitor requires sudo to scan.")
        exit(1)
    except Exception as e:
        rootLogger.error(f"Error occured: {e}")
        exit(1)