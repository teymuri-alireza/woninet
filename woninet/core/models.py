from datetime import datetime
from typing import Optional


class Device:
    """
    Represent a discovered network device.
    Store identity information and device state.
    """

    def __init__(self, ip: str) -> None:
        """
        Initialze the device model.

        Args:
            ip: IP address of the host
        """
        self.ip: str = ip
        self.last_seen: Optional[datetime] = None
        self.exists: bool = False  # True if ARP has seen this IP
        self.reachable: bool = (
            False  # True if ICMP is sane and within latency threshold
        )
        self.mac: Optional[str] = None  # MAC address from ARP table
        self.latency: float = 0

    def update_seen(self) -> None:
        """
        Update timestamp indicating the device responded recently.
        """
        self.last_seen = datetime.now()


class MetricRecord:
    """
    Represent a single collected metric measurement
    for a specific device at a specific time.
    """

    def __init__(
        self, device_ip: str, metric: str, value: float, timestamp=None
    ) -> None:
        """
        Initialize the metric record model.
        """
        self.device_ip = device_ip
        self.metric = metric
        self.value = value
        self.timestamp = timestamp or datetime.now()


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
    ) -> None:
        """
        Initialize the host status model.
        """
        self.ip: str = ip
        self.exists: bool = exists
        self.reachable: bool = reachable
        self.latency: Optional[float] = latency
        self.mac: Optional[str] = mac
