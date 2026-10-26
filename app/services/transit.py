"""Public transit service layer."""

from typing import Any
from pymongo.database import Database

from app.core.cache import InMemoryTTLCache, build_cache_key, service_cache
from app.core.exceptions import ResourceNotFoundException
from app.core.logging import get_logger
from app.db.repositories.city import CityRepository
from app.providers.transit.base import BaseTransitProvider
from app.providers.transit.gtfs import GTFSTransitProvider

logger = get_logger("services.transit")


class TransitService:
    """Service mediating public transit feed queries through provider adapters."""

    def __init__(
        self,
        database: Database | None = None,
        provider: BaseTransitProvider | None = None,
        cache: InMemoryTTLCache | None = service_cache,
    ) -> None:
        self.database = database
        self.city_repo = CityRepository(database) if database is not None else None
        self.provider = provider or GTFSTransitProvider()
        self.cache = cache

    async def get_transit_info(self, city_id: str) -> dict[str, Any]:
        """Fetch GTFS transit feed information or return explicit DATA_UNAVAILABLE."""
        cache_key = build_cache_key("transit", city_id=city_id)
        if self.cache:
            cached = self.cache.get(cache_key)
            if cached:
                cached_res = dict(cached)
                cached_res["meta"] = {**cached.get("meta", {}), "cached": True}
                return cached_res

        city_name: str | None = None
        if self.city_repo is not None:
            city = self.city_repo.get_by_city_id(city_id)
            if not city:
                raise ResourceNotFoundException("city", city_id)
            city_name = city.get("name")

        res = await self.provider.get_transit_info(city_id)

        result = {
            "city_id": city_id,
            "city_name": city_name,
            "transit": res.data.model_dump() if res.data else None,
            "meta": res.meta.model_dump(),
        }

        if res.is_successful and res.data and self.cache:
            self.cache.set(cache_key, result, ttl_seconds=600.0)

        return result

