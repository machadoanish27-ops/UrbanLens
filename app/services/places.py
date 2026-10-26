"""Places and points of interest service layer."""

from typing import Any
from pymongo.database import Database

from app.core.logging import get_logger
from app.providers.places.base import BasePlacesProvider
from app.providers.places.overpass import OverpassPlacesProvider

logger = get_logger("services.places")


class PlacesService:
    """Service providing bounded POI search via replaceable places providers."""

    def __init__(
        self,
        database: Database | None = None,
        provider: BasePlacesProvider | None = None,
    ) -> None:
        self.database = database
        self.provider = provider or OverpassPlacesProvider()

    async def search_places(
        self,
        latitude: float,
        longitude: float,
        category: str = "hospital",
        radius: int = 1500,
        limit: int = 10,
    ) -> dict[str, Any]:
        """Search points of interest around coordinates for a specific category."""
        res = await self.provider.get_places(
            latitude=latitude,
            longitude=longitude,
            category=category,
            radius=radius,
            limit=limit,
        )

        return {
            "latitude": latitude,
            "longitude": longitude,
            "category": category,
            "radius_meters": radius,
            "places": [p.model_dump() for p in res.data] if res.data else [],
            "count": len(res.data) if res.data else 0,
            "meta": res.meta.model_dump(),
        }
