from woninet.utilities.ip_validator import is_ip_list_valid

def test_valid_ip():
    assert is_ip_list_valid(ip_list=["192.168.1.1"])

def test_invalid_ip():
    assert not is_ip_list_valid(ip_list=["192.168.1"])
