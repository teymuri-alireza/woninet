def test_dashboard_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200


def test_devices_api_returns_mocked_devices(client):
    response = client.get("/api/devices")

    assert response.status_code == 200
    assert response.json()["devices"][0]["ip"] == "192.168.1.10"


def test_device_info_api_returns_mocked_device(client):
    response = client.get("/api/devices/192.168.100.1")

    assert response.status_code == 200
    assert response.json()["device"]["ip"] == "192.168.100.1"


def test_device_info_page_returns_mocked_device(client):
    response = client.get("/devices/192.168.100.2")

    assert response.status_code == 200


def test_device_info_page_returns_unknown_device(client):
    response = client.get("/devices/192.168.100.10")

    assert response.status_code == 404


def test_stats_api_returns_mocked_devices(client):
    response = client.get("/api/stats")

    assert response.status_code == 200
    assert response.json()["health"]["engine_alive"]
    assert response.json()["identity"]["server_ip"] == "192.168.200.100"
