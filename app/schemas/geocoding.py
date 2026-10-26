"""Geocoding search and reverse lookup response schemas."""

from typing import Any
from pydantic import BaseModel, Field


class GeocodingSearchResponse(BaseModel):
    """Response payload for forward geocoding queries."""

    query: str
    results: list[dict[str, Any]] = Field(default_factory=list)
    count: int = 0
    meta: dict[str, Any]


class GeocodingReverseResponse(BaseModel):
    """Response payload for reverse geocoding queries."""

    latitude: float
    longitude: float
    result: dict[str, Any] | None = None
    meta: dict[str, Any]
