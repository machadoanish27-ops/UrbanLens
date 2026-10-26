"""Nominatim OpenStreetMap geocoding provider implementation."""

from typing import Any
import httpx

from app.core.config import settings
from app.core.logging import get_logger
from app.providers.base import LiveStatus, ProviderResponse
from app.providers.geocoding.base import (
    BaseGeocodingProvider,
    NormalizedGeocodingItem,
)

logger = get_logger("providers.geocoding.nominatim")


class NominatimGeocodingProvider(BaseGeocodingProvider):
    """Replaceable geocoding adapter backed by OpenStreetMap Nominatim."""

    def __init__(
        self,
        base_url: str | None = None,
        user_agent: str | None = None,
        timeout: float | None = None,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self.base_url = (base_url or settings.NOMINATIM_BASE_URL).rstrip("/")
        self.user_agent = user_agent or settings.NOMINATIM_USER_AGENT
        self.timeout = timeout or settings.PROVIDER_TIMEOUT_SECONDS
        self._external_client = client

    @property
    def provider_name(self) -> str:
        return "nominatim"

    @property
    def source_info(self) -> str:
        return "https://nominatim.openstreetmap.org"

    def _headers(self) -> dict[str, str]:
        return {
            "User-Agent": self.user_agent,
            "Accept": "application/json",
        }

    async def search(
        self,
        query: str,
        limit: int = 5,
    ) -> ProviderResponse[list[NormalizedGeocodingItem]]:
        """Forward geocode a place or address query string."""
        clean_query = query.strip()
        if not clean_query:
            return ProviderResponse(
                meta=self.create_meta(
                    status=LiveStatus.UNAVAILABLE,
                    error_detail="Empty search query provided.",
                ),
                data=[],
            )

        clamped_limit = max(1, min(20, limit))
        endpoint = f"{self.base_url}/search"
        params = {
            "q": clean_query,
            "format": "jsonv2",
            "limit": clamped_limit,
            "addressdetails": 1,
        }

        try:
            if self._external_client:
                response = await self._external_client.get(
                    endpoint,
                    params=params,
                    headers=self._headers(),
                    timeout=self.timeout,
                )
            else:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        endpoint,
                        params=params,
                        headers=self._headers(),
                        timeout=self.timeout,
                    )

            if response.status_code == 429:
                logger.warning("Nominatim rate limit reached (HTTP 429).")
                return ProviderResponse(
                    meta=self.create_meta(
                        status=LiveStatus.UNAVAILABLE,
                        error_detail="Nominatim rate limit reached.",
                    ),
                    data=[],
                )

            if response.status_code != 200:
                logger.warning("Nominatim HTTP %d: %s", response.status_code, response.text[:200])
                return ProviderResponse(
                    meta=self.create_meta(
                        status=LiveStatus.ERROR,
                        error_detail=f"Nominatim returned HTTP {response.status_code}.",
                    ),
                    data=[],
                )

            raw_items = response.json()
            if not isinstance(raw_items, list):
                raw_items = []

            items = [self._normalize_item(item) for item in raw_items]
            status = LiveStatus.FRESH if items else LiveStatus.UNAVAILABLE
            err = None if items else f"No locations found for '{clean_query}'."

            return ProviderResponse(
                meta=self.create_meta(status=status, error_detail=err),
                data=items,
            )

        except httpx.TimeoutException:
            logger.warning("Nominatim search request timed out for '%s'", clean_query)
            return ProviderResponse(
                meta=self.create_meta(status=LiveStatus.ERROR, error_detail="Nominatim search timed out."),
                data=[],
            )
        except Exception as exc:
            logger.error("Nominatim search failed for '%s': %s", clean_query, str(exc))
            return ProviderResponse(
                meta=self.create_meta(
                    status=LiveStatus.ERROR,
                    error_detail=f"Nominatim communication error: {str(exc)}",
                ),
                data=[],
            )

    async def reverse(
        self,
        latitude: float,
        longitude: float,
    ) -> ProviderResponse[NormalizedGeocodingItem]:
        """Reverse geocode coordinates to location description."""
        endpoint = f"{self.base_url}/reverse"
        params = {
            "lat": round(latitude, 6),
            "lon": round(longitude, 6),
            "format": "jsonv2",
            "addressdetails": 1,
        }

        try:
            if self._external_client:
                response = await self._external_client.get(
                    endpoint,
                    params=params,
                    headers=self._headers(),
                    timeout=self.timeout,
                )
            else:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        endpoint,
                        params=params,
                        headers=self._headers(),
                        timeout=self.timeout,
                    )

            if response.status_code == 429:
                return ProviderResponse(
                    meta=self.create_meta(
                        status=LiveStatus.UNAVAILABLE,
                        error_detail="Nominatim rate limit reached.",
                    ),
                    data=None,
                )

            if response.status_code != 200:
                return ProviderResponse(
                    meta=self.create_meta(
                        status=LiveStatus.ERROR,
                        error_detail=f"Nominatim reverse geocoding returned HTTP {response.status_code}.",
                    ),
                    data=None,
                )

            payload = response.json()
            if not payload or "error" in payload:
                return ProviderResponse(
                    meta=self.create_meta(
                        status=LiveStatus.UNAVAILABLE,
                        error_detail=payload.get("error", "No address found for coordinates."),
                    ),
                    data=None,
                )

            item = self._normalize_item(payload)
            return ProviderResponse(
                meta=self.create_meta(status=LiveStatus.FRESH),
                data=item,
            )

        except httpx.TimeoutException:
            return ProviderResponse(
                meta=self.create_meta(status=LiveStatus.ERROR, error_detail="Nominatim reverse geocoding timed out."),
                data=None,
            )
        except Exception as exc:
            return ProviderResponse(
                meta=self.create_meta(
                    status=LiveStatus.ERROR,
                    error_detail=f"Nominatim reverse communication error: {str(exc)}",
                ),
                data=None,
            )

    def _normalize_item(self, raw: dict[str, Any]) -> NormalizedGeocodingItem:
        """Parse raw Nominatim result into NormalizedGeocodingItem."""
        bounding = raw.get("boundingbox")
        bbox: list[float] | None = None
        if isinstance(bounding, list) and len(bounding) == 4:
            try:
                bbox = [float(b) for b in bounding]
            except (ValueError, TypeError):
                bbox = None

        lat_val = float(raw.get("lat", 0.0))
        lon_val = float(raw.get("lon", 0.0))

        return NormalizedGeocodingItem(
            place_id=raw.get("place_id", ""),
            name=raw.get("name") or raw.get("display_name", "").split(",")[0],
            display_name=raw.get("display_name", ""),
            latitude=lat_val,
            longitude=lon_val,
            type=raw.get("type"),
            category=raw.get("category"),
            importance=float(raw.get("importance")) if raw.get("importance") is not None else None,
            boundingbox=bbox,
        )
