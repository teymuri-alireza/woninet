from ipaddress import ip_address
from woninet.core.models import Device


def is_ip_list_valid(ip_list: list[str]) -> bool:
    """
    Validate a list of IP addresses.

    Args:
        ip_list (list[str]): IP addresses to validate.

    Returns:
        bool: Boolean indicating if IP addresses are valid.
    """
    for ip in ip_list:
        try:
            ip_address(ip)
        except ValueError:
            return False
    return True


def is_device_ip_valid(devices: dict[str, Device]) -> bool:
    """
    Validate the dictionary of candidate devices.

    Args:
        devices (dict[str,Device]): Dictrionary of IP addresses and Device model
            instances to validate.

    Returns:
        bool: Boolean indicating if IP addresses are valid.
    """
    for ip, dev in devices.items():
        try:
            ip_address(ip)
        except ValueError:
            return False
    return True
