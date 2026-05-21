import logging
from woninet.core.models import Device

core_logger = logging.getLogger("core")


class SubnetEnumerator:
    """
    Build a dictionary of candidate devices for a given IPv4 /24 subnet.
    """

    def enumerate(self, ip: str) -> dict[str, Device]:
        """
        Build a dictionary of candidate devices based on the /24 subnet
        of the provided IPv4 address.

        Args:
            ip (str): IPv4 address used to derive the subnet.

        Returns:
            dict[str,Device]: Dictionary of candidate devices containing host
                IP addresses and the related `Device` instances. Hosts range
                from `.1` to `.254`.
        """
        ip_split = ip.split(".")
        subnet = f"{ip_split[0]}.{ip_split[1]}.{ip_split[2]}"
        core_logger.debug(f"Building a dictionaty of IP addresses base on {subnet}.x")
        devices = {}
        for i in range(1, 255):
            ip = f"{subnet}.{i}"
            devices[ip] = Device(ip)
        return devices
