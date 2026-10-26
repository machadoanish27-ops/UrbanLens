"""Geocoding service layer."""

from typing import Any
from pymongo.database import Database

from app.core.cache import InMemoryTTLCache, build_cache_key, service_cache
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
        cache: InMemoryTTLCache | None = service_cache,
    ) -> None:
        self.database = database
        self.provider = provider or NominatimGeocodingProvider()
        self.cache = cache

    async def search(self, query: str, limit: int = 5) -> dict[str, Any]:
        """Forward geocode a text address or city query."""
        cache_key = build_cache_key("geocoding_search", q=query.strip().lower(), limit=limit)
        if self.cache:
            cached = self.cache.get(cache_key)
            if cached:
                cached_res = dict(cached)
                cached_res["meta"] = {**cached.get("meta", {}), "cached": True}
                return cached_res

        res = await self.provider.search(query=query, limit=limit)
        result = {
            "query": query,
            "results": [item.model_dump() for item in res.data] if res.data else [],
            "count": len(res.data) if res.data else 0,
            "meta": res.meta.model_dump(),
        }

        if res.is_successful and res.data and self.cache:
            self.cache.set(cache_key, result, ttl_seconds=3600.0)

        return result

    async def reverse(self, latitude: float, longitude: float) -> dict[str, Any]:
        """Reverse geocode coordinates to location description."""
        cache_key = build_cache_key("geocoding_reverse", lat=round(latitude, 4), lon=round(longitude, 4))
        if self.cache:
            cached = self.cache.get(cache_key)
            if cached:
                cached_res = dict(cached)
                cached_res["meta"] = {**cached.get("meta", {}), "cached": True}
                return cached_res

        res = await self.provider.reverse(latitude=latitude, longitude=longitude)
        result = {
            "latitude": latitude,
            "longitude": longitude,
            "result": res.data.model_dump() if res.data else None,
            "meta": res.meta.model_dump(),
        }

        if res.is_successful and res.data and self.cache:
            self.cache.set(cache_key, result, ttl_seconds=3600.0)

        return result

