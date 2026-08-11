from fastapi import APIRouter, Request, Path, status, HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from woninet.server.dependencies import get_monitor_gracefully

router = APIRouter(prefix="/api/devices", tags=["devices"])


@router.get("")
def list_devices(request: Request):
    monitor = get_monitor_gracefully()
    return JSONResponse(
        content={"devices": jsonable_encoder(monitor.get_device_history())},
        status_code=status.HTTP_200_OK,
    )


@router.get("/{ip}")
def device_info_api(
    request: Request,
    ip: str = Path(
        ...,
        title="IP address",
        description="IP address of the device.",
        min_length=7,
        max_length=15,
    ),
):

    monitor = get_monitor_gracefully()

    if not monitor.device_exists(ip=ip):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    device, device_alert_state, device_recent_alert_events = monitor.get_device_info(
        ip=ip
    )
    monitor.graph_engine.design_device_latency_events(
        ip=ip, recent_device_alert_events=device_recent_alert_events
    )
    return JSONResponse(
        content={
            "device": jsonable_encoder(device),
            "device_alert_state": jsonable_encoder(device_alert_state),
            "device_recent_alert_events": jsonable_encoder(device_recent_alert_events),
        },
        status_code=status.HTTP_200_OK,
    )
