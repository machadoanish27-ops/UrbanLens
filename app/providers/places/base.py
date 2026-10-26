"""Places and POI provider base interface and schemas."""

from abc import abstractmethod
from pydantic import BaseModel, Field

from app.providers.base import BaseProvider, ProviderResponse


class NormalizedPlaceItem(BaseModel):
    """Normalized point of interest (POI)."""

    place_id: str | int
    name: str
    category: str
    latitude: float
    longitude: float
    distance_meters: float | None = None
    amenity: str | None = None
    tags: dict[str, str] = Field(default_factory=dict)


class BasePlacesProvider(BaseProvider):
    """Abstract interface for places and POI discovery providers."""

    @abstractmethod
    async def get_places(
        self,
        latitude: float,
        longitude: float,
        category: str = "hospital",
        radius: int = 1500,
        limit: int = 10,
    ) -> ProviderResponse[list[NormalizedPlaceItem]]:
        """Query controlled category-based points of interest around coordinates."""
        ...
