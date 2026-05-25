from datetime import datetime


class Device:
    """
    Represents a discovered network device and stores identity information
    and device state.

    Attributes:
        ip (str): IP address of the host.
        last_seen (datetime|None): Last time device responded to ICMP request; Otherwise `None`.
        exists (bool): If device responded to the last ARP scan.
        reachable (bool): If device responded to the last ICMP scan.
        mac (str): MAC address if known; Otherwise `None`.
        latency (float): The last latency of host if reachable; Otherwise zero.
        packet_loss (float): Most recent packet-loss ratio in the range [0.0, 1.0].
            A value of 1.0 indicates 100% packet loss or that the device is unreachable.
    """

    def __init__(self, ip: str) -> None:
        """
        Initialize the device model.

        Args:
            ip: IP address of the host
        """
        self.ip: str = ip
        self.last_seen: datetime | None = None
        self.exists: bool = False
        self.reachable: bool = False
        self.mac: str | None = None
        self.latency: float = 0
        self.packet_loss: float = 1

    def update_seen(self) -> None:
        """
        Update timestamp indicating the device responded recently.
        """
        self.last_seen = datetime.now()


class MetricRecord:
    """
    Represents a single collected metric measurement
    for a specific device at a specific time.

    Attributes:
        device_ip (str): IP address of the host.
        metric (str): Name of the metric.
        value (float): Recorded value of the metric.
        timestamp (datetime|None): Timestamp when the metric was captured.
            If `None`, defaults to the current time.
    """

    def __init__(
        self,
        device_ip: str,
        metric: str,
        value: float,
        timestamp: datetime | None = None,
    ) -> None:
        """
        Initialize a metric record.

        Args:
            device_ip (str): IP address of the host the metric belongs to.
            metric (str): Name of the recorded metric.
            value (float): Recorded value of the metric.
            timestamp (datetime|None): Timestamp of the measurement.
                If omitted, the current time is used.
        """
        self.device_ip = device_ip
        self.metric = metric
        self.value = value
        self.timestamp = timestamp or datetime.now()


class HostStatus:
    """
    Represents a Combined ARP + ICMP status for a given IP.

    Attributes:
        ip (str): IP address of the host.
        exists (bool): If device responded to the ARP scan
        reachable (bool): If device responded to the ICMP scan
        latency (float): The latency of host if reachable; Otherwise zero.
        packet_loss (float): Most recent packet-loss ratio in the range [0.0, 1.0].
            A value of 1.0 indicates 100% packet loss or that the device is unreachable.
        mac (str): MAC address if known; Otherwise `None`.
    """

    def __init__(
        self,
        ip: str,
        exists: bool = False,
        reachable: bool = False,
        latency: float = 0.0,
        mac: str | None = None,
    ) -> None:
        """
        Initialize the host status model.

        Args:
            ip (str): IP address of the host.
            exists (bool): If device responded to the ARP scan
            reachable (bool): If device responded to the ICMP scan
            latency (float): The latency of host if reachable; Otherwise zero.
            mac (str): MAC address if known; Otherwise `None`.
        """
        self.ip: str = ip
        self.exists: bool = exists
        self.reachable: bool = reachable
        self.latency: float = latency
        self.packet_loss: float = 1
        self.mac: str | None = mac
