"""Cost of living repository accessing canonical cost-of-living metrics."""

from typing import Any
from pymongo.database import Database

from app.db.repositories.base import BaseRepository


class CostOfLivingRepository(BaseRepository):
    """Repository for city cost-of-living and affordability metrics."""

    def __init__(self, database: Database) -> None:
        super().__init__(database, "cost_of_living")

    def get_by_city_id(
        self,
        city_id: str,
        metric: str | None = None,
    ) -> list[dict[str, Any]]:
        """Fetch cost of living metrics for a city."""
        filters: dict[str, Any] = {"city_id": city_id}
        if metric:
            filters["metric"] = metric
        return self.find_many(filters, sort=[("metric", 1), ("observed_at", -1)])

    def get_city_metrics_dict(self, city_id: str) -> dict[str, dict[str, Any]]:
        """Fetch cost of living metrics structured by metric key."""
        items = self.get_by_city_id(city_id)
        return {item["metric"]: item for item in items if "metric" in item}
