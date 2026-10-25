"""Weather service layer."""

from typing import Any
from pymongo.database import Database

from app.db.repositories.weather import WeatherRepository


class WeatherService:
    """Service managing weather observations and forecasts."""

    def __init__(self, database: Database) -> None:
        self.weather_repo = WeatherRepository(database)

    def get_weather(self, city_id: str, provider: str | None = None, limit: int = 10) -> dict[str, Any]:
        """Fetch latest weather observation and historical records for a city."""
        latest = self.weather_repo.get_latest_observation(city_id, provider=provider)
        history = self.weather_repo.get_observations(city_id, provider=provider, limit=limit)

        return {
            "city_id": city_id,
            "latest": latest,
            "history": history,
        }

    def get_forecast(self, city_id: str, provider: str | None = None, limit: int = 14) -> dict[str, Any]:
        """Fetch weather forecasts (WMO)."""
        forecasts = self.weather_repo.get_forecasts(city_id, provider=provider, limit=limit)
        return {
            "city_id": city_id,
            "provider": provider or "WMO",
            "forecasts": forecasts,
        }
