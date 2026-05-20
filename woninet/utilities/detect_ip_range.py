def detect_ip_range(ip: str) -> bool:
    """
    Detect if an IP address is provided as a range.
    (e.g., 192.168.10.10-20)

    Args:
        ip (str): IP address to detect.

    Returns:
        bool: Boolean indicating if IP address is provided as a range.

    Raises:
        ValueError: If the range notation is used in any of the first three octets.\n
            (e.g., 192.168.1-10.10 - 192.168-188.1.10 - 192.180.168.1.10)
    """
    base, last_octet = ip.rsplit(".", maxsplit=1)
    if "-" in base:
        raise ValueError("Ip addess range is only allowed in the last octet.")
    if "-" in last_octet:
        return True
    return False
