"""Schemas package."""

from app.schemas.air_quality import CityAirQualityResponse, GlobalWeatherAqItem, WhoAqItem
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
from app.schemas.intelligence import (
    AgentCatalogItem,
    AgentResultSchema,
    IntelligenceQueryRequest,
    IntelligenceQueryResponse,
    SourceProvenanceSchema,
)
from app.schemas.university import UniversityDetail, UniversityItem, UniversityRankingItem
from app.schemas.weather import (
    CityForecastResponse,
    CityWeatherResponse,
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
    "GlobalWeatherAqItem",
    "WhoAqItem",
    "CityAirQualityResponse",
    "CostOfLivingMetricItem",
    "CityCostOfLivingResponse",
    "UniversityItem",
    "UniversityDetail",
    "UniversityRankingItem",
    "AgentCatalogItem",
    "AgentResultSchema",
    "SourceProvenanceSchema",
    "IntelligenceQueryRequest",
    "IntelligenceQueryResponse",
]
