"""Routing service layer."""

from typing import Any
from pymongo.database import Database

from app.core.cache import InMemoryTTLCache, build_cache_key, service_cache
from app.core.logging import get_logger
from app.providers.routing.base import BaseRoutingProvider
from app.providers.routing.osrm import OSRMRoutingProvider

logger = get_logger("services.routing")


class RoutingService:
    """Service providing waypoint-to-waypoint routing via provider adapters."""

    def __init__(
        self,
        database: Database | None = None,
        provider: BaseRoutingProvider | None = None,
        cache: InMemoryTTLCache | None = service_cache,
    ) -> None:
        self.database = database
        self.provider = provider or OSRMRoutingProvider()
        self.cache = cache

    async def calculate_route(
        self,
        origin_lat: float,
        origin_lon: float,
        dest_lat: float,
        dest_lon: float,
        profile: str = "driving",
    ) -> dict[str, Any]:
        """Calculate routing distance, duration, and summary between waypoints."""
        cache_key = build_cache_key(
            "routing",
            olat=round(origin_lat, 4),
            olon=round(origin_lon, 4),
            dlat=round(dest_lat, 4),
            dlon=round(dest_lon, 4),
            profile=profile,
        )
        if self.cache:
            cached = self.cache.get(cache_key)
            if cached:
                cached_res = dict(cached)
                cached_res["meta"] = {**cached.get("meta", {}), "cached": True}
                return cached_res

        res = await self.provider.get_route(
            origin_lat=origin_lat,
            origin_lon=origin_lon,
            dest_lat=dest_lat,
            dest_lon=dest_lon,
            profile=profile,
        )

        result = {
            "origin": {"latitude": origin_lat, "longitude": origin_lon},
            "destination": {"latitude": dest_lat, "longitude": dest_lon},
            "route": res.data.model_dump() if res.data else None,
            "meta": res.meta.model_dump(),
        }

        if res.is_successful and res.data and self.cache:
            self.cache.set(cache_key, result, ttl_seconds=600.0)

        return result

