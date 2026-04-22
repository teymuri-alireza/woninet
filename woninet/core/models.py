from datetime import datetime
from typing import Dict, Optional


class Device:
    """
    Represents a discovered network device.
    Stores identity information and the latest known metrics and state.
    """

    def __init__(self, ip: str):
        self.ip: str = ip
        self.last_seen: Optional[datetime] = None
        self.metrics: Dict[str, float] = {}  # Bandwidth, CPU, etc

        self.exists: bool = False  # True if ARP has seen this IP
        self.reachable: bool = (
            False  # True if ICMP is sane and within latency threshold
        )
        self.mac: Optional[str] = None  # MAC address from ARP table
        self.latency: Optional[float] = 0

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

        # Formatting datetime
        datetime_now = datetime.now()
        year = datetime_now.year
        month = datetime_now.month
        day = datetime_now.day
        hour = datetime_now.hour
        minute = datetime_now.minute
        second = datetime_now.second

        self.timestamp = timestamp or f"{year}/{month}/{day} {hour}:{minute}:{second}"


class HostStatus:
    """
    Combined ARP + ICMP status for a given IP
    """

    def __init__(
        self,
        ip: str,
        exists: bool = False,
        reachable: bool = False,
        latency: Optional[float] = None,
        mac: Optional[str] = None,
    ):
        self.ip = ip
        self.exists = exists
        self.reachable = reachable
        self.latency = latency  # in milliseconds
        self.mac = mac
