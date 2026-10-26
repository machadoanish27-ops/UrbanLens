"""UrbanLens live intelligence providers module."""

from app.providers.base import (
    BaseProvider,
    LiveMetadata,
    LiveStatus,
    ProviderResponse,
)
from app.providers.weather import BaseWeatherProvider, OpenMeteoWeatherProvider
from app.providers.air_quality import BaseAirQualityProvider, OpenAQAirQualityProvider
from app.providers.currency import BaseCurrencyProvider, FrankfurterCurrencyProvider
from app.providers.geocoding import BaseGeocodingProvider, NominatimGeocodingProvider
from app.providers.routing import BaseRoutingProvider, OSRMRoutingProvider
from app.providers.places import BasePlacesProvider, OverpassPlacesProvider
from app.providers.transit import BaseTransitProvider, GTFSTransitProvider

__all__ = [
    "BaseProvider",
    "LiveMetadata",
    "LiveStatus",
    "ProviderResponse",
    "BaseWeatherProvider",
    "OpenMeteoWeatherProvider",
    "BaseAirQualityProvider",
    "OpenAQAirQualityProvider",
    "BaseCurrencyProvider",
    "FrankfurterCurrencyProvider",
    "BaseGeocodingProvider",
    "NominatimGeocodingProvider",
    "BaseRoutingProvider",
    "OSRMRoutingProvider",
    "BasePlacesProvider",
    "OverpassPlacesProvider",
    "BaseTransitProvider",
    "GTFSTransitProvider",
]
