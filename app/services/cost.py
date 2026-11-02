"""Cost of living service layer."""

from typing import Any
from pymongo.database import Database

from app.core.exceptions import DataUnavailableException
from app.db.repositories.city import CityRepository
from app.db.repositories.cost_of_living import CostOfLivingRepository


class CostOfLivingService:
    """Service providing canonical cost-of-living metrics."""

    def __init__(self, database: Database) -> None:
        self.cost_repo = CostOfLivingRepository(database)
        self.city_repo = CityRepository(database)

    def _resolve_canonical_city_id(self, city_id: str) -> str:
        """Resolve city alias, slug, or name to canonical city_id."""
        if city_id.startswith("city_"):
            return city_id

        # Try resolving via alias mapping (e.g. 'mumbai-in', 'mumbai')
        resolved = self.city_repo.resolve_alias_to_city_id(city_id)
        if resolved:
            return resolved

        # Try prefix before dash (e.g., 'mumbai-in' -> 'mumbai')
        if "-" in city_id:
            prefix = city_id.split("-")[0]
            resolved = self.city_repo.resolve_alias_to_city_id(prefix)
            if resolved:
                return resolved

        # Try searching by name
        cities, _ = self.city_repo.search_cities(query=city_id.split("-")[0], page_size=1)
        if cities and "city_id" in cities[0]:
            return str(cities[0]["city_id"])

        return city_id

    def get_cost_of_living(self, city_id: str, metric: str | None = None) -> dict[str, Any]:
        """Fetch cost of living metrics for a city, or return explicit unavailable structure."""
        canonical_id = self._resolve_canonical_city_id(city_id)
        metrics = self.cost_repo.get_by_city_id(canonical_id, metric=metric)
        if not metrics and canonical_id != city_id:
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
