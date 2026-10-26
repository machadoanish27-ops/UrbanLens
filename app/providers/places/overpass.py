"""OpenStreetMap Overpass POI and places provider implementation."""

import math
from typing import Any
import httpx

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


class OverpassPlacesProvider(BasePlacesProvider):
    """Controlled POI lookup adapter backed by OpenStreetMap Overpass."""

    def __init__(
        self,
        base_url: str | None = None,
        timeout: float | None = None,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self.base_url = (base_url or settings.OVERPASS_BASE_URL).rstrip("/")
        self.timeout = timeout or settings.PROVIDER_TIMEOUT_SECONDS
        self._external_client = client

    @property
    def provider_name(self) -> str:
        return "overpass"

    @property
    def source_info(self) -> str:
        return "https://overpass-api.de"

    async def get_places(
        self,
        latitude: float,
        longitude: float,
        category: str = "hospital",
        radius: int = 1500,
        limit: int = 10,
    ) -> ProviderResponse[list[NormalizedPlaceItem]]:
        """Query bounded POI elements near given coordinates."""
        clean_cat = category.strip().lower()
        if clean_cat not in ALLOWED_CATEGORIES:
            return ProviderResponse(
                meta=self.create_meta(
                    status=LiveStatus.UNAVAILABLE,
                    error_detail=f"Category '{category}' is not supported. Supported: {', '.join(sorted(ALLOWED_CATEGORIES))}",
                ),
                data=[],
            )

        # Enforce strict bounds to prevent uncontrolled broad-area queries
        clamped_radius = max(200, min(5000, radius))
        clamped_limit = max(1, min(25, limit))

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

        try:
            if self._external_client:
                response = await self._external_client.post(
                    self.base_url,
                    data={"data": query},
                    headers=headers,
                    timeout=self.timeout,
                )
            else:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        self.base_url,
                        data={"data": query},
                        headers=headers,
                        timeout=self.timeout,
                    )

            if response.status_code in (429, 502, 504):
                logger.warning("Overpass capacity/rate issue (HTTP %d).", response.status_code)
                return ProviderResponse(
                    meta=self.create_meta(
                        status=LiveStatus.UNAVAILABLE,
                        error_detail=f"Overpass API server is currently busy or rate-limited (HTTP {response.status_code}).",
                    ),
                    data=[],
                )

            if response.status_code != 200:
                logger.warning("Overpass HTTP %d: %s", response.status_code, response.text[:200])
                return ProviderResponse(
                    meta=self.create_meta(
                        status=LiveStatus.ERROR,
                        error_detail=f"Overpass returned HTTP {response.status_code}.",
                    ),
                    data=[],
                )

            payload = response.json()
            elements = payload.get("elements") or []

            items: list[NormalizedPlaceItem] = []
            for elem in elements:
                tags = elem.get("tags") or {}
                # Determine coordinate (direct for node, center for way)
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
                        tags={k: str(v) for k, v in tags.items() if k in {"brand", "operator", "opening_hours", "wheelchair", "website", "phone"}},
                    )
                )

            # Sort by distance
            items.sort(key=lambda x: x.distance_meters if x.distance_meters is not None else float("inf"))
            items = items[:clamped_limit]

            status = LiveStatus.FRESH if items else LiveStatus.UNAVAILABLE
            err = None if items else f"No places found for category '{clean_cat}' within {clamped_radius}m."

            return ProviderResponse(
                meta=self.create_meta(status=status, error_detail=err),
                data=items,
            )

        except httpx.TimeoutException:
            logger.warning("Overpass query timed out.")
            return ProviderResponse(
                meta=self.create_meta(status=LiveStatus.ERROR, error_detail="Overpass query timed out."),
                data=[],
            )
        except Exception as exc:
            logger.error("Overpass places error: %s", str(exc))
            return ProviderResponse(
                meta=self.create_meta(
                    status=LiveStatus.ERROR,
                    error_detail=f"Overpass communication failure: {str(exc)}",
                ),
                data=[],
            )
