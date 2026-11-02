"""Places and points of interest service layer."""

import asyncio
import time
from typing import Any
from pymongo.database import Database

from app.core.cache import InMemoryTTLCache, build_cache_key, service_cache
from app.core.logging import get_logger
from app.providers.places.base import BasePlacesProvider
from app.providers.places.overpass import OverpassPlacesProvider

logger = get_logger("services.places")


class PlacesService:
    """Service providing bounded POI search via replaceable places providers."""

    def __init__(
        self,
        database: Database | None = None,
        provider: BasePlacesProvider | None = None,
        cache: InMemoryTTLCache | None = service_cache,
    ) -> None:
        self.database = database
        self.provider = provider or OverpassPlacesProvider()
        self.cache = cache

    async def search_places(
        self,
        latitude: float,
        longitude: float,
        category: str = "hospital",
        radius: int = 1500,
        limit: int = 10,
    ) -> dict[str, Any]:
        """Search points of interest around coordinates for a specific category."""
        cache_key = build_cache_key(
            "places",
            lat=round(latitude, 4),
            lon=round(longitude, 4),
            cat=category.strip().lower(),
            rad=radius,
            lim=limit,
        )
        if self.cache:
            cached = self.cache.get(cache_key)
            if cached:
                cached_res = dict(cached)
                cached_res["meta"] = {**cached.get("meta", {}), "cached": True}
                return cached_res

        try:
            res = await asyncio.wait_for(
                self.provider.get_places(
                    latitude=latitude,
                    longitude=longitude,
                    category=category,
                    radius=radius,
                    limit=limit,
                ),
                timeout=3.0,
            )
        except (asyncio.TimeoutError, Exception) as exc:
            logger.warning("Places provider query timed out or failed for (%s, %s): %s", latitude, longitude, exc)
            if self.database is not None and category.strip().lower() in ("hospital", "healthcare", "clinic", "pharmacy"):
                try:
                    hf_col = self.database["healthcare_facilities"]
                    near_query: dict[str, Any] = {
                        "location": {
                            "$nearSphere": {
                                "$geometry": {
                                    "type": "Point",
                                    "coordinates": [float(longitude), float(latitude)],
                                },
                                "$maxDistance": radius,
                            }
                        }
                    }
                    if category.strip().lower() in ("hospital", "clinic", "pharmacy"):
                        near_query["facility_type"] = category.strip().lower()
                    kaggle_docs = list(hf_col.find(near_query).limit(limit))
                    if kaggle_docs:
                        places = []
                        for d in kaggle_docs:
                            d_lat = float(d.get("latitude", 0.0))
                            d_lon = float(d.get("longitude", 0.0))
                            places.append({
                                "place_id": str(d.get("healthcare_id") or d.get("_id")),
                                "name": d.get("name", "Healthcare Facility"),
                                "category": category,
                                "amenity": d.get("facility_type"),
                                "latitude": d_lat,
                                "longitude": d_lon,
                                "address": d.get("address"),
                                "distance_meters": d.get("city_match_distance_km", 0.0) * 1000 if d.get("city_match_distance_km") else None,
                                "tags": {
                                    "website": d.get("website"),
                                    "phone": d.get("phone"),
                                    "emergency": "yes" if d.get("emergency") else None,
                                    "source": "kaggle",
                                }
                            })
                        return {
                            "latitude": latitude,
                            "longitude": longitude,
                            "category": category,
                            "radius_meters": radius,
                            "places": places,
                            "count": len(places),
                            "meta": {
                                "source": "kaggle",
                                "status": "fresh",
                                "timestamp": time.time(),
                                "cached": False,
                            },
                        }
                except Exception as db_err:
                    logger.debug("Healthcare fallback query error: %s", db_err)

            return {
                "latitude": latitude,
                "longitude": longitude,
                "category": category,
                "radius_meters": radius,
                "places": [],
                "count": 0,
                "meta": {
                    "source": "overpass",
                    "status": "unavailable",
                    "timestamp": time.time(),
                    "cached": False,
                    "error_detail": f"Places lookup timed out: {exc}",
                },
            }

        places_list = [p.model_dump() for p in res.data] if res.data else []
        if not places_list and self.database is not None and category.strip().lower() in ("hospital", "healthcare", "clinic", "pharmacy"):
            try:
                hf_col = self.database["healthcare_facilities"]
                near_query: dict[str, Any] = {
                    "location": {
                        "$nearSphere": {
                            "$geometry": {
                                "type": "Point",
                                "coordinates": [float(longitude), float(latitude)],
                            },
                            "$maxDistance": radius,
                        }
                    }
                }
                if category.strip().lower() in ("hospital", "clinic", "pharmacy"):
                    near_query["facility_type"] = category.strip().lower()
                kaggle_docs = list(hf_col.find(near_query).limit(limit))
                for d in kaggle_docs:
                    d_lat = float(d.get("latitude", 0.0))
                    d_lon = float(d.get("longitude", 0.0))
                    places_list.append({
                        "place_id": str(d.get("healthcare_id") or d.get("_id")),
                        "name": d.get("name", "Healthcare Facility"),
                        "category": category,
                        "amenity": d.get("facility_type"),
                        "latitude": d_lat,
                        "longitude": d_lon,
                        "address": d.get("address"),
                        "distance_meters": d.get("city_match_distance_km", 0.0) * 1000 if d.get("city_match_distance_km") else None,
                        "tags": {
                            "website": d.get("website"),
                            "phone": d.get("phone"),
                            "emergency": "yes" if d.get("emergency") else None,
                            "source": "kaggle",
                        }
                    })
            except Exception as db_err:
                logger.debug("Healthcare fallback query error: %s", db_err)

        result = {
            "latitude": latitude,
            "longitude": longitude,
            "category": category,
            "radius_meters": radius,
            "places": places_list,
            "count": len(places_list),
            "meta": res.meta.model_dump() if res.data else {"source": "kaggle" if places_list else "overpass", "status": "fresh" if places_list else "unavailable", "timestamp": time.time(), "cached": False},
        }

        if res.is_successful and res.data and self.cache:
            self.cache.set(cache_key, result, ttl_seconds=600.0)

        return result
