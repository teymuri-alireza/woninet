from fastapi import APIRouter, Request, Path, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from woninet.server.dependencies import get_static_path, get_monitor_gracefully

TEMPLATES_DIR, STATIC_DIR = get_static_path()
templates = Jinja2Templates(directory=TEMPLATES_DIR)

router = APIRouter(prefix="/devices", tags=["devices"])


@router.get("/")
def list_devices():
    monitor = get_monitor_gracefully()
    return {"devices": monitor.get_device_history()}


@router.get("/{ip}", response_class=HTMLResponse)
def device_info(
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
    exists = monitor.device_exists(ip=ip)
    if not exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    return templates.TemplateResponse(request=request, name="device_info.html")


@router.get("/{ip}/api")
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
    device, device_alert_state, device_recent_alert_events = monitor.get_device_info(
        ip=ip
    )
    return {
        "device": device,
        "device_alert_state": device_alert_state,
        "device_recent_alert_events": device_recent_alert_events,
        }
