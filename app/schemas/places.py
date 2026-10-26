"""Places and POI search response schemas."""

from typing import Any
from pydantic import BaseModel, Field


class PlacesSearchResponse(BaseModel):
    """Response payload for category-based POI search."""

    latitude: float
    longitude: float
    category: str
    radius_meters: int
    places: list[dict[str, Any]] = Field(default_factory=list)
    count: int = 0
    meta: dict[str, Any]
