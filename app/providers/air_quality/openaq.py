"""OpenAQ live air quality provider implementation."""

from typing import Any
import httpx

from app.core.config import settings
from app.core.logging import get_logger
from app.providers.base import LiveStatus, ProviderResponse
from app.providers.air_quality.base import (
    BaseAirQualityProvider,
    NormalizedAirQuality,
    NormalizedPollutants,
)

logger = get_logger("providers.air_quality.openaq")

POLLUTANT_KEY_MAP: dict[str, str] = {
    "pm25": "pm25",
    "pm2.5": "pm25",
    "pm10": "pm10",
    "no2": "no2",
    "o3": "o3",
    "ozone": "o3",
    "so2": "so2",
    "co": "co",
}


class OpenAQAirQualityProvider(BaseAirQualityProvider):
    """Live air quality adapter backed by the OpenAQ API v3."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: float | None = None,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self.api_key = api_key if api_key is not None else settings.OPENAQ_API_KEY
        self.base_url = (base_url or settings.OPENAQ_BASE_URL).rstrip("/")
        self.timeout = timeout or settings.PROVIDER_TIMEOUT_SECONDS
        self._external_client = client

    @property
    def provider_name(self) -> str:
        return "openaq"

    @property
    def source_info(self) -> str:
        return "https://api.openaq.org"

    async def get_air_quality(
        self,
        latitude: float,
        longitude: float,
        radius: int = 25000,
    ) -> ProviderResponse[NormalizedAirQuality]:
        """Fetch live air quality measurements near coordinates from OpenAQ."""
        if not self.api_key or not self.api_key.strip():
            logger.info("OpenAQ API key is not configured in environment.")
            return ProviderResponse(
                meta=self.create_meta(
                    status=LiveStatus.UNAVAILABLE,
                    error_detail="OpenAQ API key is not configured (OPENAQ_API_KEY).",
                ),
                data=None,
            )

        endpoint = f"{self.base_url}/locations"
        params = {
            "coordinates": f"{round(latitude, 4)},{round(longitude, 4)}",
            "radius": max(1000, min(100000, radius)),
            "limit": 5,
        }
        headers = {
            "X-API-Key": self.api_key.strip(),
            "User-Agent": "UrbanLens/0.1.0",
        }

        try:
            if self._external_client:
                response = await self._external_client.get(
                    endpoint,
                    params=params,
                    headers=headers,
                    timeout=self.timeout,
                )
            else:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        endpoint,
                        params=params,
                        headers=headers,
                        timeout=self.timeout,
                    )

            if response.status_code in (401, 403):
                logger.warning("OpenAQ authentication failed (HTTP %d).", response.status_code)
                return ProviderResponse(
                    meta=self.create_meta(
                        status=LiveStatus.UNAVAILABLE,
                        error_detail="OpenAQ API key is invalid or unauthorized.",
                    ),
                    data=None,
                )

            if response.status_code == 429:
                logger.warning("OpenAQ rate limit exceeded (HTTP 429).")
                return ProviderResponse(
                    meta=self.create_meta(
                        status=LiveStatus.UNAVAILABLE,
                        error_detail="OpenAQ API rate limit exceeded.",
                    ),
                    data=None,
                )

            if response.status_code >= 500:
                logger.warning("OpenAQ server error (HTTP %d).", response.status_code)
                return ProviderResponse(
                    meta=self.create_meta(
                        status=LiveStatus.ERROR,
                        error_detail=f"OpenAQ server error ({response.status_code}).",
                    ),
                    data=None,
                )

            if response.status_code != 200:
                logger.warning("OpenAQ unexpected response (HTTP %d).", response.status_code)
                return ProviderResponse(
                    meta=self.create_meta(
                        status=LiveStatus.ERROR,
                        error_detail=f"OpenAQ returned HTTP {response.status_code}.",
                    ),
                    data=None,
                )

            payload = response.json()
            return self._normalize_response(latitude, longitude, payload)

        except httpx.TimeoutException:
            logger.warning("OpenAQ request timed out for (%.4f, %.4f)", latitude, longitude)
            return ProviderResponse(
                meta=self.create_meta(
                    status=LiveStatus.ERROR,
                    error_detail="OpenAQ request timed out.",
                ),
                data=None,
            )
        except Exception as exc:
            logger.error("OpenAQ communication error for (%.4f, %.4f): %s", latitude, longitude, str(exc))
            return ProviderResponse(
                meta=self.create_meta(
                    status=LiveStatus.ERROR,
                    error_detail=f"OpenAQ communication error: {str(exc)}",
                ),
                data=None,
            )

    def _normalize_response(
        self,
        latitude: float,
        longitude: float,
        payload: dict[str, Any],
    ) -> ProviderResponse[NormalizedAirQuality]:
        """Normalize raw OpenAQ JSON into standard UrbanLens air quality model."""
        results = payload.get("results") or []
        if not results:
            return ProviderResponse(
                meta=self.create_meta(
                    status=LiveStatus.UNAVAILABLE,
                    error_detail="No OpenAQ monitoring stations found within radius.",
                ),
                data=None,
            )

        # Select first matching station
        station = results[0]
        location_name = station.get("name") or station.get("locality")
        location_id = station.get("id")
        distance_meters = station.get("distance")

        pollutant_values: dict[str, float] = {}
        latest_timestamps: list[str] = []

        # OpenAQ v3 returns sensors list on location object
        sensors = station.get("sensors") or []
        for sensor in sensors:
            param_info = sensor.get("parameter") or {}
            param_name = str(param_info.get("name", "")).lower()
            normalized_key = POLLUTANT_KEY_MAP.get(param_name)
            if not normalized_key:
                continue

            latest_obj = sensor.get("latest") or {}
            val = latest_obj.get("value")
            if val is not None and normalized_key not in pollutant_values:
                try:
                    pollutant_values[normalized_key] = float(val)
                except (ValueError, TypeError):
                    pass

            dt = latest_obj.get("datetime")
            if dt:
                latest_timestamps.append(str(dt))

        # Check legacy or flat measurements structure if present
        measurements = station.get("measurements") or []
        for m in measurements:
            param_name = str(m.get("parameter", "")).lower()
            normalized_key = POLLUTANT_KEY_MAP.get(param_name)
            if not normalized_key:
                continue
            val = m.get("value")
            if val is not None and normalized_key not in pollutant_values:
                try:
                    pollutant_values[normalized_key] = float(val)
                except (ValueError, TypeError):
                    pass
            dt = m.get("lastUpdated") or m.get("date", {}).get("utc")
            if dt:
                latest_timestamps.append(str(dt))

        pollutants = NormalizedPollutants(
            pm25=pollutant_values.get("pm25"),
            pm10=pollutant_values.get("pm10"),
            no2=pollutant_values.get("no2"),
            o3=pollutant_values.get("o3"),
            so2=pollutant_values.get("so2"),
            co=pollutant_values.get("co"),
        )

        available = [k for k, v in pollutant_values.items() if v is not None]
        observed_at = max(latest_timestamps) if latest_timestamps else None

        normalized = NormalizedAirQuality(
            latitude=latitude,
            longitude=longitude,
            location_name=location_name,
            location_id=location_id,
            distance_meters=distance_meters,
            observed_at=observed_at,
            pollutants=pollutants,
            available_pollutants=available,
        )

        return ProviderResponse(
            meta=self.create_meta(
                status=LiveStatus.FRESH,
                observed_at=observed_at,
            ),
            data=normalized,
        )
