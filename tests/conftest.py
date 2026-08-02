import pytest
from fastapi.testclient import TestClient
from woninet.server.app import app
import woninet.server.routes.api.devices as devices_route


class FakeMonitor:

    def get_device_history(self):
        return [{"ip": "192.168.1.10", "hostname": "test-host"}]


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

    return TestClient(app)
