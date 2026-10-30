"""Education discovery endpoints."""

from fastapi import APIRouter, Depends, Query, Request
from pymongo.database import Database

from app.core.config import settings
from app.core.rate_limit import limiter
from app.db.client import get_db
from app.schemas.common import ApiResponse, ResponseMeta
from app.schemas.education import CityEducationResponse
from app.services.education import EducationService

router = APIRouter(prefix="/cities", tags=["Education Discovery"])


@router.get(
    "/{city_id}/education",
    response_model=ApiResponse[CityEducationResponse],
    summary="Discover educational institutions in and around a city",
)
@limiter.limit(settings.RATE_LIMIT_LIVE_PROVIDERS)
async def get_city_education(
    request: Request,
    city_id: str,
    type: str | None = Query(None, description="Filter by institution type (e.g. University, College, School, Medical College)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(25, ge=1, le=100, description="Items per page"),
    limit: int | None = Query(None, ge=1, le=100, description="Limit count (alias for page_size)"),
    offset: int | None = Query(None, ge=0, description="Pagination offset"),
    database: Database = Depends(get_db),
) -> ApiResponse[CityEducationResponse]:
    """Retrieve educational institutions for a city from canonical registry and OpenStreetMap."""
    service = EducationService(database)
    effective_limit = limit or page_size
    data = await service.get_city_education(
        city_id=city_id,
        institution_type=type,
        page=page,
        page_size=effective_limit,
        limit=effective_limit,
        offset=offset,
    )
    return ApiResponse(
        data=data,
        meta=ResponseMeta(source="World Universities Dataset & OpenStreetMap"),
    )
