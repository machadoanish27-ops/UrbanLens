"""Geocoding service layer."""

from typing import Any
from pymongo.database import Database

from app.core.logging import get_logger
from app.providers.geocoding.base import BaseGeocodingProvider
from app.providers.geocoding.nominatim import NominatimGeocodingProvider

logger = get_logger("services.geocoding")


class GeocodingService:
    """Service providing forward and reverse geocoding via provider adapters."""

    def __init__(
        self,
        database: Database | None = None,
        provider: BaseGeocodingProvider | None = None,
    ) -> None:
        self.database = database
        self.provider = provider or NominatimGeocodingProvider()

    async def search(self, query: str, limit: int = 5) -> dict[str, Any]:
        """Forward geocode a text address or city query."""
        res = await self.provider.search(query=query, limit=limit)
        return {
            "query": query,
            "results": [item.model_dump() for item in res.data] if res.data else [],
            "count": len(res.data) if res.data else 0,
            "meta": res.meta.model_dump(),
        }

    async def reverse(self, latitude: float, longitude: float) -> dict[str, Any]:
        """Reverse geocode coordinates to location description."""
        res = await self.provider.reverse(latitude=latitude, longitude=longitude)
        return {
            "latitude": latitude,
            "longitude": longitude,
            "result": res.data.model_dump() if res.data else None,
            "meta": res.meta.model_dump(),
        }
