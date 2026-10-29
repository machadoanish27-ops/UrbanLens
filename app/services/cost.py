"""Cost of living service layer."""

from typing import Any
from pymongo.database import Database

from app.core.exceptions import DataUnavailableException
from app.db.repositories.cost_of_living import CostOfLivingRepository


class CostOfLivingService:
    """Service providing canonical cost-of-living metrics."""

    def __init__(self, database: Database) -> None:
        self.cost_repo = CostOfLivingRepository(database)

    def get_cost_of_living(self, city_id: str, metric: str | None = None) -> dict[str, Any]:
        """Fetch cost of living metrics for a city, or return explicit unavailable structure."""
        metrics = self.cost_repo.get_by_city_id(city_id, metric=metric)
        if not metrics:
            return {
                "city_id": city_id,
                "is_available": False,
                "status": "unavailable",
                "metric_count": 0,
                "metrics": [],
                "source": None,
                "warning": "Cost of living data is not currently available for this city.",
            }

        return {
            "city_id": city_id,
            "is_available": True,
            "status": "available",
            "metric_count": len(metrics),
            "metrics": metrics,
            "source": "cost_of_living_canonical",
            "warning": None,
        }
