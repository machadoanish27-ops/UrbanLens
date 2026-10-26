"""Routing service layer."""

from typing import Any
from pymongo.database import Database

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
    ) -> None:
        self.database = database
        self.provider = provider or OSRMRoutingProvider()

    async def calculate_route(
        self,
        origin_lat: float,
        origin_lon: float,
        dest_lat: float,
        dest_lon: float,
        profile: str = "driving",
    ) -> dict[str, Any]:
        """Calculate routing distance, duration, and summary between waypoints."""
        res = await self.provider.get_route(
            origin_lat=origin_lat,
            origin_lon=origin_lon,
            dest_lat=dest_lat,
            dest_lon=dest_lon,
            profile=profile,
        )

        return {
            "origin": {"latitude": origin_lat, "longitude": origin_lon},
            "destination": {"latitude": dest_lat, "longitude": dest_lon},
            "route": res.data.model_dump() if res.data else None,
            "meta": res.meta.model_dump(),
        }
