from fastapi import APIRouter
from woninet.server.services.stats_service import get_network_stats

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/")
def stats():
    return get_network_stats()
