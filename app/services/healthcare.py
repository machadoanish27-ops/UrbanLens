"""Healthcare discovery service providing verified and mapped healthcare locations."""

from typing import Any
from pymongo.database import Database

from app.core.cache import InMemoryTTLCache, build_cache_key, service_cache
from app.core.exceptions import ResourceNotFoundException
from app.core.logging import get_logger
from app.db.repositories.city import CityRepository
from app.providers.places.base import BasePlacesProvider
from app.providers.places.overpass import OverpassPlacesProvider
from app.schemas.healthcare import CityHealthcareResponse, HealthcareFacilityItem

logger = get_logger("services.healthcare")

CATEGORY_TO_TYPE_MAP = {
    "hospital": "Hospital",
    "clinic": "Clinic",
    "doctors": "Medical Practice",
    "dentist": "Dental Clinic",
    "pharmacy": "Pharmacy",
}


def classify_healthcare_facility(name: str, amenity: str | None) -> str:
    """Classify medical facility type from amenity tag and name keywords."""
    amenity_clean = (amenity or "").lower()
    name_clean = name.lower()

    if "dentist" in amenity_clean or any(k in name_clean for k in ("dental", "dentist", "dentistry", "orthodontic")):
        return "Dental Clinic"
    if "pharmacy" in amenity_clean or any(k in name_clean for k in ("pharmacy", "chemist", "drugstore", "apotheke")):
        return "Pharmacy"
    if "hospital" in amenity_clean or any(k in name_clean for k in ("hospital", "infirmary", "medical center", "krankenhaus")):
        return "Hospital"
    if any(k in name_clean for k in ("laboratory", "diagnostic", "pathology", "imaging", "mri", "x-ray")):
        return "Diagnostic Laboratory"
    if any(k in name_clean for k in ("mental", "psychiatry", "psychological", "counseling")):
        return "Mental Health Facility"
    if any(k in name_clean for k in ("urgent care", "walk-in", "emergency clinic")):
        return "Urgent Care"
    if "clinic" in amenity_clean or "doctors" in amenity_clean or "clinic" in name_clean:
        return "Clinic"

    return CATEGORY_TO_TYPE_MAP.get(amenity_clean, "Medical Facility")


class HealthcareService:
    """Service providing bounded, honest healthcare POI discovery."""

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

    async def get_city_healthcare(
        self,
        city_id: str,
        category: str | None = None,
        radius: int = 5000,
        limit: int = 30,
    ) -> CityHealthcareResponse:
        """Discover healthcare facilities near city coordinates without fabricating missing data."""
        city = self.city_repo.get_by_city_id(city_id)
        if not city:
            resolved = self.city_repo.resolve_alias_to_city_id(city_id)
            if resolved:
                city = self.city_repo.get_by_city_id(resolved)
        if not city:
            raise ResourceNotFoundException("city", city_id)

        city_name = city.get("name", "Unknown")
        lat = city.get("latitude")
        lon = city.get("longitude")

        if lat is None or lon is None:
            return CityHealthcareResponse(
                city_id=city_id,
                city_name=city_name,
                total=0,
                facilities=[],
                available_types=[],
                disclaimer=f"Geographic coordinates unavailable for {city_name}. Cannot query proximity healthcare facilities.",
                meta={"radius_meters": radius, "status": "unavailable"},
            )

        cache_key = build_cache_key(
            "healthcare",
            lat=round(lat, 3),
            lon=round(lon, 3),
            cat=category or "all",
            rad=radius,
        )

        cached = self.cache.get(cache_key) if self.cache else None
        if cached:
            return CityHealthcareResponse(**cached)

        # Categories to query based on parameter
        categories_to_query = ["hospital", "clinic", "dentist", "pharmacy"]
        if category and category.strip().lower() in ("hospital", "clinic", "dentist", "pharmacy", "doctors"):
            categories_to_query = [category.strip().lower()]

        raw_places = []
        for cat in categories_to_query:
            try:
                res = await self.places_provider.get_places(
                    latitude=float(lat),
                    longitude=float(lon),
                    category=cat,
                    radius=radius,
                    limit=limit // len(categories_to_query) + 5,
                )
                if res.is_successful and res.data:
                    raw_places.extend(res.data)
            except Exception as exc:
                logger.debug("Failed querying healthcare cat %s: %s", cat, exc)

        facilities: list[HealthcareFacilityItem] = []
        seen_ids: set[str] = set()

        for p in raw_places:
            p_id = str(p.place_id)
            if p_id in seen_ids:
                continue
            seen_ids.add(p_id)

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

            inst_type = classify_healthcare_facility(p.name, p.amenity)

            facilities.append(
                HealthcareFacilityItem(
                    facility_id=p_id,
                    name=p.name,
                    type=inst_type,
                    amenity=p.amenity,
                    address=clean_addr,
                    latitude=p.latitude,
                    longitude=p.longitude,
                    distance_meters=p.distance_meters,
                    phone=str(phone).strip() if phone else None,
                    website=str(web).strip() if is_valid_url else None,
                    has_verified_website=is_valid_url,
                    opening_hours=tags.get("opening_hours"),
                    emergency=emergency_val,
                    source="OpenStreetMap Contributors",
                    provider="openstreetmap",
                    status="community_mapped",
                    verified_at=None,
                )
            )

        # Sort by distance
        facilities.sort(key=lambda x: x.distance_meters if x.distance_meters is not None else float("inf"))
        facilities = facilities[:limit]

        available_types = sorted(list(set(f.type for f in facilities)))
        total_found = len(facilities)

        response = CityHealthcareResponse(
            city_id=city_id,
            city_name=city_name,
            total=total_found,
            facilities=facilities,
            available_types=available_types,
            disclaimer=(
                f"Showing {total_found} community-mapped healthcare locations for {city_name} from OpenStreetMap. "
                "UrbanLens does not claim exhaustive coverage of all medical providers in the municipality."
            ),
            meta={"radius_meters": radius, "status": "fresh" if total_found > 0 else "unavailable"},
        )

        if self.cache and total_found > 0:
            self.cache.set(cache_key, response.model_dump(), ttl_seconds=900.0)

        return response
