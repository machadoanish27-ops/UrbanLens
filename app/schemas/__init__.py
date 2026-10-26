"""Schemas package."""

from app.schemas.air_quality import (
    CityAirQualityResponse,
    GlobalWeatherAqItem,
    LiveCityAirQualityResponse,
    WhoAqItem,
)
from app.schemas.city import (
    CityAliasItem,
    CityDetail,
    CityListItem,
    CityOverview,
    CityProviderIdentityItem,
)
from app.schemas.common import (
    ApiErrorDetail,
    ApiErrorResponse,
    ApiResponse,
    PaginationMeta,
    ProvenanceInfo,
    ResponseMeta,
)
from app.schemas.cost import CityCostOfLivingResponse, CostOfLivingMetricItem
from app.schemas.country import CountryDetail, CountryItem, CountryMetricItem, CountryMetricsResponse
from app.schemas.currency import CurrencyConversionResponse
from app.schemas.geocoding import GeocodingReverseResponse, GeocodingSearchResponse
from app.schemas.intelligence import (
    AgentCatalogItem,
    AgentResultSchema,
    IntelligenceQueryRequest,
    IntelligenceQueryResponse,
    SourceProvenanceSchema,
)
from app.schemas.places import PlacesSearchResponse
from app.schemas.routing import RouteResponse
from app.schemas.transit import TransitFeedResponse
from app.schemas.university import UniversityDetail, UniversityItem, UniversityRankingItem
from app.schemas.weather import (
    CityForecastResponse,
    CityWeatherResponse,
    LiveCityWeatherResponse,
    WeatherForecastItem,
    WeatherObservationItem,
)

__all__ = [
    "ApiResponse",
    "ApiErrorResponse",
    "ApiErrorDetail",
    "ResponseMeta",
    "PaginationMeta",
    "ProvenanceInfo",
    "CityListItem",
    "CityDetail",
    "CityAliasItem",
    "CityProviderIdentityItem",
    "CityOverview",
    "CountryItem",
    "CountryDetail",
    "CountryMetricItem",
    "CountryMetricsResponse",
    "WeatherObservationItem",
    "WeatherForecastItem",
    "CityWeatherResponse",
    "CityForecastResponse",
    "LiveCityWeatherResponse",
    "GlobalWeatherAqItem",
    "WhoAqItem",
    "CityAirQualityResponse",
    "LiveCityAirQualityResponse",
    "CostOfLivingMetricItem",
    "CityCostOfLivingResponse",
    "CurrencyConversionResponse",
    "GeocodingSearchResponse",
    "GeocodingReverseResponse",
    "PlacesSearchResponse",
    "RouteResponse",
    "TransitFeedResponse",
    "UniversityItem",
    "UniversityDetail",
    "UniversityRankingItem",
    "AgentCatalogItem",
    "AgentResultSchema",
    "SourceProvenanceSchema",
    "IntelligenceQueryRequest",
    "IntelligenceQueryResponse",
]
