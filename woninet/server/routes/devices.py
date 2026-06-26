from fastapi import APIRouter, Request, Path
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from woninet.server.services.device_service import get_devices
from woninet.server.dependencies import get_static_path

TEMPLATES_DIR, STATIC_DIR = get_static_path()
templates = Jinja2Templates(directory=TEMPLATES_DIR)

router = APIRouter(prefix="/devices", tags=["devices"])


@router.get("/")
def list_devices():
    return get_devices()


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
    device, device_alert_state, device_recent_alert_events = monitor.get_device_info(
        ip=ip
    )
    return templates.TemplateResponse(
        request=request,
        name="device_info.html",
        context={
            "request": request,
            "device": device,
            "device_alert_state": device_alert_state,
            "device_recent_alert_events": device_recent_alert_events,
        }
    )
