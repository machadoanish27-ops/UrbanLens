"""Knowledge models for UrbanLens RAG knowledge layer."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any

from app.models.taxonomy import (
    AUTHORITY_TIER_SCORES,
    AuthorityTier,
    FreshnessPolicy,
    FreshnessStatus,
    KnowledgeCategory,
    KnowledgeScope,
    TAXONOMY_TREE,
    calculate_freshness,
    is_valid_category,
    is_valid_subcategory,
    normalize_category,
)


class DocumentStatus(StrEnum):
    """Lifecycle status of a knowledge document."""

    ACTIVE = "active"
    ARCHIVED = "archived"
    DRAFT = "draft"


@dataclass(frozen=True)
class KnowledgeDocument:
    """Document representation in the UrbanLens knowledge store."""

    document_id: str
    title: str
    source: str
    content: str
    checksum: str
    source_url: str | None = None
    publisher: str | None = None
    authority_tier: str = AuthorityTier.TIER_1_OFFICIAL.value
    authority_score: float = 1.0
    scope: str = KnowledgeScope.COUNTRY.value
    country_id: str | None = None
    city_id: str | None = None
    category: str = KnowledgeCategory.CITY_INFORMATION.value
    subcategory: str | None = None
    language: str = "en"
    content_language: str = "en"
    source_type: str = "official"
    ingestion_method: str = "curated_source"
    canonical_url: str | None = None
    freshness_policy: str = FreshnessPolicy.MODERATE_180D.value
    review_required: bool = False
    published_at: str | None = None
    updated_at: str | None = None
    fetched_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: dict[str, Any] = field(default_factory=dict)
    status: str = DocumentStatus.ACTIVE.value


@dataclass(frozen=True)
class KnowledgeChunk:
    """Deterministic chunk derived from a KnowledgeDocument."""

    chunk_id: str
    document_id: str
    chunk_index: int
    text: str
    char_count: int
    token_count: int
    embedding: list[float] | None = None
    source: str = ""
    source_url: str | None = None
    publisher: str | None = None
    authority_tier: str = AuthorityTier.TIER_1_OFFICIAL.value
    authority_score: float = 1.0
    scope: str = KnowledgeScope.COUNTRY.value
    city_id: str | None = None
    country_id: str | None = None
    category: str = KnowledgeCategory.CITY_INFORMATION.value
    subcategory: str | None = None
    fetched_at: str | None = None
    updated_at: str | None = None
    freshness_policy: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class KnowledgeEvidence:
    """Grounded evidence item retrieved from the knowledge store for agent/orchestrator synthesis."""

    evidence_id: str
    document_id: str
    chunk_id: str
    title: str
    source: str
    text: str
    category: str
    subcategory: str | None = None
    source_url: str | None = None
    publisher: str | None = None
    authority_tier: str = AuthorityTier.TIER_1_OFFICIAL.value
    authority_score: float = 1.0
    scope: str = KnowledgeScope.COUNTRY.value
    freshness_status: str = FreshnessStatus.FRESH.value
    fetched_at: str | None = None
    updated_at: str | None = None
    city_id: str | None = None
    country_id: str | None = None
    retrieved_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    retrieval_score: float | None = None
    score_breakdown: dict[str, float] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
