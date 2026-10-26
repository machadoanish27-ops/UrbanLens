"""Geocoding provider base interface and schemas."""

from abc import abstractmethod
from pydantic import BaseModel, Field

from app.providers.base import BaseProvider, ProviderResponse


class NormalizedGeocodingItem(BaseModel):
    """Normalized geocoding record for forward and reverse lookups."""

    place_id: str | int
    name: str | None = None
    display_name: str
    latitude: float
    longitude: float
    type: str | None = None
    category: str | None = None
    importance: float | None = None
    boundingbox: list[float] | None = None


class BaseGeocodingProvider(BaseProvider):
    """Abstract interface for geocoding providers."""

    @abstractmethod
    async def search(
        self,
        query: str,
        limit: int = 5,
    ) -> ProviderResponse[list[NormalizedGeocodingItem]]:
        """Forward geocode a text address or city query."""
        ...

    @abstractmethod
    async def reverse(
        self,
        latitude: float,
        longitude: float,
    ) -> ProviderResponse[NormalizedGeocodingItem]:
        """Reverse geocode coordinates to location and address description."""
        ...
