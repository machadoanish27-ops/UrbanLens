"""City intelligence endpoints."""

from fastapi import APIRouter, Depends, Query
from pymongo.database import Database

from app.db.client import get_db
from app.schemas.city import CityDetail, CityListItem, CityOverview
from app.schemas.common import ApiResponse, PaginationMeta, ResponseMeta
from app.services.city import CityService

router = APIRouter(prefix="/cities", tags=["Cities"])


@router.get("", response_model=ApiResponse[list[CityListItem]], summary="Search and filter cities")
def list_cities(
    q: str | None = Query(None, description="City name or alias query"),
    country_id: str | None = Query(None, description="Country identifier filter"),
    country_iso2: str | None = Query(None, description="Two-letter ISO country code"),
    country_iso3: str | None = Query(None, description="Three-letter ISO country code"),
    min_population: int | None = Query(None, ge=0, description="Minimum population threshold"),
    max_population: int | None = Query(None, ge=0, description="Maximum population threshold"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size"),
    database: Database = Depends(get_db),
) -> ApiResponse[list[CityListItem]]:
    """Retrieve paginated cities matching search criteria."""
    service = CityService(database)
    items, total = service.search_cities(
        query=q,
        country_id=country_id,
        country_iso2=country_iso2,
        country_iso3=country_iso3,
        min_population=min_population,
        max_population=max_population,
        page=page,
        page_size=page_size,
    )
    pagination = PaginationMeta.create(page=page, page_size=page_size, total=total)
    return ApiResponse(
        data=[CityListItem(**item) for item in items],
        meta=ResponseMeta(pagination=pagination, source="cities_collection"),
    )


@router.get("/{city_id}", response_model=ApiResponse[CityDetail], summary="Get city details")
def get_city(
    city_id: str,
    database: Database = Depends(get_db),
) -> ApiResponse[CityDetail]:
    """Retrieve full canonical city record with registered aliases and provider mappings."""
    service = CityService(database)
    city_data = service.get_city_details(city_id)
    return ApiResponse(
        data=CityDetail(**city_data),
        meta=ResponseMeta(source="cities_with_identities"),
    )


@router.get("/{city_id}/overview", response_model=ApiResponse[CityOverview], summary="Get comprehensive city overview")
def get_city_overview(
    city_id: str,
    database: Database = Depends(get_db),
) -> ApiResponse[CityOverview]:
    """Synthesize multi-dimensional urban overview across weather, air quality, economics, and education."""
    service = CityService(database)
    overview_data = service.get_city_overview(city_id)
    return ApiResponse(
        data=CityOverview(**overview_data),
        meta=ResponseMeta(source="urbanlens_city_overview_engine"),
    )
