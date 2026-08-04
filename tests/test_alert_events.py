from woninet.core.storage import StorageEngine
from woninet.core.models import MetricRecord
from woninet.core.alerts import AlertRule, AlertEngine


def test_latency_trigger_alert_event(db_session):
    storage = StorageEngine(session_factory=lambda: db_session)

    metric = MetricRecord(device_ip="192.168.1.10", metric="latency", value=200)
    storage.store_metric(metric)

    alert_rule = {"metric": "latency", "threshold": 100, "consecutive_checks": 0}

    alert = AlertEngine(
        storage=storage,
        rules=[
            AlertRule(
                alert_rule["metric"],
                alert_rule["threshold"],
                alert_rule["consecutive_checks"],
            )
        ],
    )

    alert.evaluate(
        ip="192.168.1.10",
        metrics_list=[
            MetricRecord(device_ip="192.168.1.10", metric="latency", value=200),
        ],
        default_consecutive_checks={
            "latency": 0,
        },
    )

    latency = storage.get_recent_alert_events()[0]

    assert latency.event_type == "trigger"


def test_packet_loss_trigger_alert_event(db_session):
    storage = StorageEngine(session_factory=lambda: db_session)

    metric = MetricRecord(device_ip="192.168.1.10", metric="packet_loss", value=0.5)
    storage.store_metric(metric)

    alert_rule = {"metric": "packet_loss", "threshold": 0.0, "consecutive_checks": 0}

    alert = AlertEngine(
        storage=storage,
        rules=[
            AlertRule(
                alert_rule["metric"],
                alert_rule["threshold"],
                alert_rule["consecutive_checks"],
            )
        ],
    )

    alert.evaluate(
        ip="192.168.1.10",
        metrics_list=[
            MetricRecord(device_ip="192.168.1.10", metric="packet_loss", value=0.5),
        ],
        default_consecutive_checks={
            "packet_loss": 0,
        },
    )

    packet_loss = storage.get_recent_alert_events()[0]

    assert packet_loss.event_type == "trigger"


def test_latency_recover_alert_event(db_session):
    storage = StorageEngine(session_factory=lambda: db_session)

    metric = MetricRecord(device_ip="192.168.1.10", metric="latency", value=20)
    storage.store_metric(metric)

    state = storage.get_or_create_alert_state(
        ip="192.168.1.10", metric="latency", consecutive_checks=0
    )
    state.state = "warning"
    storage.update_alert_state(state)

    alert_rule = {"metric": "latency", "threshold": 100, "consecutive_checks": 0}

    alert = AlertEngine(
        storage=storage,
        rules=[
            AlertRule(
                alert_rule["metric"],
                alert_rule["threshold"],
                alert_rule["consecutive_checks"],
            )
        ],
    )

    alert.evaluate(
        ip="192.168.1.10",
        metrics_list=[
            MetricRecord(device_ip="192.168.1.10", metric="latency", value=20),
        ],
        default_consecutive_checks={
            "latency": 0,
        },
    )

    latency = storage.get_recent_alert_events()[0]

    assert latency.event_type == "recover"


def test_packet_loss_recover_alert_event(db_session):
    storage = StorageEngine(session_factory=lambda: db_session)

    metric = MetricRecord(device_ip="192.168.1.10", metric="packet_loss", value=0.0)
    storage.store_metric(metric)

    state = storage.get_or_create_alert_state(
        ip="192.168.1.10", metric="packet_loss", consecutive_checks=0
    )
    state.state = "warning"
    storage.update_alert_state(state)

    alert_rule = {"metric": "packet_loss", "threshold": 0.0, "consecutive_checks": 0}

    alert = AlertEngine(
        storage=storage,
        rules=[
            AlertRule(
                alert_rule["metric"],
                alert_rule["threshold"],
                alert_rule["consecutive_checks"],
            )
        ],
    )

    alert.evaluate(
        ip="192.168.1.10",
        metrics_list=[
            MetricRecord(device_ip="192.168.1.10", metric="packet_loss", value=0.0),
        ],
        default_consecutive_checks={
            "packet_loss": 0,
        },
    )

    packet_loss = storage.get_recent_alert_events()[0]

    assert packet_loss.event_type == "recover"
