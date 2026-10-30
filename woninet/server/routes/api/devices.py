from typing import Literal
from ipaddress import IPv4Address
from fastapi import APIRouter, HTTPException, Path, Query, Request, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from woninet.server.dependencies import get_monitor_gracefully

router = APIRouter(prefix="/api/devices", tags=["devices"])


@router.get("")
def list_devices(request: Request):
    monitor = get_monitor_gracefully()
    return JSONResponse(
        content={
            "devices": jsonable_encoder(monitor.get_device_history()),
            "gateway": monitor.default_gateway,
        },
        status_code=status.HTTP_200_OK,
    )


@router.get("/{ip}/availability")
def device_availability(
    ip: IPv4Address = Path(
        ..., title="IP address", description="IPv4 address of the device."
    ),
    days: int = Query(default=90, ge=1, le=365),
    granularity: Literal["day", "hour"] = Query(default="day"),
):
    if granularity == "hour" and days > 7:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Hourly granularity supports at most 7 days.",
        )

    monitor = get_monitor_gracefully()
    ip = str(ip)

    if not monitor.device_exists(ip=ip):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    return JSONResponse(
        content=monitor.get_availability(ip=ip, days=days, granularity=granularity),
        status_code=status.HTTP_200_OK,
    )
