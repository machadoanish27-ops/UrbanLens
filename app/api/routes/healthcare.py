"""Healthcare discovery endpoints."""

from fastapi import APIRouter, Depends, Query, Request
from pymongo.database import Database

from app.core.config import settings
from app.core.rate_limit import limiter
from app.db.client import get_db
from app.schemas.common import ApiResponse, ResponseMeta
from app.schemas.healthcare import CityHealthcareResponse
from app.services.healthcare import HealthcareService

router = APIRouter(prefix="/cities", tags=["Healthcare Discovery"])


@router.get(
    "/{city_id}/healthcare",
    response_model=ApiResponse[CityHealthcareResponse],
    summary="Discover healthcare facilities in and around a city",
)
@limiter.limit(settings.RATE_LIMIT_LIVE_PROVIDERS)
async def get_city_healthcare(
    request: Request,
    city_id: str,
    category: str | None = Query(None, description="Filter category: hospital, clinic, dentist, pharmacy"),
    radius: int = Query(5000, ge=500, le=25000, description="Search radius in meters"),
    limit: int = Query(30, ge=1, le=50, description="Maximum locations to return"),
    database: Database = Depends(get_db),
) -> ApiResponse[CityHealthcareResponse]:
    """Retrieve verified and community-mapped healthcare facilities near city coordinates."""
    service = HealthcareService(database)
    data = await service.get_city_healthcare(
        city_id=city_id,
        category=category,
        radius=radius,
        limit=limit,
    )
    return ApiResponse(
        data=data,
        meta=ResponseMeta(source="OpenStreetMap Healthcare Facilities"),
    )
