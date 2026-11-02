"""Healthcare discovery endpoints integrating Kaggle baseline data with verified provenance."""

from fastapi import APIRouter, Depends, Query, Request
from pymongo.database import Database

from app.core.config import settings
from app.core.rate_limit import limiter
from app.db.client import get_db
from app.schemas.common import ApiResponse, ResponseMeta
from app.schemas.healthcare import (
    CityHealthcareResponse,
    HealthcareDetailResponse,
    HealthcareNearbyResponse,
)
from app.services.healthcare import HealthcareService

router = APIRouter(prefix="/cities", tags=["Healthcare Discovery"])
nearby_router = APIRouter(prefix="/healthcare", tags=["Healthcare Discovery"])


@router.get(
    "/{city_id}/healthcare",
    response_model=ApiResponse[CityHealthcareResponse],
    summary="Discover healthcare facilities in and around a city",
)
@limiter.limit(settings.RATE_LIMIT_LIVE_PROVIDERS)
async def get_city_healthcare(
    request: Request,
    city_id: str,
    category: str | None = Query(None, description="Filter category: hospital, clinic, pharmacy, health_center, etc."),
    search: str | None = Query(None, description="Search facility name"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    radius: int = Query(25000, ge=500, le=50000, description="Search radius in meters"),
    limit: int | None = Query(None, ge=1, le=100, description="Maximum locations to return"),
    database: Database = Depends(get_db),
) -> ApiResponse[CityHealthcareResponse]:
    """Retrieve verified and community-mapped healthcare facilities for a canonical city."""
    service = HealthcareService(database)
    effective_limit = limit if limit is not None else page_size
    data = await service.get_city_healthcare(
        city_id=city_id,
        category=category,
        search=search,
        page=page,
        page_size=effective_limit,
        radius=radius,
        limit=effective_limit,
    )
    return ApiResponse(
        data=data,
        meta=ResponseMeta(source=data.source),
    )


@router.get(
    "/{city_id}/healthcare/{healthcare_id}",
    response_model=ApiResponse[HealthcareDetailResponse],
    summary="Retrieve details for a specific healthcare facility",
)
@limiter.limit(settings.RATE_LIMIT_LIVE_PROVIDERS)
async def get_healthcare_detail(
    request: Request,
    city_id: str,
    healthcare_id: str,
    database: Database = Depends(get_db),
) -> ApiResponse[HealthcareDetailResponse]:
    """Retrieve detailed metadata and verified contact data for a single healthcare facility."""
    service = HealthcareService(database)
    data = await service.get_facility_by_id(
        city_id=city_id,
        healthcare_id=healthcare_id,
    )
    return ApiResponse(
        data=data,
        meta=ResponseMeta(source=data.source),
    )


@nearby_router.get(
    "/nearby",
    response_model=ApiResponse[HealthcareNearbyResponse],
    summary="Discover nearby healthcare facilities around coordinates",
)
@limiter.limit(settings.RATE_LIMIT_LIVE_PROVIDERS)
async def get_nearby_healthcare(
    request: Request,
    lat: float = Query(..., ge=-90.0, le=90.0, description="Latitude coordinate"),
    lon: float = Query(..., ge=-180.0, le=180.0, description="Longitude coordinate"),
    radius: int = Query(10000, ge=500, le=50000, description="Radius in meters"),
    category: str | None = Query(None, description="Optional facility category filter"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Page size"),
    database: Database = Depends(get_db),
) -> ApiResponse[HealthcareNearbyResponse]:
    """Geospatially discover nearby verified healthcare facilities around GPS coordinates."""
    service = HealthcareService(database)
    data = await service.get_nearby_facilities(
        latitude=lat,
        longitude=lon,
        radius=radius,
        page=page,
        page_size=page_size,
        category=category,
    )
    return ApiResponse(
        data=data,
        meta=ResponseMeta(source=data.source),
    )
