from fastapi import APIRouter, status, Request, Form
from fastapi.responses import JSONResponse
from woninet.server.dependencies import get_monitor_gracefully

router = APIRouter(prefix="/api/settings", tags=["settings"])


@router.get("")
def settings():
    monitor = get_monitor_gracefully()
    data = monitor.load_config_json()

    return JSONResponse(
        content={
            "settings": {
                "arp_noise_limit": data["monitoring"]["arp_noise_limit"],
                "max_workers": data["monitoring"]["max_workers"],
                "target_ip_list": data["target_ip_list"],
            }
        },
        status_code=status.HTTP_200_OK,
    )


@router.post("")
def update_settings(
    request: Request,
    max_workers=Form(None),
    arp_noise_limit=Form(None),
    target_ip_list=Form(None),
):
    monitor = get_monitor_gracefully()

    monitor.update_configuration(
        max_workers=max_workers,
        arp_noise_limit=arp_noise_limit,
        target_ip_list=target_ip_list,
    )

    return JSONResponse(
        content={
            "success": True,
        },
        status_code=status.HTTP_201_CREATED,
    )
