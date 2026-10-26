"""Places and points of interest service layer."""

from typing import Any
from pymongo.database import Database

from app.core.cache import InMemoryTTLCache, build_cache_key, service_cache
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
        cache: InMemoryTTLCache | None = service_cache,
    ) -> None:
        self.database = database
        self.provider = provider or OverpassPlacesProvider()
        self.cache = cache

    async def search_places(
        self,
        latitude: float,
        longitude: float,
        category: str = "hospital",
        radius: int = 1500,
        limit: int = 10,
    ) -> dict[str, Any]:
        """Search points of interest around coordinates for a specific category."""
        cache_key = build_cache_key(
            "places",
            lat=round(latitude, 4),
            lon=round(longitude, 4),
            cat=category.strip().lower(),
            rad=radius,
            lim=limit,
        )
        if self.cache:
            cached = self.cache.get(cache_key)
            if cached:
                cached_res = dict(cached)
                cached_res["meta"] = {**cached.get("meta", {}), "cached": True}
                return cached_res

        res = await self.provider.get_places(
            latitude=latitude,
            longitude=longitude,
            category=category,
            radius=radius,
            limit=limit,
        )

        result = {
            "latitude": latitude,
            "longitude": longitude,
            "category": category,
            "radius_meters": radius,
            "places": [p.model_dump() for p in res.data] if res.data else [],
            "count": len(res.data) if res.data else 0,
            "meta": res.meta.model_dump(),
        }

        if res.is_successful and res.data and self.cache:
            self.cache.set(cache_key, result, ttl_seconds=600.0)

        return result

