"""Education discovery and institutional classification schemas."""

from typing import Any
from pydantic import BaseModel, Field


class InstitutionItem(BaseModel):
    """Normalized educational institution with strict source and website provenance."""

    institution_id: str
    name: str
    type: str  # University, College, Institute, School, Medical College, Engineering College, etc.
    city: str | None = None
    country: str | None = None
    country_iso2: str | None = None
    address: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    distance_meters: float | None = None
    website: str | None = None
    has_verified_website: bool = False
    source: str = "World Universities Dataset (Canonical)"
    source_url: str | None = None
    verified_at: str | None = None
    provider: str = "canonical_db"  # canonical_db | openstreetmap
    status: str = "canonical"  # canonical | community_mapped


class CityEducationResponse(BaseModel):
    """Comprehensive education discovery response with provenance disclaimers."""

    city_id: str
    city_name: str
    country_iso2: str | None = None
    total: int = 0
    displayed_count: int = 0
    canonical_count: int = 0
    community_mapped_count: int = 0
    limit: int = 25
    offset: int = 0
    page: int = 1
    page_size: int = 25
    items: list[InstitutionItem] = Field(default_factory=list)
    institutions: list[InstitutionItem] = Field(default_factory=list)
    available_types: list[str] = Field(default_factory=list)
    disclaimer: str = (
        "Showing indexed institutions from the canonical UrbanLens dataset and mapped locations from OpenStreetMap. "
        "Does not claim exhaustive coverage of all institutions in the municipality."
    )
    meta: dict[str, Any] = Field(default_factory=dict)
