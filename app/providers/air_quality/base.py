"""Air quality provider base interface and normalized schemas."""

from abc import abstractmethod
from pydantic import BaseModel, Field

from app.providers.base import BaseProvider, ProviderResponse


class NormalizedPollutants(BaseModel):
    """Normalized concentrations for primary criteria air pollutants."""

    pm25: float | None = Field(default=None, description="Particulate Matter <= 2.5 µm (µg/m³)")
    pm10: float | None = Field(default=None, description="Particulate Matter <= 10 µm (µg/m³)")
    no2: float | None = Field(default=None, description="Nitrogen Dioxide (µg/m³ or ppm)")
    o3: float | None = Field(default=None, description="Ozone (µg/m³ or ppm)")
    so2: float | None = Field(default=None, description="Sulfur Dioxide (µg/m³ or ppm)")
    co: float | None = Field(default=None, description="Carbon Monoxide (µg/m³ or ppm)")


class NormalizedAirQuality(BaseModel):
    """Standardized air quality data payload preserving observation provenance."""

    latitude: float
    longitude: float
    location_name: str | None = None
    location_id: str | int | None = None
    distance_meters: float | None = None
    observed_at: str | None = None
    pollutants: NormalizedPollutants = Field(default_factory=NormalizedPollutants)
    available_pollutants: list[str] = Field(default_factory=list)
    provider: str | None = None
    status: str | None = None
    warning: str | None = None
    is_live: bool = False


class BaseAirQualityProvider(BaseProvider):
    """Abstract interface for live air quality providers."""

    @abstractmethod
    async def get_air_quality(
        self,
        latitude: float,
        longitude: float,
        radius: int = 25000,
    ) -> ProviderResponse[NormalizedAirQuality]:
        """Fetch live air quality measurements for coordinates within radius."""
        ...
