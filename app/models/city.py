from dataclasses import dataclass


@dataclass(frozen=True)
class CityIdentity:
    city_id: str
    name: str
    country_id: str | None = None
    country_iso2: str | None = None


@dataclass(frozen=True)
class ProviderLocationIdentity:
    city_id: str
    provider: str
    provider_location_id: str