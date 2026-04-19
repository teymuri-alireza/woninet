from fastapi import APIRouter
from woninet.server.services.device_service import get_devices

router = APIRouter(
    prefix="/devices",
    tags=["devices"]
)

@router.get("/")
def list_devices():
    return get_devices()