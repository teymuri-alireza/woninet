def test_dashboard_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200


def test_devices_api_returns_mocked_devices(client):
    response = client.get("/api/devices")

    assert response.status_code == 200
    assert response.json()["devices"][0]["ip"] == "192.168.1.10"
