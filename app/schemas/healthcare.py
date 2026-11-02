"""Healthcare discovery and medical facility schemas."""

from typing import Any
from pydantic import BaseModel, Field


class HealthcareFacilityItem(BaseModel):
    """Normalized medical facility with source provenance and verified contact data."""

    facility_id: str
    name: str
    name_original: str | None = None
    type: str  # Hospital, Clinic, Dental Clinic, Pharmacy, Medical Center, Laboratory, Urgent Care, Health Center
    facility_type: str | None = None
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
    source: str = "kaggle"
    source_dataset: str | None = None
    source_url: str | None = None
    provider: str = "kaggle"
    status: str = "verified_dataset"
    verified_at: str | None = None
    city_id: str | None = None
    city_name: str | None = None
    country: str | None = None
    city_match_method: str | None = None
    city_match_distance_km: float | None = None
    city_match_confidence: float | None = None
    specialties: list[str] = Field(default_factory=list)
    services: list[str] = Field(default_factory=list)
    data_quality: dict[str, Any] | None = None


class CityHealthcareResponse(BaseModel):
    """Comprehensive healthcare discovery response with explicit provenance disclaimers."""

    city_id: str
    city_name: str
    total: int = 0
    page: int = 1
    page_size: int = 50
    items: list[HealthcareFacilityItem] = Field(default_factory=list)
    facilities: list[HealthcareFacilityItem] = Field(default_factory=list)
    available_types: list[str] = Field(default_factory=list)
    source: str = "kaggle"
    timestamp: str | None = None
    provenance: dict[str, Any] = Field(default_factory=dict)
    disclaimer: str = (
        "Showing verified healthcare facilities sourced from Kaggle open datasets "
        "and mapped to UrbanLens canonical municipal coordinates."
    )
    meta: dict[str, Any] = Field(default_factory=dict)


class HealthcareDetailResponse(BaseModel):
    """Specific healthcare facility detail response."""

    facility: HealthcareFacilityItem
    source: str = "kaggle"
    provenance: dict[str, Any] = Field(default_factory=dict)


class HealthcareNearbyResponse(BaseModel):
    """Geospatial proximity healthcare discovery response."""

    latitude: float
    longitude: float
    radius_meters: int
    total: int
    page: int = 1
    page_size: int = 50
    items: list[HealthcareFacilityItem] = Field(default_factory=list)
    facilities: list[HealthcareFacilityItem] = Field(default_factory=list)
    source: str = "kaggle"
    provenance: dict[str, Any] = Field(default_factory=dict)
