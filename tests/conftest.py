import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from woninet.server.app import app
import woninet.server.routes.api.devices as devices_route
import woninet.server.routes.page.devices as device_page_route
import woninet.server.routes.api.stats as stats_route
import woninet.server.routes.api.settings as settings_route
import woninet.server.routes.api.alerts as alerts_route
from woninet.database.engine import DatabaseEngine
from woninet.database.tables import DeviceTable

_start_uptime = datetime.now()

TEST_DEVICES = [
    DeviceTable(ip="192.168.1.10", latency=32, packet_loss=0),
    DeviceTable(ip="192.168.100.1", latency=12, packet_loss=0),
    DeviceTable(ip="192.168.100.2", latency=8, packet_loss=0),
]

TEST_ALERT_EVENTS = [
    {
        "event_type": "trigger",
        "device_ip": "192.168.1.10",
        "metric": "latency",
        "value": 150.5,
        "timestamp": "2026-10-19T10:15:00",
    },
    {
        "event_type": "recover",
        "device_ip": "192.168.1.10",
        "metric": "latency",
        "value": 30.0,
        "timestamp": "2026-10-19T10:20:00",
    },
    {
        "event_type": "trigger",
        "device_ip": "192.168.100.1",
        "metric": "packet_loss",
        "value": 5.0,
        "timestamp": "2026-10-19T10:25:00",
    },
]

TEST_CONFIG = {
    "monitoring": {
        "max_workers": 16,
        "arp_noise_limit": 50,
    },
    "target_ip_list": "192.168.1.1-100,192.168.1.110",
}


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


class FakeMonitor:
    def __init__(self, devices: list[DeviceTable] = TEST_DEVICES):
        self.devices = devices
        self.local_ip = "192.168.200.100"
        self.default_gateway = "192.168.200.1"
        self.config: dict = TEST_CONFIG
        self.config_updates: list[dict] = []
        self.alert_events: list[dict] = list(TEST_ALERT_EVENTS)

    def load_config_json(self):
        return dict(self.config)

    def update_configuration(self, **kwargs):
        self.config_updates.append(kwargs)
        for k, v in kwargs.items():
            if v is not None:
                if k == "target_ip_list":
                    self.config.update({k: v})
                else:
                    self.config["monitoring"].update({k: v})

    def get_alert_events(self):
        return self.alert_events

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

    def classify_recent_alert_events(self, limit: int = 10, offset: int = 0):
        return self.alert_events

    def count_alert_events(self):
        return len(self.alert_events)


@pytest.fixture
def fake_monitor():
    return FakeMonitor()


@pytest.fixture
def client(monkeypatch, fake_monitor):
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

    monkeypatch.setattr(
        settings_route,
        "get_monitor_gracefully",
        fake_get_monitor_gracefully,
    )

    monkeypatch.setattr(
        alerts_route,
        "get_monitor_gracefully",
        fake_get_monitor_gracefully,
    )

    return TestClient(app)
