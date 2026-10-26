"""Public transport provider base interface and GTFS abstraction schemas."""

from abc import abstractmethod
from typing import Any
from pydantic import BaseModel, Field

from app.providers.base import BaseProvider, ProviderResponse


class NormalizedTransitAlert(BaseModel):
    """Transit service alert or disruption."""

    id: str
    cause: str | None = None
    effect: str | None = None
    header_text: str
    description_text: str | None = None


class NormalizedTransitFeedInfo(BaseModel):
    """Normalized transit coverage and feed status."""

    city_id: str
    is_feed_configured: bool = False
    agency_name: str | None = None
    feed_url: str | None = None
    realtime_url: str | None = None
    coverage_summary: str | None = None
    routes_count: int | None = None
    alerts: list[NormalizedTransitAlert] = Field(default_factory=list)


class BaseTransitProvider(BaseProvider):
    """Abstract interface for public transit providers (GTFS / GTFS-Realtime)."""

    @abstractmethod
    async def get_transit_info(self, city_id: str) -> ProviderResponse[NormalizedTransitFeedInfo]:
        """Fetch GTFS feed status and alerts for a registered city."""
        ...
