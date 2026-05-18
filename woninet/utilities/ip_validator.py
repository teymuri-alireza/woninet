from ipaddress import ip_address


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
