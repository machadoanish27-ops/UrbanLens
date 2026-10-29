"""Global knowledge taxonomy, source authority hierarchy, and freshness policies for UrbanLens RAG."""

from datetime import datetime, timezone
from enum import StrEnum
from typing import Any


class KnowledgeCategory(StrEnum):
    """Recognized categories for knowledge documents and evidence."""

    IMMIGRATION = "immigration"
    GOVERNMENT = "government"
    TRANSPORT = "transport"
    HEALTHCARE = "healthcare"
    EDUCATION = "education"
    HOUSING = "housing"
    SAFETY = "safety"
    CULTURE = "culture"
    LIFESTYLE = "lifestyle"
    CULTURE_LIFESTYLE = "culture_lifestyle"
    ENVIRONMENT = "environment"
    CITY_INFORMATION = "city_information"
    RELOCATION = "relocation"  # Preserved for Phase 5 backward compatibility


class KnowledgeScope(StrEnum):
    """Geographic applicability scope of a knowledge document or evidence."""

    GLOBAL = "global"
    COUNTRY = "country"
    REGION = "region"
    CITY = "city"


class AuthorityTier(StrEnum):
    """Source authority classification hierarchy."""

    TIER_1_OFFICIAL = "tier_1_official"
    TIER_2_INTERGOVERNMENTAL = "tier_2_intergovernmental"
    TIER_3_SECONDARY = "tier_3_secondary"
    TIER_4_COMMUNITY = "tier_4_community"


AUTHORITY_TIER_SCORES: dict[str, float] = {
    AuthorityTier.TIER_1_OFFICIAL.value: 1.0,
    AuthorityTier.TIER_2_INTERGOVERNMENTAL.value: 0.85,
    AuthorityTier.TIER_3_SECONDARY.value: 0.60,
    AuthorityTier.TIER_4_COMMUNITY.value: 0.35,
}

AUTHORITY_TIER_DESCRIPTIONS: dict[str, str] = {
    AuthorityTier.TIER_1_OFFICIAL.value: "Official national, state, or municipal government agencies, ministries, and transport authorities",
    AuthorityTier.TIER_2_INTERGOVERNMENTAL.value: "Recognized intergovernmental organizations (WHO, UNESCO, World Bank, OECD, UN agencies)",
    AuthorityTier.TIER_3_SECONDARY.value: "High-quality secondary sources, verified statistical reference repositories, and official partner publishers",
    AuthorityTier.TIER_4_COMMUNITY.value: "Community-driven open datasets (e.g. OpenStreetMap). Strictly restricted to POI/amenity discovery, not legal/immigration authority",
}


class FreshnessPolicy(StrEnum):
    """Category-specific freshness policies governing document aging thresholds."""

    HIGH_90D = "high_90d"  # 90-day validity (immigration, legal, rapid-transit tariffs)
    MODERATE_180D = "moderate_180d"  # 180-day validity (housing, tenancy, municipal governance)
    ANNUAL_365D = "annual_365d"  # 365-day validity (education curricula, culture, general environment)
    STATIC = "static"  # General institutional structures with multi-year stability


class FreshnessStatus(StrEnum):
    """Current freshness evaluation state of a knowledge document."""

    FRESH = "fresh"
    AGING = "aging"
    STALE = "stale"
    UNKNOWN = "unknown"


# Controlled category to subcategory taxonomy tree (extensible)
TAXONOMY_TREE: dict[str, list[str]] = {
    KnowledgeCategory.IMMIGRATION.value: [
        "visa",
        "residency",
        "work_permits",
        "student_permits",
        "citizenship",
        "entry_requirements",
        "immigration_procedures",
    ],
    KnowledgeCategory.GOVERNMENT.value: [
        "government_services",
        "registration",
        "taxation_basics",
        "public_services",
        "official_forms",
        "municipal_services",
    ],
    KnowledgeCategory.TRANSPORT.value: [
        "public_transport",
        "metro",
        "bus",
        "rail",
        "airport",
        "transport_cards",
        "fares",
        "transport_rules",
    ],
    KnowledgeCategory.HEALTHCARE.value: [
        "healthcare_system",
        "public_healthcare",
        "private_healthcare",
        "emergency_services",
        "insurance",
        "pharmacies",
        "hospitals",
        "dental_care",
    ],
    KnowledgeCategory.EDUCATION.value: [
        "education_system",
        "universities",
        "schools",
        "admissions",
        "international_students",
        "tuition_guidance",
    ],
    KnowledgeCategory.HOUSING.value: [
        "renting",
        "tenancy_rules",
        "deposits",
        "utilities",
        "housing_regulations",
        "neighborhoods_locality_guidance",
    ],
    KnowledgeCategory.SAFETY.value: [
        "emergency_numbers",
        "official_safety_guidance",
        "disaster_preparedness",
        "local_emergency_procedures",
    ],
    KnowledgeCategory.CULTURE.value: [
        "language",
        "customs",
        "etiquette",
        "holidays",
        "cultural_practices",
        "lifestyle",
    ],
    KnowledgeCategory.LIFESTYLE.value: [
        "lifestyle",
        "customs",
        "cultural_practices",
        "recreation",
    ],
    KnowledgeCategory.CULTURE_LIFESTYLE.value: [
        "language",
        "customs",
        "etiquette",
        "holidays",
        "cultural_practices",
        "lifestyle",
    ],
    KnowledgeCategory.ENVIRONMENT.value: [
        "climate",
        "air_quality_guidance",
        "environmental_regulations",
        "seasonal_conditions",
        "disaster_environmental_guidance",
    ],
    KnowledgeCategory.CITY_INFORMATION.value: [
        "official_city_information",
        "municipal_information",
        "city_services",
        "local_regulations",
    ],
    KnowledgeCategory.RELOCATION.value: [
        "settling_in",
        "moving_guide",
        "checklists",
        "neighborhoods",
    ],
}

# Category to default freshness policy
CATEGORY_FRESHNESS_POLICIES: dict[str, str] = {
    KnowledgeCategory.IMMIGRATION.value: FreshnessPolicy.HIGH_90D.value,
    KnowledgeCategory.HEALTHCARE.value: FreshnessPolicy.HIGH_90D.value,
    KnowledgeCategory.TRANSPORT.value: FreshnessPolicy.HIGH_90D.value,
    KnowledgeCategory.GOVERNMENT.value: FreshnessPolicy.MODERATE_180D.value,
    KnowledgeCategory.HOUSING.value: FreshnessPolicy.MODERATE_180D.value,
    KnowledgeCategory.SAFETY.value: FreshnessPolicy.MODERATE_180D.value,
    KnowledgeCategory.EDUCATION.value: FreshnessPolicy.ANNUAL_365D.value,
    KnowledgeCategory.CULTURE.value: FreshnessPolicy.ANNUAL_365D.value,
    KnowledgeCategory.LIFESTYLE.value: FreshnessPolicy.ANNUAL_365D.value,
    KnowledgeCategory.CULTURE_LIFESTYLE.value: FreshnessPolicy.ANNUAL_365D.value,
    KnowledgeCategory.ENVIRONMENT.value: FreshnessPolicy.ANNUAL_365D.value,
    KnowledgeCategory.CITY_INFORMATION.value: FreshnessPolicy.ANNUAL_365D.value,
    KnowledgeCategory.RELOCATION.value: FreshnessPolicy.MODERATE_180D.value,
}


# Canonical city ID aliases mapping friendly slugs to canonical MongoDB city_ids
CANONICAL_CITY_ALIASES: dict[str, str] = {
    # Singapore
    "singapore_sg": "city_1702341327",
    "singapore": "city_1702341327",
    # Dubai
    "dubai_ae": "city_1784736618",
    "dubai": "city_1784736618",
    # London
    "london_uk": "city_1826645935",
    "london": "city_1826645935",
    # New York
    "new_york_us": "city_1840034016",
    "nyc": "city_1840034016",
    "new_york": "city_1840034016",
    # Paris
    "paris_fr": "city_1250015082",
    "paris": "city_1250015082",
    # Tokyo
    "tokyo_jp": "city_1392685764",
    "tokyo": "city_1392685764",
    # Mumbai
    "mumbai_in": "city_1356226629",
    "mumbai": "city_1356226629",
    # Delhi
    "delhi_in": "city_1356872604",
    "delhi": "city_1356872604",
}

CITY_TO_COUNTRY: dict[str, str] = {
    "city_1702341327": "singapore",
    "singapore_sg": "singapore",
    "city_1784736618": "uae",
    "dubai_ae": "uae",
    "city_1826645935": "uk",
    "london_uk": "uk",
    "city_1840034016": "usa",
    "new_york_us": "usa",
    "city_1250015082": "france",
    "paris_fr": "france",
    "city_1392685764": "japan",
    "tokyo_jp": "japan",
    "city_1356226629": "india",
    "mumbai_in": "india",
    "city_1356872604": "india",
    "delhi_in": "india",
}


def resolve_city_id(city_id: str | None) -> str | None:
    """Resolve city identifier to its canonical representation."""
    if not city_id:
        return None
    clean = city_id.strip().lower()
    return CANONICAL_CITY_ALIASES.get(clean, city_id.strip())


def get_country_for_city(city_id: str | None) -> str | None:
    """Lookup canonical country associated with a city identifier."""
    if not city_id:
        return None
    clean = city_id.strip().lower()
    canon = resolve_city_id(clean)
    return CITY_TO_COUNTRY.get(clean) or (CITY_TO_COUNTRY.get(canon) if canon else None)


def is_valid_category(category: str) -> bool:
    """Check if category string is supported by the taxonomy."""
    cat_lower = category.strip().lower()
    return cat_lower in {c.value for c in KnowledgeCategory} or cat_lower in TAXONOMY_TREE


def is_valid_subcategory(category: str, subcategory: str) -> bool:
    """Check if subcategory belongs to the given category."""
    cat_lower = category.strip().lower()
    sub_lower = subcategory.strip().lower().replace(" ", "_").replace("-", "_")
    valid_subs = TAXONOMY_TREE.get(cat_lower, [])
    return sub_lower in valid_subs


def normalize_category(category: str) -> str:
    """Normalize category name to canonical taxonomy value."""
    cat_clean = category.strip().lower()
    mapping = {
        "immigration": KnowledgeCategory.IMMIGRATION.value,
        "visa": KnowledgeCategory.IMMIGRATION.value,
        "government": KnowledgeCategory.GOVERNMENT.value,
        "transport": KnowledgeCategory.TRANSPORT.value,
        "transportation": KnowledgeCategory.TRANSPORT.value,
        "healthcare": KnowledgeCategory.HEALTHCARE.value,
        "health": KnowledgeCategory.HEALTHCARE.value,
        "education": KnowledgeCategory.EDUCATION.value,
        "housing": KnowledgeCategory.HOUSING.value,
        "accommodation": KnowledgeCategory.HOUSING.value,
        "safety": KnowledgeCategory.SAFETY.value,
        "culture": KnowledgeCategory.CULTURE.value,
        "lifestyle": KnowledgeCategory.LIFESTYLE.value,
        "culture_lifestyle": KnowledgeCategory.CULTURE_LIFESTYLE.value,
        "environment": KnowledgeCategory.ENVIRONMENT.value,
        "city_information": KnowledgeCategory.CITY_INFORMATION.value,
        "city_info": KnowledgeCategory.CITY_INFORMATION.value,
        "relocation": KnowledgeCategory.RELOCATION.value,
    }
    return mapping.get(cat_clean, KnowledgeCategory.CITY_INFORMATION.value)


def calculate_freshness(
    fetched_at: str | None,
    updated_at: str | None = None,
    category: str | None = None,
    policy: str | None = None,
) -> tuple[FreshnessStatus, float]:
    """Calculate freshness status and continuous freshness score [0.0 - 1.0].

    Returns:
        (FreshnessStatus, freshness_score)
    """
    reference_date_str = updated_at or fetched_at
    if not reference_date_str:
        return FreshnessStatus.UNKNOWN, 0.5

    try:
        # Parse ISO date string (handle Z or offset)
        ref_iso = reference_date_str.replace("Z", "+00:00")
        ref_dt = datetime.fromisoformat(ref_iso)
        if ref_dt.tzinfo is None:
            ref_dt = ref_dt.replace(tzinfo=timezone.utc)
    except Exception:
        return FreshnessStatus.UNKNOWN, 0.5

    now_dt = datetime.now(timezone.utc)
    age_days = max(0, (now_dt - ref_dt).days)

    active_policy = policy or CATEGORY_FRESHNESS_POLICIES.get(
        normalize_category(category or ""), FreshnessPolicy.MODERATE_180D.value
    )

    if active_policy == FreshnessPolicy.STATIC.value:
        return FreshnessStatus.FRESH, 1.0

    if active_policy == FreshnessPolicy.HIGH_90D.value:
        fresh_thresh = 90
        aging_thresh = 180
    elif active_policy == FreshnessPolicy.ANNUAL_365D.value:
        fresh_thresh = 365
        aging_thresh = 730
    else:  # MODERATE_180D
        fresh_thresh = 180
        aging_thresh = 365

    if age_days <= fresh_thresh:
        # Linear decay within fresh bracket: 1.0 down to 0.85
        score = 1.0 - (0.15 * (age_days / fresh_thresh))
        return FreshnessStatus.FRESH, round(score, 3)
    elif age_days <= aging_thresh:
        # Aging bracket: 0.85 down to 0.50
        aging_span = aging_thresh - fresh_thresh
        progress = (age_days - fresh_thresh) / max(1, aging_span)
        score = 0.85 - (0.35 * progress)
        return FreshnessStatus.AGING, round(score, 3)
    else:
        # Stale bracket: 0.50 decays towards 0.10
        stale_excess = age_days - aging_thresh
        score = max(0.10, 0.50 - (0.001 * stale_excess))
        return FreshnessStatus.STALE, round(score, 3)
