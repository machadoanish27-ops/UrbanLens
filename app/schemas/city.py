"""City response schemas."""

from typing import Any
from pydantic import BaseModel, Field


class CityAliasItem(BaseModel):
    """An alias or alternate naming for a city."""

    alias: str
    normalized_alias: str | None = None
    alias_source: str | None = None
    mapping_version: str | None = None


class CityProviderIdentityItem(BaseModel):
    """A cross-reference identity linking this city to an external provider."""

    provider: str
    provider_location_id: str | int
    provider_name_raw: str | None = None
    provider_country_code: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    match_method: str | None = None
    confidence: str | float | None = None
    status: str | None = None


class CityListItem(BaseModel):
    """City summary item for list and search results."""

    city_id: str
    worldcities_id: int | None = None
    name: str | None = None
    name_ascii: str | None = None
    country_id: str | None = None
    country_iso2: str | None = None
    country_iso3: str | None = None
    admin_name: str | None = None
    capital: str | None = None
    population: int | float | None = None
    latitude: float | None = None
    longitude: float | None = None


class PopulationDensityInfo(BaseModel):
    """Population density specification and provenance."""

    status: str = "unavailable"
    value: float | None = None
    unit: str = "people/km²"
    area_km2: float | None = None
    source: str | None = None
    level: str = "city"
    national_density_value: float | None = None
    national_density_period: int | None = None
    national_density_source: str | None = "country_metrics"


from app.schemas.country import CountryLanguageInfo


class CityCurrencyInfo(BaseModel):
    """Currency specification for a city's national context."""

    code: str
    symbol: str
    name: str


class CityDetail(CityListItem):
    """Detailed city representation including aliases and provider cross-references."""

    population_unavailable: bool | None = None
    geonames_id: int | str | None = None
    identity_status: str | None = None
    identity_confidence: str | float | None = None
    review_required: bool | None = None
    identity_relationship: str | None = None
    source_id: str | None = None
    mapping_version: str | None = None
    area_km2: float | None = None
    population_density: PopulationDensityInfo | None = None
    languages: CountryLanguageInfo | None = None
    currency: CityCurrencyInfo | None = None
    aliases: list[CityAliasItem] = Field(default_factory=list)
    provider_identities: list[CityProviderIdentityItem] = Field(default_factory=list)


class CityOverview(BaseModel):
    """Comprehensive city overview synthesizing core urban intelligence domains."""

    city: CityDetail
    weather_summary: dict[str, Any] | None = None
    air_quality_summary: dict[str, Any] | None = None
    cost_of_living_summary: dict[str, Any] | None = None
    universities_summary: dict[str, Any] | None = None
    country_summary: dict[str, Any] | None = None
