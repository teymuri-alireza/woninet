from woninet.core.models import Device


class ManualIPEnumerator:
    """
    Build a dictionary of candidate devices for user-provided IP addresses.
    """

    def enumerate(self, ip_list: list[str]) -> dict[str, str]:
        devices = {}
        for ip in ip_list:
            devices[ip] = Device(ip=ip)
        return devices

    def enumerate_range(self, ip_range: str) -> dict[str, Device]:
        """
        Build a dictionary of candidate devices for user-provided IP addresses range.

        Args:
            ip_range (str): IP address as a range (e.g. 192.168.1.10-50).

        Raises:
            ValueError: If the range notation is not in the last octet.
        """
        base, last_octect = ip_range.rsplit(".", maxsplit=1)
        if "-" in base:
            raise ValueError("Range enumeraton is only supported on the last octet.")
        start, stop = last_octect.split("-")
        devices = {}
        for i in range(int(start), int(stop) + 1):
            ip = f"{base}.{i}"
            devices[ip] = Device(ip=ip)
        return devices
