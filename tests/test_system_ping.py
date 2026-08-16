import re


def _parse_ping_output(output: str, os_name: str):
    if os_name != "Windows":
        avg_rtt_regex = r"rtt min/avg/max/mdev = [\d\.]+/([\d\.]+)/[\d\.]+/[\d\.]+ ms"

        packet_loss_regex = r"([\d\.]+)% packet loss"

        per_ping_time_regex = r"time[=<]([\d\.]+) ?ms"
    else:
        avg_rtt_regex = r"Average = ([\d\.]+)ms"

        packet_loss_regex = r"\(([^\)]+)% loss\)"

        per_ping_time_regex = r"time[=<]([\d\.]+)ms"

    avg_rtt = 0
    packet_loss = 0.0
    per_ping_times = []
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

        m = re.search(per_ping_time_regex, line)
        if m:
            try:
                per_ping_times.append(float(m.group(1)))
            except ValueError:
                pass

    jitter = 0.0
    if len(per_ping_times) >= 2:
        diffs = [abs(per_ping_times[i] - per_ping_times[i - 1]) for i in range(1, len(per_ping_times))]
        jitter = round(sum(diffs) / len(diffs), 3)

    return avg_rtt, packet_loss, jitter


def test_successful_parse_output_on_linux():
    sample_output = """
    PING 192.168.1.1 (192.168.1.1) 56(84) bytes of data.
    64 bytes from 192.168.1.1: icmp_seq=1 ttl=64 time=2.67 ms
    64 bytes from 192.168.1.1: icmp_seq=2 ttl=64 time=6.38 ms

    --- 192.168.1.1 ping statistics ---
    2 packets transmitted, 2 received, 0% packet loss, time 1002ms
    rtt min/avg/max/mdev = 2.672/4.524/6.376/1.852 ms
    """

    avg_rtt, packet_loss, jitter = _parse_ping_output(sample_output, "Linux")

    assert avg_rtt == 4.524
    assert packet_loss == 0.0
    assert jitter == 3.71


def test_failed_parse_output_on_linux():
    sample_output = """
    PING 192.168.1.2 (192.168.1.2) 56(84) bytes of data.

    --- 192.168.1.2 ping statistics ---
    2 packets transmitted, 0 received, 100% packet loss, time 1044ms
    """

    avg_rtt, packet_loss, jitter = _parse_ping_output(sample_output, "Linux")

    assert avg_rtt == 0.0
    assert packet_loss == 100.0
    assert jitter == 0.0


def test_successful_parse_output_on_windows():
    sample_output = """
    Pinging 192.168.1.1 with 32 bytes of data:
    Reply from 192.168.1.1: bytes=32 time=6ms TTL=64
    Reply from 192.168.1.1: bytes=32 time=2ms TTL=64

    Ping statistics for 192.168.1.1:
        Packets: Sent = 2, Received = 2, Lost = 0 (0% loss),
    Approximate round trip times in milli-seconds:
        Minimum = 2ms, Maximum = 6ms, Average = 4ms
    """

    avg_rtt, packet_loss, jitter = _parse_ping_output(sample_output, "Windows")

    assert avg_rtt == 4.0
    assert packet_loss == 0.0
    assert jitter == 4.0


def test_failed_parse_output_on_windows():
    sample_output = """
    Pinging 192.168.1.2 with 32 bytes of data:
    Request timed out.
    Request timed out.

    Ping statistics for 192.168.1.2:
    Packets: Sent = 2, Received = 0, Lost = 2 (100% loss),
    """

    avg_rtt, packet_loss, jitter = _parse_ping_output(sample_output, "Windows")

    assert avg_rtt == 0.0
    assert packet_loss == 100.0
    assert jitter == 0.0
