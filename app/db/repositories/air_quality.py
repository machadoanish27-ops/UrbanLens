"""Air quality repository accessing Global Weather AQ and WHO AQ collections."""

from typing import Any
from pymongo.database import Database

from app.db.repositories.base import BaseRepository


class AirQualityRepository:
    """Repository for city air quality datasets, maintaining explicit provenance and never mixing them."""

    def __init__(self, database: Database) -> None:
        self.global_weather_repo = BaseRepository(database, "air_quality_observations_global_weather")
        self.who_repo = BaseRepository(database, "air_quality_observations_who")

    def get_global_weather_aq(
        self,
        city_id: str,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """Fetch observational air quality records from Global Weather provider."""
        return self.global_weather_repo.find_many(
            {"city_id": city_id},
            sort=[("observed_at", -1)],
            limit=limit,
        )

    def get_latest_global_weather_aq(self, city_id: str) -> dict[str, Any] | None:
        """Fetch the most recent Global Weather AQ record."""
        return self.global_weather_repo.find_one(
            {"city_id": city_id},
            sort=[("observed_at", -1)],
        )

    def get_who_aq(
        self,
        city_id: str,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """Fetch annual mean air quality observations from WHO dataset."""
        return self.who_repo.find_many(
            {"city_id": city_id},
            sort=[("year", -1)],
            limit=limit,
        )

    def get_latest_who_aq(self, city_id: str) -> dict[str, Any] | None:
        """Fetch the most recent annual WHO air quality record."""
        return self.who_repo.find_one(
            {"city_id": city_id},
            sort=[("year", -1)],
        )
