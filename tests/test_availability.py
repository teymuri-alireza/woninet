from datetime import datetime
from woninet.core.engine import NetworkMonitorCore

HOUR = datetime(2026, 10, 28, 14, 0)


def record(checks, when, fake_monitor):
    NetworkMonitorCore.record_availability(fake_monitor, checks, when)
    return fake_monitor.storage.calls


def test_monitor_rounds_the_cycle_to_its_hour(fake_monitor):
    calls = record(
        [("192.168.1.10", True), ("192.168.1.11", False)],
        datetime(2026, 10, 28, 14, 37, 12),
        fake_monitor,
    )
    assert calls == [([("192.168.1.10", True), ("192.168.1.11", False)], HOUR)]


def test_monitor_skips_a_cycle_where_nothing_responded(fake_monitor):
    assert (
        record(
            [("192.168.1.10", False), ("192.168.1.11", False)],
            datetime(2026, 10, 28, 14, 37, 12),
            fake_monitor,
        )
        == []
    )


def test_monitor_records_a_single_device_that_is_down(fake_monitor):
    assert (
        len(
            record(
                [("192.168.1.10", False)],
                datetime(2026, 10, 28, 14, 37, 12),
                fake_monitor,
            )
        )
        == 1
    )


def test_monitor_passes_an_empty_cycle_to_storage(fake_monitor):
    assert record([], datetime(2026, 10, 28, 14, 37, 12), fake_monitor) == [([], HOUR)]
