"""Air quality service layer with live OpenAQ integration and dataset preservation."""

from typing import Any
from pymongo.database import Database

from app.core.cache import InMemoryTTLCache, build_cache_key, service_cache
from app.core.exceptions import ResourceNotFoundException
from app.core.logging import get_logger
from app.db.repositories.air_quality import AirQualityRepository
from app.db.repositories.city import CityRepository
from app.providers.air_quality.base import (
    BaseAirQualityProvider,
    NormalizedAirQuality,
    NormalizedPollutants,
)
from app.providers.air_quality.openaq import OpenAQAirQualityProvider
from app.providers.base import LiveMetadata, LiveStatus

logger = get_logger("services.air_quality")


class AirQualityService:
    """Service providing source-grounded air quality data without silently merging datasets."""

    def __init__(
        self,
        database: Database,
        provider: BaseAirQualityProvider | None = None,
        cache: InMemoryTTLCache | None = service_cache,
    ) -> None:
        self.database = database
        self.aq_repo = AirQualityRepository(database)
        self.city_repo = CityRepository(database)
        self.provider = provider or OpenAQAirQualityProvider()
        self.cache = cache

    def get_air_quality(self, city_id: str, limit: int = 10) -> dict[str, Any]:
        """Fetch both Global Weather and WHO datasets while maintaining dataset separation."""
        gw_records = self.aq_repo.get_global_weather_aq(city_id, limit=limit)
        who_records = self.aq_repo.get_who_aq(city_id, limit=limit)

        available_providers = []
        if gw_records:
            available_providers.append("GlobalWeather")
        if who_records:
            available_providers.append("WHO")

        return {
            "city_id": city_id,
            "global_weather": gw_records,
            "who_annual": who_records,
            "available_providers": available_providers,
        }

    async def get_live_air_quality(self, city_id: str, radius: int = 25000) -> dict[str, Any]:
        """Retrieve live air quality from OpenAQ or fall back to verified database observations.
        
        Preserves source timestamps and distinguishes live measurements from database baselines.
        """
        city = self.city_repo.get_by_city_id(city_id)
        if not city:
            raise ResourceNotFoundException("city", city_id)

        latitude = city.get("latitude")
        longitude = city.get("longitude")

        if latitude is None or longitude is None:
            return self._build_database_fallback(
                city_id=city_id,
                city_name=city.get("name"),
                latitude=0.0,
                longitude=0.0,
                reason="City lacks geographic coordinates for live station proximity matching.",
            )

        # Check cache for live air quality
        prov_name = getattr(self.provider, "provider_name", "air_quality")
        cache_key = build_cache_key("air_quality", provider=prov_name, city_id=city_id, radius=radius)
        if self.cache:
            cached = self.cache.get(cache_key)
            if cached:
                cached_res = dict(cached)
                cached_res["meta"] = {**cached.get("meta", {}), "cached": True}
                return cached_res

        # 1. Attempt live provider
        res = await self.provider.get_air_quality(
            latitude=float(latitude),
            longitude=float(longitude),
            radius=radius,
        )

        if res.is_successful and res.data:
            result = {
                "city_id": city_id,
                "city_name": city.get("name"),
                "latitude": float(latitude),
                "longitude": float(longitude),
                "air_quality": res.data.model_dump(),
                "meta": res.meta.model_dump(),
            }
            if self.cache:
                self.cache.set(cache_key, result, ttl_seconds=300.0)
            return result

        # 2. Fallback to MongoDB ground-truth observations
        return self._build_database_fallback(
            city_id=city_id,
            city_name=city.get("name"),
            latitude=float(latitude),
            longitude=float(longitude),
            reason=res.meta.error_detail or "Live air quality provider returned error status.",
        )

    def _build_database_fallback(
        self,
        city_id: str,
        city_name: str | None,
        latitude: float,
        longitude: float,
        reason: str,
    ) -> dict[str, Any]:
        """Fallback to Global Weather or WHO historical records, or return explicit UNAVAILABLE."""
        latest_gw = self.aq_repo.get_latest_global_weather_aq(city_id)
        if latest_gw:
            obs_dt = latest_gw.get("observed_at")
            pollutants = NormalizedPollutants(
                pm25=latest_gw.get("pm25"),
                pm10=latest_gw.get("pm10"),
                no2=latest_gw.get("no2"),
                so2=latest_gw.get("so2"),
                o3=latest_gw.get("o3"),
                co=latest_gw.get("co"),
            )
            available = [
                k for k in ["pm25", "pm10", "no2", "so2", "o3", "co"]
                if latest_gw.get(k) is not None
            ]
            normalized = NormalizedAirQuality(
                latitude=latitude,
                longitude=longitude,
                location_name="MongoDB Ground-Truth Observation",
                observed_at=str(obs_dt) if obs_dt else None,
                pollutants=pollutants,
                available_pollutants=available,
            )
            meta = LiveMetadata(
                provider="mongodb",
                source="MongoDB air_quality_observations_global_weather ground-truth fallback",
                status=LiveStatus.DATABASE,
                observed_at=str(obs_dt) if obs_dt else None,
                error_detail=f"Live provider fallback: {reason}",
            )
            return {
                "city_id": city_id,
                "city_name": city_name,
                "latitude": latitude,
                "longitude": longitude,
                "air_quality": normalized.model_dump(),
                "meta": meta.model_dump(),
            }

        latest_who = self.aq_repo.get_latest_who_aq(city_id)
        if latest_who:
            year_val = latest_who.get("year")
            pollutants = NormalizedPollutants(
                pm25=latest_who.get("pm25_annual_mean_ug_m3"),
                pm10=latest_who.get("pm10_annual_mean_ug_m3"),
            )
            available = [
                k for k in ["pm25", "pm10"]
                if getattr(pollutants, k) is not None
            ]
            normalized = NormalizedAirQuality(
                latitude=latitude,
                longitude=longitude,
                location_name=f"WHO Annual Urban AQ ({year_val})",
                observed_at=str(year_val) if year_val else None,
                pollutants=pollutants,
                available_pollutants=available,
            )
            meta = LiveMetadata(
                provider="mongodb",
                source="MongoDB air_quality_observations_who annual fallback",
                status=LiveStatus.DATABASE,
                observed_at=str(year_val) if year_val else None,
                error_detail=f"Live provider fallback: {reason}",
            )
            return {
                "city_id": city_id,
                "city_name": city_name,
                "latitude": latitude,
                "longitude": longitude,
                "air_quality": normalized.model_dump(),
                "meta": meta.model_dump(),
            }

        # Explicitly unavailable
        meta = LiveMetadata(
            provider=self.provider.provider_name,
            source=self.provider.source_info,
            status=LiveStatus.UNAVAILABLE,
            error_detail=f"Air quality data unavailable: {reason}",
        )
        return {
            "city_id": city_id,
            "city_name": city_name,
            "latitude": latitude,
            "longitude": longitude,
            "air_quality": None,
            "meta": meta.model_dump(),
        }
