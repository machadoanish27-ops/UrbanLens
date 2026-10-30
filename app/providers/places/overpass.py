"""Resilient OpenStreetMap Overpass POI provider with multi-endpoint rotation, circuit cooldown, and stale cache fallback."""

from __future__ import annotations

import asyncio
import math
import time
from dataclasses import dataclass
from typing import Any
import httpx

from app.core.cache import build_cache_key, service_cache
from app.core.config import settings
from app.core.logging import get_logger
from app.providers.base import LiveStatus, ProviderResponse
from app.providers.places.base import (
    BasePlacesProvider,
    NormalizedPlaceItem,
)

logger = get_logger("providers.places.overpass")

ALLOWED_CATEGORIES: frozenset[str] = frozenset({
    "hospital",
    "clinic",
    "dentist",
    "doctors",
    "pharmacy",
    "school",
    "university",
    "college",
    "library",
    "bank",
    "atm",
    "restaurant",
    "cafe",
    "fast_food",
    "supermarket",
    "marketplace",
    "park",
    "bus_station",
    "train_station",
    "subway_entrance",
    "police",
    "fire_station",
    "place_of_worship",
})


def calculate_haversine_distance_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate great-circle distance between two coordinate pairs in meters."""
    radius_earth = 6371000.0  # Earth's radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return round(radius_earth * c, 1)


@dataclass
class EndpointHealth:
    """Tracks endpoint availability, consecutive failure streaks, and cooldown status."""

    url: str
    consecutive_failures: int = 0
    total_requests: int = 0
    total_failures: int = 0
    last_failure_time: float = 0.0
    last_success_time: float = 0.0

    def is_cooling_down(self, cooldown_seconds: float) -> bool:
        """Endpoint is in cooldown if it experienced >= 2 consecutive failures recently."""
        if self.consecutive_failures < 2:
            return False
        return (time.time() - self.last_failure_time) < cooldown_seconds

    def record_success(self) -> None:
        self.consecutive_failures = 0
        self.total_requests += 1
        self.last_success_time = time.time()

    def record_failure(self) -> None:
        self.consecutive_failures += 1
        self.total_requests += 1
        self.total_failures += 1
        self.last_failure_time = time.time()


class OverpassPlacesProvider(BasePlacesProvider):
    """Controlled POI lookup adapter backed by resilient OpenStreetMap Overpass mirrors."""

    def __init__(
        self,
        base_url: str | None = None,
        fallback_urls: list[str] | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
        cooldown_seconds: float | None = None,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        primary = (base_url or settings.OVERPASS_BASE_URL).rstrip("/")
        self.primary_url = primary
        self.fallback_urls = [
            u.rstrip("/")
            for u in (fallback_urls if fallback_urls is not None else settings.OVERPASS_FALLBACK_URLS)
            if u.rstrip("/") != primary
        ]
        self.endpoints = [self.primary_url] + self.fallback_urls
        self.timeout = timeout or settings.PROVIDER_TIMEOUT_SECONDS
        self.max_retries = max_retries if max_retries is not None else settings.OVERPASS_MAX_RETRIES
        self.cooldown_seconds = (
            cooldown_seconds if cooldown_seconds is not None else settings.OVERPASS_COOLDOWN_SECONDS
        )
        self._external_client = client

        # Endpoint health registry
        self._endpoint_health: dict[str, EndpointHealth] = {
            url: EndpointHealth(url=url) for url in self.endpoints
        }

    @property
    def provider_name(self) -> str:
        return "overpass"

    @property
    def source_info(self) -> str:
        return self.primary_url

    def get_health_diagnostics(self) -> dict[str, Any]:
        """Return operational health diagnostics across all Overpass endpoints."""
        endpoints_info = []
        for url in self.endpoints:
            h = self._endpoint_health.get(url, EndpointHealth(url=url))
            cooling = h.is_cooling_down(self.cooldown_seconds)
            endpoints_info.append({
                "url": url,
                "is_primary": url == self.primary_url,
                "consecutive_failures": h.consecutive_failures,
                "total_requests": h.total_requests,
                "total_failures": h.total_failures,
                "is_cooling_down": cooling,
                "status": "degraded" if cooling else ("healthy" if h.consecutive_failures == 0 else "recovering"),
            })

        healthy_count = sum(1 for e in endpoints_info if not e["is_cooling_down"])
        return {
            "total_endpoints": len(self.endpoints),
            "available_endpoints": healthy_count,
            "overall_status": "ok" if healthy_count > 0 else "all_cooling_down",
            "endpoints": endpoints_info,
        }

    def _get_candidate_endpoints(self) -> list[str]:
        """Return ordered list of endpoints, prioritizing non-cooling endpoints."""
        now = time.time()
        active = [
            u for u in self.endpoints
            if not self._endpoint_health[u].is_cooling_down(self.cooldown_seconds)
        ]
        # If all are in cooldown, reset and allow retry on all
        if not active:
            logger.warning("All Overpass endpoints in cooldown; attempting recovery on primary.")
            return self.endpoints[:]
        return active

    async def get_places(
        self,
        latitude: float,
        longitude: float,
        category: str = "hospital",
        radius: int = 1500,
        limit: int = 10,
    ) -> ProviderResponse[list[NormalizedPlaceItem]]:
        """Query bounded POI elements near coordinates with multi-mirror failover and stale cache recovery."""
        clean_cat = category.strip().lower()
        if clean_cat not in ALLOWED_CATEGORIES:
            return ProviderResponse(
                meta=self.create_meta(
                    status=LiveStatus.UNAVAILABLE,
                    error_detail=f"Category '{category}' is not supported. Supported: {', '.join(sorted(ALLOWED_CATEGORIES))}",
                ),
                data=[],
            )

        clamped_radius = max(200, min(5000, radius))
        clamped_limit = max(1, min(25, limit))

        # Build cache key for places
        cache_key = build_cache_key(
            "places",
            lat=round(latitude, 4),
            lon=round(longitude, 4),
            cat=clean_cat,
            rad=clamped_radius,
            lim=clamped_limit,
        )

        query = f"""[out:json][timeout:8];
(
  node["amenity"="{clean_cat}"](around:{clamped_radius},{latitude:.6f},{longitude:.6f});
  way["amenity"="{clean_cat}"](around:{clamped_radius},{latitude:.6f},{longitude:.6f});
);
out center {clamped_limit};"""

        headers = {
            "User-Agent": settings.NOMINATIM_USER_AGENT,
            "Accept": "application/json",
        }

        candidate_endpoints = self._get_candidate_endpoints()
        last_error_detail: str | None = None
        attempt_count = 0
        max_attempts = min(len(candidate_endpoints), self.max_retries + 1)
        # Bounded per-attempt timeout: 3.5s per mirror prevents lingering latency spikes
        attempt_timeout = min(self.timeout, 3.5)

        for endpoint in candidate_endpoints[:max_attempts]:
            attempt_count += 1
            health = self._endpoint_health.setdefault(endpoint, EndpointHealth(url=endpoint))
            try:
                if self._external_client:
                    response = await self._external_client.post(
                        endpoint,
                        data={"data": query},
                        headers=headers,
                        timeout=attempt_timeout,
                    )
                else:
                    async with httpx.AsyncClient() as client:
                        response = await client.post(
                            endpoint,
                            data={"data": query},
                            headers=headers,
                            timeout=attempt_timeout,
                        )

                if response.status_code in (429, 502, 504):
                    health.record_failure()
                    last_error_detail = f"Endpoint {endpoint} busy/rate-limited (HTTP {response.status_code})."
                    logger.warning("Overpass mirror %s returned %d. Rotating...", endpoint, response.status_code)
                    await asyncio.sleep(0.3)
                    continue

                if response.status_code != 200:
                    health.record_failure()
                    last_error_detail = f"Endpoint {endpoint} returned HTTP {response.status_code}."
                    logger.warning("Overpass mirror %s error %d. Rotating...", endpoint, response.status_code)
                    await asyncio.sleep(0.3)
                    continue

                payload = response.json()
                elements = payload.get("elements") or []

                items: list[NormalizedPlaceItem] = []
                for elem in elements:
                    tags = elem.get("tags") or {}
                    elem_lat = elem.get("lat")
                    elem_lon = elem.get("lon")
                    if elem_lat is None or elem_lon is None:
                        center = elem.get("center") or {}
                        elem_lat = center.get("lat")
                        elem_lon = center.get("lon")

                    if elem_lat is None or elem_lon is None:
                        continue

                    lat_f = float(elem_lat)
                    lon_f = float(elem_lon)
                    dist_m = calculate_haversine_distance_m(latitude, longitude, lat_f, lon_f)

                    name = tags.get("name") or tags.get("name:en") or f"Unnamed {clean_cat.capitalize()}"

                    items.append(
                        NormalizedPlaceItem(
                            place_id=str(elem.get("id", "")),
                            name=name,
                            category=clean_cat,
                            latitude=lat_f,
                            longitude=lon_f,
                            distance_meters=dist_m,
                            amenity=tags.get("amenity", clean_cat),
                            tags={
                                k: str(v)
                                for k, v in tags.items()
                                if k in {
                                    "brand", "operator", "opening_hours", "wheelchair", "website",
                                    "phone", "contact:website", "contact:phone", "emergency",
                                    "addr:street", "addr:city", "addr:housenumber",
                                }
                            },
                        )
                    )

                items.sort(key=lambda x: x.distance_meters if x.distance_meters is not None else float("inf"))
                items = items[:clamped_limit]

                # Successful live response
                health.record_success()
                status = LiveStatus.FRESH if items else LiveStatus.UNAVAILABLE
                err = None if items else f"No places found for category '{clean_cat}' within {clamped_radius}m."

                # Cache successful result
                if items:
                    serialized_items = [p.model_dump() for p in items]
                    service_cache.set(cache_key, serialized_items, ttl_seconds=1800.0)

                return ProviderResponse(
                    meta=self.create_meta(status=status, error_detail=err),
                    data=items,
                )

            except httpx.TimeoutException:
                health.record_failure()
                last_error_detail = f"Endpoint {endpoint} timed out after {self.timeout}s."
                logger.warning("Overpass endpoint %s timed out. Rotating to mirror...", endpoint)
                await asyncio.sleep(0.3)
                continue
            except Exception as exc:
                health.record_failure()
                last_error_detail = f"Endpoint {endpoint} failure: {str(exc)}"
                logger.warning("Overpass endpoint %s exception: %s. Rotating...", endpoint, exc)
                await asyncio.sleep(0.3)
                continue

        # All live endpoints exhausted -> check for stale/cached fallback
        cached_entry = service_cache.get_entry(cache_key, allow_stale=True)
        if cached_entry and cached_entry.value:
            logger.info("Serving stale/cached POIs for %s near (%f, %f)", clean_cat, latitude, longitude)
            stale_items = [NormalizedPlaceItem(**p) for p in cached_entry.value]
            meta = self.create_meta(
                status=LiveStatus.CACHED,
                error_detail=f"Live Overpass endpoints unavailable ({last_error_detail}); returning cached POIs ({cached_entry.age_seconds:.0f}s old).",
            )
            return ProviderResponse(meta=meta, data=stale_items)

        # Explicit honest unavailable
        return ProviderResponse(
            meta=self.create_meta(
                status=LiveStatus.UNAVAILABLE,
                error_detail=f"All Overpass mirrors unavailable and no cached POIs available: {last_error_detail}",
            ),
            data=[],
        )
