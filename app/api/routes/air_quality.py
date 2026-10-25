"""Air quality endpoints distinguishing separate datasets."""

from fastapi import APIRouter, Depends, Query
from pymongo.database import Database

from app.db.client import get_db
from app.schemas.air_quality import CityAirQualityResponse, GlobalWeatherAqItem, WhoAqItem
from app.schemas.common import ApiResponse, ResponseMeta
from app.services.air_quality import AirQualityService

router = APIRouter(prefix="/cities", tags=["Air Quality"])


@router.get(
    "/{city_id}/air-quality",
    response_model=ApiResponse[CityAirQualityResponse],
    summary="Get city air quality metrics",
)
def get_city_air_quality(
    city_id: str,
    limit: int = Query(10, ge=1, le=50, description="Max records per dataset"),
    database: Database = Depends(get_db),
) -> ApiResponse[CityAirQualityResponse]:
    """Retrieve air quality data preserving distinct Global Weather and WHO datasets without mixing."""
    service = AirQualityService(database)
    data = service.get_air_quality(city_id=city_id, limit=limit)

    gw_items = [GlobalWeatherAqItem(**item) for item in data.get("global_weather", [])]
    who_items = [WhoAqItem(**item) for item in data.get("who_annual", [])]

    return ApiResponse(
        data=CityAirQualityResponse(
            city_id=city_id,
            global_weather=gw_items,
            who_annual=who_items,
            available_providers=data.get("available_providers", []),
        ),
        meta=ResponseMeta(source="air_quality_multi_provider_ground_truth"),
    )
