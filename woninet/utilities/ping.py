import re
import shutil
import platform
import subprocess
from woninet.core.models import PingResult
from woninet.exc import PingUtilityNotFound


def system_ping(address: str, timeout: float, count: int, interval: int) -> PingResult:
    """
    Ping an address using the system ping command and parse results.

    Args:
        address: The target hostname or IP address to ping.
        timeout: Per-ping timeout in seconds.
        count: Number of ICMP echo requests to send.
        interval: Interval between sending each ping in seconds
            (Only available on Unix systems. Ignored on Windows).

    Returns:
        PingResult: PingResult instance with average round-trip time and packet loss percentage.

    Raises:
        PingUtilityNotFound: if the ping command is not found on PATH.
    """
    if shutil.which("ping") is None:
        raise PingUtilityNotFound

    try:
        # fmt: off
        if platform.system() != "Windows":
            command = ["ping", "-c", str(count), "-W", str(timeout), "-i", str(interval), address]
        else:
            command = ["ping", "-n", str(count), "-w", str(timeout), address]
        # fmt: on

        output = subprocess.check_output(command, stderr=subprocess.DEVNULL, text=True)

        if platform.system() != "Windows":
            # Example rtt line: rtt min/avg/max/mdev = 5.377/5.729/6.082/0.352 ms
            avg_rtt_regex = (
                r"rtt min/avg/max/mdev = [\d\.]+/([\d\.]+)/[\d\.]+/[\d\.]+ ms"
            )

            # Example packet loss line: 2 packets transmitted, 2 received, 0% packet loss, time 1002ms
            packet_loss_regex = r"([\d\.]+)% packet loss"
        else:
            # Example rtt line: Minimum = 2ms, Maximum = 5ms, Average = 3ms
            avg_rtt_regex = r"Average = ([\d\.]+)ms"

            # Example packet loss line: Packets: Sent = 2, Received = 2, Lost = 0 (0% loss),
            packet_loss_regex = r"\(([^\)]+)% loss\)"

        avg_rtt = 0
        packet_loss = 0.0
        for line in output.splitlines():
            m = re.search(avg_rtt_regex, line)
            if m:
                try:
                    avg_rtt = float(m.group(1))
                except ValueError:
                    avg_rtt = 0
                continue

            m = re.search(packet_loss_regex, line)
            if m:
                try:
                    packet_loss = float(m.group(1))
                except ValueError:
                    packet_loss = 0.0

        return PingResult(avg_rtt, packet_loss)

    except Exception:
        return PingResult(0, 0.0)
