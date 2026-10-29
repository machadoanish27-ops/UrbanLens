import re
from typing import Any
from pymongo.database import Database

from app.core.cache import InMemoryTTLCache, build_cache_key, service_cache
from app.core.exceptions import ResourceNotFoundException
from app.core.logging import get_logger
from app.db.repositories.city import CityRepository
from app.db.repositories.university import UniversityRepository
from app.providers.places.base import BasePlacesProvider
from app.providers.places.overpass import OverpassPlacesProvider
from app.schemas.education import CityEducationResponse, InstitutionItem

logger = get_logger("services.education")


def get_city_search_terms(city_name: str) -> list[str]:
    """Return search terms including historical and colloquial aliases for university matching."""
    low = city_name.strip().lower()
    if "mumbai" in low or "bombay" in low:
        return ["mumbai", "bombay"]
    if "tokyo" in low:
        return ["tokyo"]
    if "london" in low:
        return ["london"]
    if "paris" in low:
        return ["paris"]
    if "new york" in low or "nyc" in low:
        return ["new york", "columbia", "nyu"]
    if "singapore" in low:
        return ["singapore"]
    if "dubai" in low:
        return ["dubai"]
    return [low]


def classify_institution_name(name: str) -> str:
    """Classify institutional category based on title keywords."""
    lower = name.lower()
    if any(k in lower for k in ("medical", "medicine", "health sciences", "dental", "nursing", "pharmacy")):
        return "Medical College"
    if any(k in lower for k in ("engineering", "technology", "polytechnic", "institute of tech")):
        return "Engineering & Technology"
    if any(k in lower for k in ("business", "management", "commerce", "economics")):
        return "Business School"
    if any(k in lower for k in ("law", "legal", "judicature")):
        return "Law School"
    if any(k in lower for k in ("art", "design", "music", "drama", "fine arts")):
        return "Arts & Design"
    if any(k in lower for k in ("school", "academy", "lyceum", "gymnasium")):
        return "School"
    if any(k in lower for k in ("college", "community college")):
        return "College"
    if any(k in lower for k in ("institute", "research institute", "centre")):
        return "Institute"
    return "University"


class EducationService:
    """Service providing multi-source education discovery with explicit provenance."""

    def __init__(
        self,
        database: Database,
        places_provider: BasePlacesProvider | None = None,
        cache: InMemoryTTLCache | None = service_cache,
    ) -> None:
        self.database = database
        self.city_repo = CityRepository(database)
        self.univ_repo = UniversityRepository(database)
        self.places_provider = places_provider or OverpassPlacesProvider()
        self.cache = cache

    async def get_city_education(
        self,
        city_id: str,
        institution_type: str | None = None,
        page: int = 1,
        page_size: int = 25,
        limit: int | None = None,
        offset: int | None = None,
    ) -> CityEducationResponse:
        """Discover educational institutions from canonical registry and OpenStreetMap POIs."""
        city = self.city_repo.get_by_city_id(city_id)
        if not city:
            # Check alias
            resolved = self.city_repo.resolve_alias_to_city_id(city_id)
            if resolved:
                city = self.city_repo.get_by_city_id(resolved)
        if not city:
            raise ResourceNotFoundException("city", city_id)

        city_name = city.get("name", "Unknown")
        country_iso2 = city.get("country_iso2")
        country_id = city.get("country_id")
        lat = city.get("latitude")
        lon = city.get("longitude")

        # Support limit and offset aliases
        if limit is not None:
            page_size = limit
        if offset is not None:
            start = offset
            page = (offset // page_size) + 1 if page_size > 0 else 1
            end = start + page_size
        else:
            start = (page - 1) * page_size
            end = start + page_size

        institutions: list[InstitutionItem] = []
        seen_names: set[str] = set()

        # 1. First fetch canonical institutions specifically matching city name or historical aliases
        search_terms = get_city_search_terms(city_name)
        regex_pattern = "|".join(re.escape(t) for t in search_terms)
        city_filters: dict[str, Any] = {
            "name": {"$regex": regex_pattern, "$options": "i"}
        }
        if country_iso2:
            city_filters["country_iso2"] = country_iso2.strip().upper()
        city_canonical = self.univ_repo.find_many(city_filters, sort=[("name", 1)])

        # 2. Broader canonical institutions for this country / regional context
        canonical_raw, total_canonical = self.univ_repo.get_universities_by_country(
            country_iso2=country_iso2,
            country_id=country_id,
            page=1,
            page_size=100,  # Grab up to 100 canonical institutions
        )

        # Merge city-specific matches first so they appear in top results
        combined_canonical = list(city_canonical)
        seen_ids = {u.get("university_id") for u in city_canonical if u.get("university_id")}
        for u in canonical_raw:
            uid = u.get("university_id")
            if uid and uid not in seen_ids:
                combined_canonical.append(u)
                seen_ids.add(uid)

        for u in combined_canonical:
            name = u.get("name", "").strip()
            if not name:
                continue
            norm_key = name.lower()
            if norm_key in seen_names:
                continue
            seen_names.add(norm_key)

            classified_type = classify_institution_name(name)
            website = u.get("website")
            is_valid_url = bool(website and str(website).startswith("http"))

            institutions.append(
                InstitutionItem(
                    institution_id=u.get("university_id", f"univ_{hash(name)}"),
                    name=name,
                    type=classified_type,
                    city=city_name,
                    country=city.get("country_iso3") or country_iso2,
                    country_iso2=country_iso2,
                    address=None,
                    latitude=None,
                    longitude=None,
                    distance_meters=None,
                    website=str(website).strip() if is_valid_url else None,
                    has_verified_website=is_valid_url,
                    source="World Universities Dataset (Canonical)",
                    source_url="https://github.com/Hipo/university-domains-list",
                    verified_at="2024",
                    provider="canonical_db",
                    status="canonical",
                )
            )

        canonical_count = total_canonical

        # 3. Query community-mapped POIs around city coordinates from OpenStreetMap
        community_count = 0
        if lat is not None and lon is not None:
            cache_key = build_cache_key("education_osm", lat=round(lat, 3), lon=round(lon, 3))
            osm_places = None
            if self.cache:
                osm_places = self.cache.get(cache_key)

            if osm_places is None:
                try:
                    # Query college and university amenities within 8km radius
                    res_col = await self.places_provider.get_places(
                        latitude=float(lat),
                        longitude=float(lon),
                        category="college",
                        radius=8000,
                        limit=25,
                    )
                    res_univ = await self.places_provider.get_places(
                        latitude=float(lat),
                        longitude=float(lon),
                        category="university",
                        radius=8000,
                        limit=25,
                    )
                    places_list = (res_col.data or []) + (res_univ.data or [])
                    osm_places = [p.model_dump() for p in places_list]
                    if self.cache:
                        self.cache.set(cache_key, osm_places, ttl_seconds=900.0)
                except Exception as exc:
                    logger.debug("Failed to fetch OSM education POIs: %s", exc)
                    osm_places = []

            for p in (osm_places or []):
                p_name = p.get("name", "").strip()
                if not p_name or "Unnamed" in p_name:
                    continue
                norm_key = p_name.lower()
                if norm_key in seen_names:
                    # Enrich coordinates/address if matching canonical institution
                    for inst in institutions:
                        if inst.name.lower() == norm_key:
                            inst.latitude = p.get("latitude")
                            inst.longitude = p.get("longitude")
                            inst.distance_meters = p.get("distance_meters")
                            inst.address = p.get("tags", {}).get("addr:street")
                    continue
                seen_names.add(norm_key)

                tags = p.get("tags", {})
                web = tags.get("website") or tags.get("contact:website")
                is_valid_url = bool(web and str(web).startswith("http"))
                amenity_val = p.get("amenity") or p.get("category", "")
                inst_type = "College" if "college" in amenity_val else ("University" if "university" in amenity_val else classify_institution_name(p_name))

                addr_parts = [
                    tags.get("addr:housenumber"),
                    tags.get("addr:street"),
                    tags.get("addr:city") or city_name,
                ]
                clean_addr = ", ".join([str(x) for x in addr_parts if x]) or None

                institutions.append(
                    InstitutionItem(
                        institution_id=f"osm_{p.get('place_id')}",
                        name=p_name,
                        type=inst_type,
                        city=city_name,
                        country=country_iso2,
                        country_iso2=country_iso2,
                        address=clean_addr,
                        latitude=p.get("latitude"),
                        longitude=p.get("longitude"),
                        distance_meters=p.get("distance_meters"),
                        website=str(web).strip() if is_valid_url else None,
                        has_verified_website=is_valid_url,
                        source="OpenStreetMap Contributors",
                        source_url="https://www.openstreetmap.org",
                        verified_at=None,
                        provider="openstreetmap",
                        status="community_mapped",
                    )
                )
                community_count += 1

        # Available types
        available_types = sorted(list(set(i.type for i in institutions)))

        # Filter by requested institution type
        filtered = institutions
        if institution_type and institution_type.strip():
            target_type = institution_type.strip().lower()
            filtered = [i for i in institutions if i.type.lower() == target_type]

        # Total count calculation: total canonical in dataset + community mapped
        if institution_type and institution_type.strip():
            if target_type == "university":
                total = total_canonical + sum(1 for i in institutions if i.status == "community_mapped" and i.type.lower() == "university")
            else:
                total = len(filtered)
        else:
            total = total_canonical + community_count

        # Pagination
        paged = filtered[start:end]
        displayed_count = len(paged)

        return CityEducationResponse(
            city_id=city_id,
            city_name=city_name,
            country_iso2=country_iso2,
            total=total,
            displayed_count=displayed_count,
            canonical_count=canonical_count,
            community_mapped_count=community_count,
            limit=page_size,
            offset=start,
            page=page,
            page_size=page_size,
            items=paged,
            institutions=paged,
            available_types=available_types,
            disclaimer=(
                f"Showing {displayed_count} of {total} indexed institutions for {city_name} from the canonical UrbanLens dataset "
                f"({canonical_count} canonical universities, {community_count} mapped colleges/schools). "
                "UrbanLens does not claim exhaustive coverage of all institutions."
            ),
            meta={
                "total": total,
                "displayed_count": displayed_count,
                "limit": page_size,
                "offset": start,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size if total > 0 else 1,
            },
        )

