"""Weather provider interface and normalized schemas."""

from abc import abstractmethod
from pydantic import BaseModel, Field

from app.providers.base import BaseProvider, ProviderResponse


class NormalizedCurrentWeather(BaseModel):
    """Normalized real-time weather observation."""

    temperature_c: float | None = None
    apparent_temperature_c: float | None = None
    relative_humidity_pct: float | None = None
    surface_pressure_mb: float | None = None
    wind_speed_kph: float | None = None
    precipitation_mm: float | None = None
    weather_code: int | None = None
    condition: str | None = None
    observed_at: str | None = None


class NormalizedDailyForecast(BaseModel):
    """Normalized daily weather forecast."""

    date: str
    temp_min_c: float | None = None
    temp_max_c: float | None = None
    precipitation_mm: float | None = None
    weather_code: int | None = None
    condition: str | None = None


class NormalizedWeather(BaseModel):
    """Normalized weather payload containing current observation and daily forecasts."""

    latitude: float
    longitude: float
    timezone: str | None = None
    elevation: float | None = None
    current: NormalizedCurrentWeather | None = None
    daily_forecasts: list[NormalizedDailyForecast] = Field(default_factory=list)


class BaseWeatherProvider(BaseProvider):
    """Abstract interface for weather providers."""

    @abstractmethod
    async def get_weather(
        self,
        latitude: float,
        longitude: float,
        forecast_days: int = 7,
    ) -> ProviderResponse[NormalizedWeather]:
        """Fetch current weather and daily forecasts for coordinates."""
        ...
