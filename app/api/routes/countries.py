"""Country and macroeconomic metrics endpoints."""

from fastapi import APIRouter, Depends, Query
from pymongo.database import Database

from app.db.client import get_db
from app.schemas.common import ApiResponse, PaginationMeta, ResponseMeta
from app.schemas.country import (
    CountryDetail,
    CountryItem,
    CountryLanguageInfo,
    CountryMetricItem,
    CountryMetricsResponse,
)
from app.services.country import CountryService

router = APIRouter(prefix="/countries", tags=["Countries"])


@router.get("", response_model=ApiResponse[list[CountryItem]], summary="List countries")
def list_countries(
    continent: str | None = Query(None, description="Filter by continent name"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size"),
    database: Database = Depends(get_db),
) -> ApiResponse[list[CountryItem]]:
    """Retrieve paginated countries."""
    service = CountryService(database)
    items, total = service.list_countries(continent=continent, page=page, page_size=page_size)
    pagination = PaginationMeta.create(page=page, page_size=page_size, total=total)
    return ApiResponse(
        data=[CountryItem(**item) for item in items],
        meta=ResponseMeta(pagination=pagination, source="countries_collection"),
    )


@router.get("/{country_id}", response_model=ApiResponse[CountryDetail], summary="Get country details")
def get_country(
    country_id: str,
    database: Database = Depends(get_db),
) -> ApiResponse[CountryDetail]:
    """Retrieve single country details by country_id or ISO code."""
    service = CountryService(database)
    country = service.get_country(country_id)
    return ApiResponse(
        data=CountryDetail(**country),
        meta=ResponseMeta(source="countries_collection"),
    )


@router.get("/{country_id}/languages", response_model=ApiResponse[CountryLanguageInfo], summary="Get country authoritative language data")
def get_country_languages(
    country_id: str,
    database: Database = Depends(get_db),
) -> ApiResponse[CountryLanguageInfo]:
    """Retrieve authoritative spoken and official languages with provenance."""
    service = CountryService(database)
    languages = service.get_country_languages(country_id)
    return ApiResponse(
        data=CountryLanguageInfo(**languages),
        meta=ResponseMeta(source=languages.get("source") or "un_iso_languages"),
    )


@router.get("/{country_id}/metrics", response_model=ApiResponse[CountryMetricsResponse], summary="Get country macroeconomic metrics")
def get_country_metrics(
    country_id: str,
    metric: str | None = Query(None, description="Specific metric filter"),
    period: int | None = Query(None, description="Year or period filter"),
    database: Database = Depends(get_db),
) -> ApiResponse[CountryMetricsResponse]:
    """Retrieve socioeconomic and GDP metrics for a country."""
    service = CountryService(database)
    metrics_data = service.get_country_metrics(country_id, metric=metric, period=period)
    return ApiResponse(
        data=CountryMetricsResponse(
            country_id=metrics_data["country_id"],
            metrics=[CountryMetricItem(**m) for m in metrics_data["metrics"]],
            gdp_metrics=[CountryMetricItem(**m) for m in metrics_data["gdp_metrics"]],
        ),
        meta=ResponseMeta(source="country_metrics_collection"),
    )
