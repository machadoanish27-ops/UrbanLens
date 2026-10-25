"""Weather observations and WMO forecasts endpoints."""

from fastapi import APIRouter, Depends, Query
from pymongo.database import Database

from app.db.client import get_db
from app.schemas.common import ApiResponse, ResponseMeta
from app.schemas.weather import (
    CityForecastResponse,
    CityWeatherResponse,
    WeatherForecastItem,
    WeatherObservationItem,
)
from app.services.weather import WeatherService

router = APIRouter(prefix="/cities", tags=["Weather"])


@router.get(
    "/{city_id}/weather",
    response_model=ApiResponse[CityWeatherResponse],
    summary="Get ground-truth weather observations",
)
def get_city_weather(
    city_id: str,
    provider: str | None = Query(None, description="Optional provider filter"),
    limit: int = Query(10, ge=1, le=50, description="Max observations history to return"),
    database: Database = Depends(get_db),
) -> ApiResponse[CityWeatherResponse]:
    """Retrieve the latest ground-truth weather observation and history for a city."""
    service = WeatherService(database)
    data = service.get_weather(city_id=city_id, provider=provider, limit=limit)
    latest_obj = WeatherObservationItem(**data["latest"]) if data.get("latest") else None
    history_objs = [WeatherObservationItem(**item) for item in data.get("history", [])]

    return ApiResponse(
        data=CityWeatherResponse(
            city_id=city_id,
            latest=latest_obj,
            history=history_objs,
        ),
        meta=ResponseMeta(source="weather_observations_ground_truth"),
    )


@router.get(
    "/{city_id}/weather/forecast",
    response_model=ApiResponse[CityForecastResponse],
    summary="Get official WMO weather forecasts",
)
def get_city_forecast(
    city_id: str,
    provider: str | None = Query(None, description="Optional provider filter"),
    limit: int = Query(14, ge=1, le=30, description="Max forecast days"),
    database: Database = Depends(get_db),
) -> ApiResponse[CityForecastResponse]:
    """Retrieve forward-looking WMO forecasts preserving provenance and timestamps."""
    service = WeatherService(database)
    data = service.get_forecast(city_id=city_id, provider=provider, limit=limit)
    forecast_objs = [WeatherForecastItem(**item) for item in data.get("forecasts", [])]

    return ApiResponse(
        data=CityForecastResponse(
            city_id=city_id,
            provider=data.get("provider", "WMO"),
            forecasts=forecast_objs,
        ),
        meta=ResponseMeta(source="weather_forecasts_wmo"),
    )
