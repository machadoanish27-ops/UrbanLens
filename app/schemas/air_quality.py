from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field


class GlobalWeatherAqItem(BaseModel):
    """Observational air quality from Global Weather dataset."""

    city_id: str
    provider: str
    observed_at: datetime | str | None = None
    aqi_us_epa: int | float | None = None
    pm25: float | None = None
    pm10: float | None = None
    no2: float | None = None
    so2: float | None = None
    o3: float | None = None
    co: float | None = None
    source_row: int | None = None


class WhoAqItem(BaseModel):
    """Annual WHO urban air quality monitoring dataset."""

    city_id: str
    source: str
    year: int | None = None
    pm25_annual_mean_ug_m3: float | None = None
    pm10_annual_mean_ug_m3: float | None = None
    pm25_temporal_coverage: str | None = None
    pm10_temporal_coverage: str | None = None
    pm25_converted: bool | None = None
    pm10_converted: bool | None = None
    source_row: int | None = None


class CityAirQualityResponse(BaseModel):
    """Comprehensive air quality response presenting both datasets with uncompromised provenance."""

    city_id: str
    global_weather: list[GlobalWeatherAqItem] = Field(default_factory=list)
    who_annual: list[WhoAqItem] = Field(default_factory=list)
    available_providers: list[str] = Field(default_factory=list)


class LiveCityAirQualityResponse(BaseModel):
    """Live air quality response with provenance and fallback metadata."""

    city_id: str
    city_name: str | None = None
    latitude: float
    longitude: float
    air_quality: dict[str, Any] | None = None
    meta: dict[str, Any]

