"""Air quality service layer."""

from typing import Any
from pymongo.database import Database

from app.db.repositories.air_quality import AirQualityRepository


class AirQualityService:
    """Service providing source-grounded air quality data without silently merging datasets."""

    def __init__(self, database: Database) -> None:
        self.aq_repo = AirQualityRepository(database)

    def get_air_quality(self, city_id: str, limit: int = 10) -> dict[str, Any]:
        """Fetch both Global Weather and WHO datasets while maintaining dataset separation."""
        gw_records = self.aq_repo.get_global_weather_aq(city_id, limit=limit)
        who_records = self.aq_repo.get_who_aq(city_id, limit=limit)

        available_providers = []
        if gw_records:
            available_providers.append("GlobalWeather")
        if who_records:
            available_providers.append("WHO")

        return {
            "city_id": city_id,
            "global_weather": gw_records,
            "who_annual": who_records,
            "available_providers": available_providers,
        }
