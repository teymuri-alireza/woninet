from woninet.core.storage import StorageEngine
from woninet.core.models import Device, MetricRecord


def test_storage_engine_persists_device(db_session):
    storage = StorageEngine(session_factory=lambda: db_session)
    device = Device(ip="192.168.1.10")

    storage.store_device(device)
    result = storage.fetch_device_info("192.168.1.10")

    assert result is not None
    assert result.ip == "192.168.1.10"


def test_storage_engine_persists_metric(db_session):
    storage = StorageEngine(session_factory=lambda: db_session)
    metric = MetricRecord(device_ip="192.168.1.10", metric="latency", value="20")

    storage.store_metric(metric)
    result = storage.list_metric_history()

    assert result is not None
    assert result[0].device_ip == "192.168.1.10"
