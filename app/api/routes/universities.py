"""University and academic institutions endpoints."""

from fastapi import APIRouter, Depends, Query
from pymongo.database import Database

from app.db.client import get_db
from app.schemas.common import ApiResponse, PaginationMeta, ResponseMeta
from app.schemas.university import UniversityDetail, UniversityItem, UniversityRankingItem
from app.services.university import UniversityService

router = APIRouter(tags=["Universities"])


@router.get(
    "/cities/{city_id}/universities",
    response_model=ApiResponse[list[UniversityItem]],
    summary="List universities associated with a city's region",
)
def get_city_universities(
    city_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size"),
    database: Database = Depends(get_db),
) -> ApiResponse[list[UniversityItem]]:
    """Retrieve universities located in or associated with a city's national region."""
    service = UniversityService(database)
    items, total = service.get_universities_by_city(city_id=city_id, page=page, page_size=page_size)
    pagination = PaginationMeta.create(page=page, page_size=page_size, total=total)

    return ApiResponse(
        data=[UniversityItem(**item) for item in items],
        meta=ResponseMeta(pagination=pagination, source="universities_collection"),
    )


@router.get(
    "/universities/{university_id}",
    response_model=ApiResponse[UniversityDetail],
    summary="Get university details",
)
def get_university(
    university_id: str,
    database: Database = Depends(get_db),
) -> ApiResponse[UniversityDetail]:
    """Retrieve university institution profile and ranking history."""
    service = UniversityService(database)
    univ_data = service.get_university(university_id)

    rankings_raw = univ_data.get("rankings", [])
    rankings_objs = [UniversityRankingItem(**r) for r in rankings_raw]
    univ_dict = {k: v for k, v in univ_data.items() if k != "rankings"}

    return ApiResponse(
        data=UniversityDetail(**univ_dict, rankings=rankings_objs),
        meta=ResponseMeta(source="universities_and_rankings"),
    )


@router.get(
    "/universities/{university_id}/rankings",
    response_model=ApiResponse[list[UniversityRankingItem]],
    summary="Get university ranking history",
)
def get_university_rankings(
    university_id: str,
    ranking_metric: str | None = Query(None, description="Optional ranking metric filter"),
    year: int | None = Query(None, description="Optional ranking year filter"),
    database: Database = Depends(get_db),
) -> ApiResponse[list[UniversityRankingItem]]:
    """Retrieve ranking entries for an institution with provenance and unavailable indicators."""
    service = UniversityService(database)
    rankings = service.get_university_rankings(
        university_id=university_id,
        ranking_metric=ranking_metric,
        year=year,
    )

    return ApiResponse(
        data=[UniversityRankingItem(**r) for r in rankings],
        meta=ResponseMeta(source="university_rankings_collection"),
    )
