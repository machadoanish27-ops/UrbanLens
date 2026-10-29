"""Pydantic schemas for knowledge documents, evidence, search, and audits."""

from typing import Any
from pydantic import BaseModel, Field


class KnowledgeDocumentCreate(BaseModel):
    """Payload to ingest a new knowledge document."""

    title: str = Field(..., min_length=2, max_length=300)
    source: str = Field(..., min_length=2, max_length=150)
    content: str = Field(..., min_length=20)
    source_url: str | None = Field(default=None)
    publisher: str | None = Field(default=None)
    authority_tier: str = Field(default="tier_1_official")
    authority_score: float | None = Field(default=None, ge=0.0, le=1.0)
    scope: str = Field(default="country")
    country_id: str | None = Field(default=None)
    city_id: str | None = Field(default=None)
    category: str = Field(default="city_information")
    subcategory: str | None = Field(default=None)
    language: str = Field(default="en")
    content_language: str = Field(default="en")
    source_type: str = Field(default="official")
    ingestion_method: str = Field(default="direct")
    canonical_url: str | None = Field(default=None)
    freshness_policy: str = Field(default="moderate_180d")
    review_required: bool = Field(default=False)
    published_at: str | None = Field(default=None)
    metadata: dict[str, Any] = Field(default_factory=dict)


class KnowledgeDocumentResponse(BaseModel):
    """Schema representing an ingested knowledge document."""

    document_id: str
    title: str
    source: str
    source_url: str | None = None
    publisher: str | None = None
    authority_tier: str = "tier_1_official"
    authority_score: float = 1.0
    scope: str = "country"
    country_id: str | None = None
    city_id: str | None = None
    category: str
    subcategory: str | None = None
    language: str = "en"
    content_language: str = "en"
    source_type: str = "official"
    ingestion_method: str = "curated_source"
    canonical_url: str | None = None
    freshness_policy: str = "moderate_180d"
    review_required: bool = False
    published_at: str | None = None
    fetched_at: str
    checksum: str
    chunks_count: int = 0
    status: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class KnowledgeEvidenceSchema(BaseModel):
    """Schema for retrieved evidence items returned to agents or callers."""

    evidence_id: str
    document_id: str
    chunk_id: str
    title: str
    source: str
    source_url: str | None = None
    publisher: str | None = None
    authority_tier: str = "tier_1_official"
    authority_score: float = 1.0
    scope: str = "country"
    freshness_status: str = "fresh"
    fetched_at: str | None = None
    updated_at: str | None = None
    text: str
    category: str
    subcategory: str | None = None
    city_id: str | None = None
    country_id: str | None = None
    retrieved_at: str
    retrieval_score: float | None = None
    score_breakdown: dict[str, float] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class KnowledgeSearchRequest(BaseModel):
    """Search request parameters."""

    query: str = Field(..., min_length=1, description="Natural language search query")
    city_id: str | None = Field(default=None, description="Optional city filter")
    country_id: str | None = Field(default=None, description="Optional country filter")
    categories: list[str] | None = Field(default=None, description="Optional category filters")
    subcategories: list[str] | None = Field(default=None, description="Optional subcategory filters")
    scope: str | None = Field(default=None, description="Optional scope filter (global, country, city)")
    authority_tier: str | None = Field(default=None, description="Optional authority tier filter")
    top_k: int = Field(default=5, ge=1, le=20, description="Max evidence chunks to return")
    min_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Minimum similarity threshold")


class KnowledgeConflictItem(BaseModel):
    """Discrepancy detected across retrieved sources for the same query."""

    category: str
    source_a: str
    source_b: str
    evidence_id_a: str
    evidence_id_b: str
    difference_note: str


class KnowledgeSearchResponse(BaseModel):
    """Response payload for knowledge retrieval."""

    query: str
    total_found: int
    evidence: list[KnowledgeEvidenceSchema] = Field(default_factory=list)
    conflict_detected: bool = False
    conflicts: list[KnowledgeConflictItem] = Field(default_factory=list)


class KnowledgeStatsResponse(BaseModel):
    """Aggregated statistics of the UrbanLens RAG knowledge base."""

    total_documents: int
    total_chunks: int
    categories_breakdown: dict[str, int]
    scope_breakdown: dict[str, int]
    tier_breakdown: dict[str, int]
    countries_covered: list[str]
    cities_covered: list[str]
    freshness_summary: dict[str, int]
