from fastapi import APIRouter, Request, Path, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from woninet.server.dependencies import get_static_path, get_monitor_gracefully

TEMPLATES_DIR, STATIC_DIR = get_static_path()
templates = Jinja2Templates(directory=TEMPLATES_DIR)

router = APIRouter(prefix="/devices", tags=["devices"])


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

    if not monitor.device_exists(ip=ip):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    return templates.TemplateResponse(request=request, name="device_info.html")
