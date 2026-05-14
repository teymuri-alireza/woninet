from typing import Any


def get_monitor_gracefully():
    """
    Call get_monitor() and return the intance of NetworkMonitorCore class
    to prevent circular import error.
    """
    from woninet.main import get_monitor

    monitor = get_monitor()
    return monitor


def get_network_stats() -> dict[str, Any]:
    from woninet.__init__ import __version__

    monitor = get_monitor_gracefully()
    devices_total, metrics_total = monitor.count_resources()

    network_stats = {
        "identity": {
            "service": "woninet",
            "version": __version__,
            "server_ip": monitor.local_ip,
        },
        "health": {
            "engine_alive": monitor.is_alive(),
            "database": monitor.database_health(),
        },
        "stats": {
            "devices_total": devices_total,
            "metrics_total": metrics_total,
            "uptime_seconds": monitor.uptime(),
        },
        "recent_alert_events": monitor.classify_recent_alert_events(),
    }
    return network_stats
