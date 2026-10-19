from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from woninet.server.dependencies import get_monitor_gracefully

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.get("")
def alerts():
    from woninet.__init__ import __version__

    monitor = get_monitor_gracefully()

    return JSONResponse(
        content={
            "recent_alert_events": monitor.classify_recent_alert_events(),
        },
        status_code=status.HTTP_200_OK,
    )
