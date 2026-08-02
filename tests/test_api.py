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


def test_dashboard_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200


def test_devices_api_returns_mocked_devices(client):
    response = client.get("/api/devices")

    assert response.status_code == 200
    assert response.json()["devices"][0]["ip"] == "192.168.1.10"
