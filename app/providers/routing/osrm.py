"""OSRM routing provider implementation."""

from typing import Any
import httpx

from app.core.config import settings
from app.core.logging import get_logger
from app.providers.base import LiveStatus, ProviderResponse
from app.providers.routing.base import (
    BaseRoutingProvider,
    NormalizedRoute,
)

logger = get_logger("providers.routing.osrm")


class OSRMRoutingProvider(BaseRoutingProvider):
    """Basic routing adapter backed by Project OSRM."""

    def __init__(
        self,
        base_url: str | None = None,
        timeout: float | None = None,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self.base_url = (base_url or settings.OSRM_BASE_URL).rstrip("/")
        self.timeout = timeout or settings.PROVIDER_TIMEOUT_SECONDS
        self._external_client = client

    @property
    def provider_name(self) -> str:
        return "osrm"

    @property
    def source_info(self) -> str:
        return "http://project-osrm.org"

    async def get_route(
        self,
        origin_lat: float,
        origin_lon: float,
        dest_lat: float,
        dest_lon: float,
        profile: str = "driving",
    ) -> ProviderResponse[NormalizedRoute]:
        """Calculate road network route using OSRM."""
        # Coordinates in OSRM are formatted as: {lon},{lat};{lon},{lat}
        coords_str = f"{round(origin_lon, 6)},{round(origin_lat, 6)};{round(dest_lon, 6)},{round(dest_lat, 6)}"
        endpoint = f"{self.base_url}/route/v1/{profile}/{coords_str}"
        params = {"overview": "false"}

        try:
            if self._external_client:
                response = await self._external_client.get(endpoint, params=params, timeout=self.timeout)
            else:
                async with httpx.AsyncClient() as client:
                    response = await client.get(endpoint, params=params, timeout=self.timeout)

            if response.status_code != 200:
                logger.warning("OSRM HTTP %d: %s", response.status_code, response.text[:200])
                return ProviderResponse(
                    meta=self.create_meta(
                        status=LiveStatus.ERROR,
                        error_detail=f"OSRM returned HTTP {response.status_code}.",
                    ),
                    data=None,
                )

            payload = response.json()
            code = payload.get("code")
            if code != "Ok":
                msg = payload.get("message", "Route calculation failed")
                return ProviderResponse(
                    meta=self.create_meta(
                        status=LiveStatus.UNAVAILABLE,
                        error_detail=f"OSRM code '{code}': {msg}",
                    ),
                    data=None,
                )

            routes = payload.get("routes") or []
            if not routes:
                return ProviderResponse(
                    meta=self.create_meta(
                        status=LiveStatus.UNAVAILABLE,
                        error_detail="No valid road routes found between the provided waypoints.",
                    ),
                    data=None,
                )

            primary_route = routes[0]
            dist_m = float(primary_route.get("distance", 0.0))
            dur_s = float(primary_route.get("duration", 0.0))

            normalized = NormalizedRoute(
                origin_lat=origin_lat,
                origin_lon=origin_lon,
                dest_lat=dest_lat,
                dest_lon=dest_lon,
                distance_meters=round(dist_m, 2),
                distance_km=round(dist_m / 1000.0, 2),
                duration_seconds=round(dur_s, 2),
                duration_minutes=round(dur_s / 60.0, 2),
                profile=profile,
            )

            return ProviderResponse(
                meta=self.create_meta(status=LiveStatus.FRESH),
                data=normalized,
            )

        except httpx.TimeoutException:
            logger.warning("OSRM route calculation timed out.")
            return ProviderResponse(
                meta=self.create_meta(status=LiveStatus.ERROR, error_detail="OSRM routing request timed out."),
                data=None,
            )
        except Exception as exc:
            logger.error("OSRM routing error: %s", str(exc))
            return ProviderResponse(
                meta=self.create_meta(
                    status=LiveStatus.ERROR,
                    error_detail=f"OSRM routing communication failure: {str(exc)}",
                ),
                data=None,
            )
