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
