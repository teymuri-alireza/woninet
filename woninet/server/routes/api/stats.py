from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from woninet.server.dependencies import get_monitor_gracefully

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("")
def stats():
    from woninet.__init__ import __version__

    monitor = get_monitor_gracefully()
    devices_total, metrics_total = monitor.count_resources()

    return JSONResponse(
        content={
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
        },
        status_code=status.HTTP_200_OK
    )
