"""Healthcare discovery and medical facility schemas."""

from typing import Any
from pydantic import BaseModel, Field


class HealthcareFacilityItem(BaseModel):
    """Normalized medical facility with source provenance and verified contact data."""

    facility_id: str
    name: str
    type: str  # Hospital, Clinic, Dental Clinic, Pharmacy, Medical Center, Laboratory, Urgent Care
    amenity: str | None = None
    address: str | None = None
    latitude: float
    longitude: float
    distance_meters: float | None = None
    phone: str | None = None
    website: str | None = None
    has_verified_website: bool = False
    opening_hours: str | None = None
    emergency: bool | None = None
    source: str = "OpenStreetMap Contributors"
    provider: str = "openstreetmap"
    status: str = "community_mapped"
    verified_at: str | None = None


class CityHealthcareResponse(BaseModel):
    """Comprehensive healthcare discovery response with explicit provenance disclaimers."""

    city_id: str
    city_name: str
    total: int = 0
    facilities: list[HealthcareFacilityItem] = Field(default_factory=list)
    available_types: list[str] = Field(default_factory=list)
    disclaimer: str = (
        "Showing community-mapped healthcare locations from OpenStreetMap. "
        "Does not claim exhaustive coverage of all medical facilities in the municipality."
    )
    meta: dict[str, Any] = Field(default_factory=dict)
