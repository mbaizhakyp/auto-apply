from fastapi import APIRouter
from src.analytics.logger import get_stats

router = APIRouter()

@router.get("/")
async def get_analytics_stats():
    stats = get_stats()
    return stats
