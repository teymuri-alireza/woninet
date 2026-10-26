from fastapi import APIRouter, Query, status
from fastapi.responses import JSONResponse
from woninet.server.dependencies import get_monitor_gracefully

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.get("")
def alerts(
    page: int = Query(default=1, ge=1), page_size: int = Query(default=10, ge=1, le=100)
):
    monitor = get_monitor_gracefully()

    offset = (page - 1) * page_size

    return JSONResponse(
        content={
            "recent_alert_events": monitor.classify_recent_alert_events(
                limit=page_size, offset=offset
            ),
            "page_details": {
                "page": page,
                "page_size": page_size,
                "total_pages": (monitor.count_alert_events() + page_size - 1)
                // page_size,
            },
        },
        status_code=status.HTTP_200_OK,
    )
