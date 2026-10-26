"""Routing provider base interface and schemas."""

from abc import abstractmethod
from pydantic import BaseModel, Field

from app.providers.base import BaseProvider, ProviderResponse


class NormalizedRoute(BaseModel):
    """Normalized route summary between two geographic waypoints."""

    origin_lat: float
    origin_lon: float
    dest_lat: float
    dest_lon: float
    distance_meters: float = Field(..., description="Route distance in meters")
    distance_km: float = Field(..., description="Route distance in kilometers")
    duration_seconds: float = Field(..., description="Estimated travel duration in seconds")
    duration_minutes: float = Field(..., description="Estimated travel duration in minutes")
    profile: str = Field(default="driving", description="Routing mode, e.g. driving, walking")


class BaseRoutingProvider(BaseProvider):
    """Abstract interface for routing providers."""

    @abstractmethod
    async def get_route(
        self,
        origin_lat: float,
        origin_lon: float,
        dest_lat: float,
        dest_lon: float,
        profile: str = "driving",
    ) -> ProviderResponse[NormalizedRoute]:
        """Calculate route between origin and destination coordinates."""
        ...
