def test_dashboard_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200


def test_devices_api_returns_mocked_devices(client):
    response = client.get("/api/devices")

    assert response.status_code == 200
    assert response.json()["devices"][0]["ip"] == "192.168.1.10"


def test_device_availability_api_returns_mocked_availability(client, fake_monitor):
    response = client.get("/api/devices/192.168.100.1/availability")

    assert response.status_code == 200
    assert response.json() == {
        "ip": "192.168.100.1",
        "granularity": "day",
        "buckets": [],
        "summary": {"uptime": None, "checks": 0},
    }
    assert fake_monitor.availability_calls == [("192.168.100.1", 90, "day")]


def test_device_info_page_serves_availability_dashboard(client):
    response = client.get("/devices/192.168.100.2")

    assert response.status_code == 200
    assert "Availability history and live metrics" in response.text
    assert 'id="heatmap"' in response.text


def test_device_info_page_rejects_unknown_device(client):
    response = client.get("/devices/192.168.100.10")

    assert response.status_code == 404


def test_stats_api_returns_mocked_devices(client):
    response = client.get("/api/stats")

    assert response.status_code == 200
    assert response.json()["health"]["engine_alive"]
    assert response.json()["identity"]["server_ip"] == "192.168.200.100"


def test_settings_page_endpoint(client):
    response = client.get("/settings")

    assert response.status_code == 200


def test_settings_api_returns_initial_configuration(client):
    response = client.get("/api/settings")

    assert response.status_code == 200

    settings = response.json()["settings"]
    assert settings["max_workers"] == 16
    assert settings["arp_noise_limit"] == 50
    assert settings["target_ip_list"] == "192.168.1.1-100,192.168.1.110"


def test_update_settings_api_passes_values_to_monitor(client, fake_monitor):
    response = client.post(
        "/api/settings",
        data={
            "max_workers": "8",
            "arp_noise_limit": "100",
            "target_ip_list": "192.168.1.1-50,192.168.1.60",
        },
    )

    assert response.status_code == 201
    assert response.json() == {"success": True}

    updates = {k: v for call in fake_monitor.config_updates for k, v in call.items()}
    assert updates["max_workers"] == "8"
    assert updates["arp_noise_limit"] == "100"
    assert updates["target_ip_list"] == ["192.168.1.1-50", "192.168.1.60"]


def test_update_settings_api_accepts_partial_form(client, fake_monitor):
    response = client.post("/api/settings", data={"max_workers": "4"})

    updates = {k: v for call in fake_monitor.config_updates for k, v in call.items()}
    assert response.status_code == 201
    assert response.json()["success"] is True
    assert updates["max_workers"] == "4"


def test_update_settings_api_is_reflected_on_next_get(client):
    client.post("/api/settings", data={"max_workers": "32", "arp_noise_limit": "75"})

    settings = client.get("/api/settings").json()["settings"]

    assert str(settings["max_workers"]) == "32"
    assert str(settings["arp_noise_limit"]) == "75"


def _alert_events(response):
    data = response.json()

    if isinstance(data, list):
        return data

    for key in ("alerts", "events", "recent_alert_events"):
        if key in data:
            return data[key]

    raise AssertionError(f"No alert events found in response: {data}")


def test_alerts_page_endpoint(client):
    response = client.get("/alerts")

    assert response.status_code == 200


def test_alerts_api_returns_mocked_events(client):
    response = client.get("/api/alerts")

    assert response.status_code == 200

    events = _alert_events(response)
    assert len(events) == 3
    assert {e["device_ip"] for e in events} == {"192.168.1.10", "192.168.100.1"}


def test_alerts_api_events_have_expected_fields(client):
    events = _alert_events(client.get("/api/alerts"))

    for event in events:
        assert event["event_type"] in {"trigger", "recover"}
        assert {"device_ip", "metric", "value", "timestamp"} <= event.keys()


def test_alerts_api_returns_both_event_types(client):
    events = _alert_events(client.get("/api/alerts"))

    assert {e["event_type"] for e in events} == {"trigger", "recover"}


def test_alerts_api_returns_empty_list_when_no_events(client, fake_monitor):
    fake_monitor.alert_events = []

    response = client.get("/api/alerts")

    assert response.status_code == 200
    assert _alert_events(response) == []
