from typing import Dict
from woninet.core.models import Device
from woninet.utilities.logger import logger_function

rootLogger = logger_function()


class SubnetEnumerator:
    """
    Build a dictionary of candidate devices within the local /24 subnet.
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
