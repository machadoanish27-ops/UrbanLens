"""Healthcare discovery service integrating Kaggle baseline data with optional live OSM enrichment."""

import asyncio
import datetime
import math
import re
import time
from typing import Any
from pymongo.database import Database

from app.core.cache import InMemoryTTLCache, build_cache_key, service_cache
from app.core.exceptions import ResourceNotFoundException
from app.core.logging import get_logger
from app.db.repositories.city import CityRepository
from app.providers.places.base import BasePlacesProvider
from app.providers.places.overpass import OverpassPlacesProvider
from app.schemas.healthcare import (
    CityHealthcareResponse,
    HealthcareDetailResponse,
    HealthcareFacilityItem,
    HealthcareNearbyResponse,
)

logger = get_logger("services.healthcare")

CATEGORY_TO_TYPE_MAP = {
    "hospital": "Hospital",
    "clinic": "Clinic",
    "doctors": "Medical Practice",
    "dentist": "Dental Clinic",
    "pharmacy": "Pharmacy",
    "health_center": "Health Center",
    "medical_center": "Medical Center",
    "diagnostic_lab": "Diagnostic Laboratory",
    "emergency_facility": "Emergency Facility",
    "rehabilitation_center": "Rehabilitation Center",
    "mental_health_facility": "Mental Health Facility",
    "maternity_facility": "Maternity Facility",
    "specialist_center": "Specialist Center",
    "other_healthcare": "Healthcare Facility",
}


def haversine_distance_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate haversine distance in meters between two coordinate points."""
    r = 6371000.0  # Earth radius in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return r * c


def doc_to_healthcare_item(doc: dict[str, Any], city_lat: float | None = None, city_lon: float | None = None) -> HealthcareFacilityItem:
    """Convert a MongoDB healthcare_facilities document to a HealthcareFacilityItem schema."""
    doc_lat = float(doc.get("latitude", 0.0))
    doc_lon = float(doc.get("longitude", 0.0))

    dist_meters = None
    if city_lat is not None and city_lon is not None:
        dist_meters = round(haversine_distance_meters(city_lat, city_lon, doc_lat, doc_lon), 1)

    ftype = str(doc.get("facility_type") or "hospital").lower().strip()
    display_type = CATEGORY_TO_TYPE_MAP.get(ftype, ftype.replace("_", " ").title())

    return HealthcareFacilityItem(
        facility_id=str(doc.get("healthcare_id") or doc.get("_id")),
        name=doc.get("name", "Unknown Facility"),
        name_original=doc.get("name_original"),
        type=display_type,
        facility_type=ftype,
        amenity=ftype,
        address=doc.get("address"),
        latitude=doc_lat,
        longitude=doc_lon,
        distance_meters=dist_meters,
        phone=doc.get("phone"),
        website=doc.get("website"),
        has_verified_website=bool(doc.get("website")),
        opening_hours=doc.get("opening_hours"),
        emergency=doc.get("emergency"),
        source=f"Kaggle - {doc.get('source_dataset', 'Verified Kaggle Dataset')}",
        source_dataset=doc.get("source_dataset"),
        source_url=doc.get("source_url"),
        provider="kaggle",
        status="verified_dataset",
        verified_at=doc.get("verified_at"),
        city_id=doc.get("city_id"),
        city_name=doc.get("city_name"),
        country=doc.get("country"),
        city_match_method=doc.get("city_match_method"),
        city_match_distance_km=doc.get("city_match_distance_km"),
        city_match_confidence=doc.get("city_match_confidence"),
        specialties=doc.get("specialties", []),
        services=doc.get("services", []),
        data_quality=doc.get("data_quality"),
    )


class HealthcareService:
    """Service providing bounded, honest healthcare facility discovery backed by Kaggle dataset in MongoDB."""

    def __init__(
        self,
        database: Database,
        places_provider: BasePlacesProvider | None = None,
        cache: InMemoryTTLCache | None = service_cache,
    ) -> None:
        self.database = database
        self.city_repo = CityRepository(database)
        self.places_provider = places_provider or OverpassPlacesProvider()
        self.cache = cache
        self.collection = database["healthcare_facilities"]

    async def get_city_healthcare(
        self,
        city_id: str,
        category: str | None = None,
        search: str | None = None,
        page: int = 1,
        page_size: int = 50,
        radius: int = 25000,
        limit: int | None = None,
    ) -> CityHealthcareResponse:
        """Discover healthcare facilities for a canonical city using Kaggle MongoDB baseline + optional OSM enrichment."""
        effective_limit = limit if limit is not None else page_size

        city = self.city_repo.get_by_city_id(city_id)
        if not city:
            resolved = self.city_repo.resolve_alias_to_city_id(city_id)
            if resolved:
                city = self.city_repo.get_by_city_id(resolved)
        if not city:
            raise ResourceNotFoundException("city", city_id)

        canonical_city_id = city.get("city_id", city_id)
        city_name = city.get("name", "Unknown")
        city_lat = city.get("latitude")
        city_lon = city.get("longitude")

        # Cache check
        cache_key = build_cache_key(
            "healthcare_v2",
            cid=canonical_city_id,
            cat=category or "all",
            srch=search or "",
            p=page,
            ps=effective_limit,
            rad=radius,
        )
        if self.cache:
            cached = self.cache.get(cache_key)
            if cached:
                return CityHealthcareResponse(**cached)

        # 1. Build MongoDB query
        query: dict[str, Any] = {"city_id": canonical_city_id}

        if category and category.strip().lower() != "all":
            clean_cat = category.strip().lower()
            if clean_cat in CATEGORY_TO_TYPE_MAP:
                query["facility_type"] = clean_cat
            elif clean_cat in ("hospital", "hospitals"):
                query["facility_type"] = "hospital"
            elif clean_cat in ("clinic", "clinics"):
                query["facility_type"] = "clinic"
            elif clean_cat in ("pharmacy", "pharmacies"):
                query["facility_type"] = "pharmacy"
            elif clean_cat in ("health_center", "health centers"):
                query["facility_type"] = "health_center"
            else:
                query["facility_type"] = {"$regex": f"^{re.escape(clean_cat)}", "$options": "i"}

        if search and search.strip():
            query["name"] = {"$regex": re.escape(search.strip()), "$options": "i"}

        # Check count for direct city_id match
        total_in_city = self.collection.count_documents(query)
        items: list[HealthcareFacilityItem] = []

        if total_in_city > 0:
            skip = max(0, (page - 1) * effective_limit)
            cursor = (
                self.collection.find(query)
                .skip(skip)
                .limit(effective_limit)
            )
            raw_docs = list(cursor)
            items = [doc_to_healthcare_item(d, city_lat, city_lon) for d in raw_docs]

        # For cities like London where borough division leaves center with < 50 items,
        # supplement with proximity search up to radius meters within same country
        if len(items) < effective_limit and city_lat is not None and city_lon is not None and radius > 0:
            existing_ids = {it.facility_id for it in items}
            country_iso2 = city.get("country_iso2") or city.get("country_id", "").replace("country_", "")

            geo_query: dict[str, Any] = {
                "location": {
                    "$nearSphere": {
                        "$geometry": {
                            "type": "Point",
                            "coordinates": [float(city_lon), float(city_lat)],
                        },
                        "$maxDistance": radius,
                    }
                }
            }
            if "facility_type" in query:
                geo_query["facility_type"] = query["facility_type"]
            if "name" in query:
                geo_query["name"] = query["name"]

            proximity_cursor = self.collection.find(geo_query).limit(effective_limit * 2)
            for d in proximity_cursor:
                hid = str(d.get("healthcare_id") or d.get("_id"))
                if hid not in existing_ids:
                    existing_ids.add(hid)
                    items.append(doc_to_healthcare_item(d, city_lat, city_lon))
                    if len(items) >= effective_limit:
                        break
            total_in_city = max(total_in_city, len(existing_ids))

        # Sort by distance
        items.sort(key=lambda x: x.distance_meters if x.distance_meters is not None else float("inf"))

        # Available types
        available_types = sorted(list(set(it.type for it in items if it.type)))

        # 2. Live OSM Provider query (Phase 15: live enrichment)
        if city_lat is not None and city_lon is not None:
            categories_to_query = ["hospital", "clinic", "pharmacy", "dentist"]
            if category and category.strip().lower() in ("hospital", "clinic", "dentist", "pharmacy"):
                categories_to_query = [category.strip().lower()]

            raw_places = []
            tasks = [
                self.places_provider.get_places(
                    latitude=float(city_lat),
                    longitude=float(city_lon),
                    category=cat,
                    radius=min(radius, 5000),
                    limit=max(5, effective_limit // len(categories_to_query) + 5),
                )
                for cat in categories_to_query
            ]
            try:
                results = await asyncio.wait_for(
                    asyncio.gather(*tasks, return_exceptions=True),
                    timeout=2.0,
                )
                for r in results:
                    if not isinstance(r, Exception) and r and r.is_successful and r.data:
                        raw_places.extend(r.data)
            except Exception as exc:
                logger.debug("Live OSM provider bounded timeout for %s: %s", city_name, exc)

            existing_names = {it.name.lower() for it in items}
            for p in raw_places:
                p_name = p.name.strip()
                if p_name.lower() in existing_names:
                    continue
                existing_names.add(p_name.lower())

                tags = p.tags or {}
                web = tags.get("website") or tags.get("contact:website")
                is_valid_url = bool(web and str(web).startswith("http"))
                phone = tags.get("phone") or tags.get("contact:phone")
                emergency_val = tags.get("emergency") == "yes"

                addr_parts = [
                    tags.get("addr:housenumber"),
                    tags.get("addr:street"),
                    tags.get("addr:city") or city_name,
                ]
                clean_addr = ", ".join([str(x) for x in addr_parts if x]) or None

                inst_type = p.category.title() if p.category else "Medical Facility"
                if p.category == "dentist":
                    inst_type = "Dental Clinic"

                items.append(
                    HealthcareFacilityItem(
                        facility_id=str(p.place_id),
                        name=p_name,
                        name_original=p_name,
                        type=inst_type,
                        facility_type=p.category,
                        amenity=p.amenity,
                        address=clean_addr,
                        latitude=p.latitude,
                        longitude=p.longitude,
                        distance_meters=p.distance_meters,
                        phone=str(phone).strip() if phone else None,
                        website=str(web).strip() if is_valid_url else None,
                        has_verified_website=is_valid_url,
                        emergency=emergency_val,
                        source="OpenStreetMap Contributors",
                        provider="openstreetmap",
                        status="community_mapped",
                    )
                )

        # Sort by distance
        items.sort(key=lambda x: x.distance_meters if x.distance_meters is not None else float("inf"))
        items = items[:effective_limit]
        available_types = sorted(list(set(it.type for it in items if it.type)))
        total_found = max(total_in_city, len(items))

        # Build final response
        is_fresh = len(items) > 0
        disclaimer = (
            f"Showing {len(items)} verified healthcare facilities for {city_name} from Kaggle open datasets and OpenStreetMap. "
            "UrbanLens does not claim exhaustive coverage of all medical facilities in the municipality."
            if is_fresh
            else f"No verified healthcare facilities found for {city_name} in indexed Kaggle datasets or live municipal registry. "
                 "UrbanLens does not claim exhaustive coverage of all medical facilities in the municipality."
        )

        response = CityHealthcareResponse(
            city_id=canonical_city_id,
            city_name=city_name,
            total=total_found,
            page=page,
            page_size=effective_limit,
            items=items,
            facilities=items,
            available_types=available_types,
            source="kaggle" if any(it.provider == "kaggle" for it in items) else ("openstreetmap" if items else "none"),
            timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            provenance={
                "source": "Kaggle",
                "dataset": "UrbanLens Kaggle Healthcare Facilities Corpus",
                "license": "Public Domain / Open Government Data / ODC-By",
                "facility_count_retrieved": len(items),
            },
            disclaimer=disclaimer,
            meta={
                "radius_meters": radius,
                "status": "fresh" if is_fresh else "unavailable",
                "verified_facility_count": len(items),
            },
        )

        if self.cache and is_fresh:
            self.cache.set(cache_key, response.model_dump(), ttl_seconds=600.0)

        return response

    async def get_facility_by_id(self, city_id: str, healthcare_id: str) -> HealthcareDetailResponse:
        """Retrieve a specific healthcare facility by unique healthcare_id."""
        doc = self.collection.find_one({"healthcare_id": healthcare_id})
        if not doc:
            raise ResourceNotFoundException("healthcare_facility", healthcare_id)

        city = self.city_repo.get_by_city_id(doc.get("city_id") or city_id)
        city_lat = city.get("latitude") if city else None
        city_lon = city.get("longitude") if city else None

        item = doc_to_healthcare_item(doc, city_lat, city_lon)
        return HealthcareDetailResponse(
            facility=item,
            source=doc.get("source", "kaggle"),
            provenance={
                "source": "Kaggle",
                "dataset": doc.get("source_dataset", "UrbanLens Kaggle Healthcare Corpus"),
                "source_url": doc.get("source_url"),
                "verified_at": doc.get("verified_at"),
            },
        )

    async def get_nearby_facilities(
        self,
        latitude: float,
        longitude: float,
        radius: int = 10000,
        page: int = 1,
        page_size: int = 50,
        category: str | None = None,
    ) -> HealthcareNearbyResponse:
        """Geospatial proximity search across all healthcare facilities in MongoDB."""
        geo_query: dict[str, Any] = {
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
        if category and category.strip().lower() != "all":
            clean_cat = category.strip().lower()
            geo_query["facility_type"] = CATEGORY_TO_TYPE_MAP.get(clean_cat, clean_cat).lower()

        skip = max(0, (page - 1) * page_size)
        cursor = self.collection.find(geo_query).skip(skip).limit(page_size)
        raw_docs = list(cursor)
        items = [doc_to_healthcare_item(d, latitude, longitude) for d in raw_docs]

        return HealthcareNearbyResponse(
            latitude=latitude,
            longitude=longitude,
            radius_meters=radius,
            total=len(items),
            page=page,
            page_size=page_size,
            items=items,
            facilities=items,
            source="kaggle",
            provenance={
                "source": "Kaggle",
                "dataset": "UrbanLens Kaggle Healthcare Facilities Corpus",
            },
        )
