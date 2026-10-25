"""Weather repository accessing weather observations and WMO forecasts."""

from typing import Any
from pymongo.database import Database

from app.db.repositories.base import BaseRepository


class WeatherRepository(BaseRepository):
    """Repository for ground-truth weather observations and WMO forecasts."""

    def __init__(self, database: Database) -> None:
        super().__init__(database, "weather_observations")
        self.forecasts_repo = BaseRepository(database, "weather_forecasts_wmo")

    def get_latest_observation(self, city_id: str, provider: str | None = None) -> dict[str, Any] | None:
        """Fetch the most recent weather observation for a city."""
        filters: dict[str, Any] = {"city_id": city_id}
        if provider:
            filters["provider"] = provider
        # Sort descending by observed_at
        return self.find_one(filters, sort=[("observed_at", -1)])

    def get_observations(
        self,
        city_id: str,
        provider: str | None = None,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """Fetch historical observations for a city."""
        filters: dict[str, Any] = {"city_id": city_id}
        if provider:
            filters["provider"] = provider
        return self.find_many(filters, sort=[("observed_at", -1)], limit=limit)

    def get_forecasts(
        self,
        city_id: str,
        provider: str | None = None,
        limit: int = 14,
    ) -> list[dict[str, Any]]:
        """Fetch upcoming weather forecasts (WMO)."""
        filters: dict[str, Any] = {"city_id": city_id}
        if provider:
            filters["provider"] = provider
        return self.forecasts_repo.find_many(filters, sort=[("forecast_for", 1)], limit=limit)
