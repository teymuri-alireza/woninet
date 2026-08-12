import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from woninet.server.app import app
import woninet.server.routes.api.devices as devices_route
import woninet.server.routes.page.devices as device_page_route
import woninet.server.routes.api.stats as stats_route
from woninet.database.engine import DatabaseEngine
from woninet.database.tables import DeviceTable

_start_uptime = datetime.now()

TEST_DEVICES = [
    DeviceTable(ip="192.168.1.10", latency=32, packet_loss=0),
    DeviceTable(ip="192.168.100.1", latency=12, packet_loss=0),
    DeviceTable(ip="192.168.100.2", latency=8, packet_loss=0),
]


@pytest.fixture
def db_session():
    db_engine = DatabaseEngine(database_path=":memory:")
    db_engine.init_db()

    session_factory = db_engine.get_session_factory()
    session = session_factory()

    try:
        yield session
    finally:
        session.close()


class FakeGraphEngine:
    def design_device_latency_events(self, ip, recent_device_alert_events):
        pass


class FakeMonitor:
    def __init__(self, devices: list[DeviceTable] = TEST_DEVICES):
        self.devices = devices
        self.graph_engine = FakeGraphEngine()
        self.local_ip = "192.168.200.100"

    def get_device_history(self):
        return self.devices

    def device_exists(self, ip: str) -> bool:
        ip_list = [d.ip for d in self.devices]
        return ip in ip_list

    def get_device_info(self, ip: str):
        device = next((d for d in self.devices if d.ip == ip), None)
        return (
            device,
            {"latency": "ok", "packet_loss": "ok"},
            [],
        )

    def count_resources(self):
        return (len(self.devices), 0)

    def is_alive(self):
        return True

    def database_health(self):
        return {"connection": "ok", "schema": "ok"}

    def uptime(self):
        global _start_uptime
        return (datetime.now() - _start_uptime).seconds

    def classify_recent_alert_events(self):
        return {}


@pytest.fixture
def client(monkeypatch):
    fake_monitor = FakeMonitor()

    def fake_get_monitor_gracefully():
        return fake_monitor

    monkeypatch.setattr(
        devices_route,
        "get_monitor_gracefully",
        fake_get_monitor_gracefully,
    )

    monkeypatch.setattr(
        device_page_route,
        "get_monitor_gracefully",
        fake_get_monitor_gracefully,
    )

    monkeypatch.setattr(
        stats_route,
        "get_monitor_gracefully",
        fake_get_monitor_gracefully,
    )

    return TestClient(app)
