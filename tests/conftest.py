import pytest
from fastapi.testclient import TestClient
from woninet.server.app import app
import woninet.server.routes.api.devices as devices_route
from woninet.database.engine import DatabaseEngine


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
