import pytest
import woninet.core.collectors as collectors

LINUX_ARP = (
    "? (192.168.10.1) at aa:aa:aa:aa:aa:01 [ether] on eth0\n"
    "? (192.168.10.7) at <incomplete> on eth0\n"
    "? (192.168.10.5) at bb:bb:bb:bb:bb:05 [ether] on eth0\n"
)


@pytest.fixture
def linux_arp(monkeypatch):
    monkeypatch.setattr(collectors.platform, "system", lambda: "Linux")
    monkeypatch.setattr(
        collectors.subprocess, "check_output", lambda *a, **k: LINUX_ARP
    )


def test_returns_mac_of_requested_ip(linux_arp):
    assert collectors.get_arp_mac("192.168.10.5") == "bb:bb:bb:bb:bb:05"


def test_unknown_ip_returns_none_not_first_entry(linux_arp):
    assert collectors.get_arp_mac("192.168.10.20") is None


def test_incomplete_entry_returns_none(linux_arp):
    assert collectors.get_arp_mac("192.168.10.7") is None


def test_missing_arp_command_returns_none(monkeypatch):
    def boom(*a, **k):
        raise FileNotFoundError("arp")

    monkeypatch.setattr(collectors.subprocess, "check_output", boom)
    assert collectors.get_arp_mac("192.168.10.1") is None
