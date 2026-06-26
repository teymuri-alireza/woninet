from typing import Any
from fastapi import APIRouter
from woninet.server.dependencies import get_monitor_gracefully

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/")
def stats():
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
