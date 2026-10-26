"""Weather service layer with live provider integration and graceful fallback."""

from typing import Any
from pymongo.database import Database

from app.core.exceptions import DataUnavailableException, ResourceNotFoundException
from app.core.logging import get_logger
from app.db.repositories.city import CityRepository
from app.db.repositories.weather import WeatherRepository
from app.providers.base import LiveMetadata, LiveStatus
from app.providers.weather.base import (
    BaseWeatherProvider,
    NormalizedCurrentWeather,
    NormalizedWeather,
)
from app.providers.weather.open_meteo import OpenMeteoWeatherProvider

logger = get_logger("services.weather")


class WeatherService:
    """Service managing weather observations, WMO forecasts, and live meteorological feeds."""

    def __init__(
        self,
        database: Database,
        provider: BaseWeatherProvider | None = None,
    ) -> None:
        self.database = database
        self.weather_repo = WeatherRepository(database)
        self.city_repo = CityRepository(database)
        self.provider = provider or OpenMeteoWeatherProvider()

    def get_weather(self, city_id: str, provider: str | None = None, limit: int = 10) -> dict[str, Any]:
        """Fetch latest weather observation and historical records for a city from database."""
        latest = self.weather_repo.get_latest_observation(city_id, provider=provider)
        history = self.weather_repo.get_observations(city_id, provider=provider, limit=limit)

        return {
            "city_id": city_id,
            "latest": latest,
            "history": history,
        }

    def get_forecast(self, city_id: str, provider: str | None = None, limit: int = 14) -> dict[str, Any]:
        """Fetch weather forecasts (WMO) from database."""
        forecasts = self.weather_repo.get_forecasts(city_id, provider=provider, limit=limit)
        return {
            "city_id": city_id,
            "provider": provider or "WMO",
            "forecasts": forecasts,
        }

    async def get_live_weather(self, city_id: str, forecast_days: int = 7) -> dict[str, Any]:
        """Retrieve live weather for a city with multi-tier fallback architecture:
        
        1. Live external provider (Open-Meteo)
        2. Fresh cache (extension point)
        3. Canonical MongoDB ground-truth observation
        4. Explicit DATA_UNAVAILABLE
        """
        city = self.city_repo.get_by_city_id(city_id)
        if not city:
            raise ResourceNotFoundException("city", city_id)

        latitude = city.get("latitude")
        longitude = city.get("longitude")

        # If coordinates are missing, check database ground-truth immediately
        if latitude is None or longitude is None:
            return self._build_database_fallback(
                city_id=city_id,
                city_name=city.get("name"),
                latitude=0.0,
                longitude=0.0,
                reason="Canonical city record lacks latitude/longitude coordinates.",
            )

        # 1. Attempt live provider
        res = await self.provider.get_weather(
            latitude=float(latitude),
            longitude=float(longitude),
            forecast_days=forecast_days,
        )

        if res.is_successful and res.data:
            return {
                "city_id": city_id,
                "city_name": city.get("name"),
                "latitude": float(latitude),
                "longitude": float(longitude),
                "weather": res.data.model_dump(),
                "meta": res.meta.model_dump(),
            }

        # 2. Fallback to MongoDB ground-truth observations
        return self._build_database_fallback(
            city_id=city_id,
            city_name=city.get("name"),
            latitude=float(latitude),
            longitude=float(longitude),
            reason=res.meta.error_detail or "Live weather provider returned error status.",
        )

    def _build_database_fallback(
        self,
        city_id: str,
        city_name: str | None,
        latitude: float,
        longitude: float,
        reason: str,
    ) -> dict[str, Any]:
        """Construct normalized response from latest database observation or mark unavailable."""
        latest_obs = self.weather_repo.get_latest_observation(city_id)
        if latest_obs:
            obs_dt = latest_obs.get("observed_at")
            current = NormalizedCurrentWeather(
                temperature_c=latest_obs.get("temperature_c"),
                apparent_temperature_c=None,
                relative_humidity_pct=latest_obs.get("humidity_pct"),
                surface_pressure_mb=latest_obs.get("pressure_mb"),
                wind_speed_kph=latest_obs.get("wind_kph"),
                precipitation_mm=latest_obs.get("precip_mm"),
                weather_code=None,
                condition=None,
                observed_at=str(obs_dt) if obs_dt else None,
            )
            normalized_db = NormalizedWeather(
                latitude=latitude,
                longitude=longitude,
                current=current,
                daily_forecasts=[],
            )
            meta = LiveMetadata(
                provider="mongodb",
                source="MongoDB weather_observations ground-truth fallback",
                status=LiveStatus.DATABASE,
                observed_at=str(obs_dt) if obs_dt else None,
                error_detail=f"Live provider fallback: {reason}",
            )
            return {
                "city_id": city_id,
                "city_name": city_name,
                "latitude": latitude,
                "longitude": longitude,
                "weather": normalized_db.model_dump(),
                "meta": meta.model_dump(),
            }

        # Explicitly unavailable when neither live feed nor database records exist
        meta = LiveMetadata(
            provider=self.provider.provider_name,
            source=self.provider.source_info,
            status=LiveStatus.UNAVAILABLE,
            error_detail=f"Weather data unavailable: {reason}",
        )
        return {
            "city_id": city_id,
            "city_name": city_name,
            "latitude": latitude,
            "longitude": longitude,
            "weather": None,
            "meta": meta.model_dump(),
        }
