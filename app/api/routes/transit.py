"""Public transport endpoints."""

from fastapi import APIRouter, Depends, Request
from pymongo.database import Database

from app.core.config import settings
from app.core.rate_limit import limiter
from app.db.client import get_db
from app.schemas.common import ApiResponse, ResponseMeta
from app.schemas.transit import TransitFeedResponse
from app.services.transit import TransitService

router = APIRouter(prefix="/transit", tags=["Transit"])


@router.get(
    "/{city_id}",
    response_model=ApiResponse[TransitFeedResponse],
    summary="Get GTFS transit feed information for a city",
)
@limiter.limit(settings.RATE_LIMIT_LIVE_PROVIDERS)
async def get_transit_info(
    request: Request,
    city_id: str,
    database: Database = Depends(get_db),
) -> ApiResponse[TransitFeedResponse]:
    """Retrieve registered GTFS / GTFS-Realtime transit feed status or explicit DATA_UNAVAILABLE."""
    service = TransitService(database)
    data = await service.get_transit_info(city_id=city_id)
    return ApiResponse(
        data=TransitFeedResponse(**data),
        meta=ResponseMeta(source="GTFS/GTFS-Realtime Feed Registry"),
    )
