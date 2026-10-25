"""Weather and forecast schemas."""

from pydantic import BaseModel, Field


class WeatherObservationItem(BaseModel):
    """Ground-truth weather observation record."""

    city_id: str
    provider: str
    observed_at: str | None = None
    temperature_c: float | None = None
    humidity_pct: float | None = None
    pressure_mb: float | None = None
    wind_kph: float | None = None
    precip_mm: float | None = None
    visibility_km: float | None = None
    uv_index: float | None = None
    source_row: int | None = None


class WeatherForecastItem(BaseModel):
    """WMO official weather forecast entry."""

    city_id: str
    provider: str
    forecast_for: str | None = None
    fetched_at: str | None = None
    forecast_min_temp_c: float | None = None
    forecast_max_temp_c: float | None = None
    condition: str | None = None
    description: str | None = None
    timezone: str | None = None
    source_city_id: str | None = None


class CityWeatherResponse(BaseModel):
    """Weather response combining latest observation and optional recent trend."""

    city_id: str
    latest: WeatherObservationItem | None = None
    history: list[WeatherObservationItem] = Field(default_factory=list)


class CityForecastResponse(BaseModel):
    """Forecast response containing forward-looking meteorological forecasts."""

    city_id: str
    provider: str = "WMO"
    forecasts: list[WeatherForecastItem] = Field(default_factory=list)
