"""Pydantic schemas for knowledge documents, evidence, and search."""

from typing import Any
from pydantic import BaseModel, Field


class KnowledgeDocumentCreate(BaseModel):
    """Payload to ingest a new knowledge document."""

    title: str = Field(..., min_length=2, max_length=300)
    source: str = Field(..., min_length=2, max_length=150)
    content: str = Field(..., min_length=20)
    source_url: str | None = Field(default=None)
    publisher: str | None = Field(default=None)
    country_id: str | None = Field(default=None)
    city_id: str | None = Field(default=None)
    category: str = Field(default="city_information")
    language: str = Field(default="en")
    published_at: str | None = Field(default=None)
    metadata: dict[str, Any] = Field(default_factory=dict)


class KnowledgeDocumentResponse(BaseModel):
    """Schema representing an ingested knowledge document."""

    document_id: str
    title: str
    source: str
    source_url: str | None = None
    publisher: str | None = None
    country_id: str | None = None
    city_id: str | None = None
    category: str
    language: str
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
    text: str
    category: str
    city_id: str | None = None
    country_id: str | None = None
    retrieved_at: str
    retrieval_score: float | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class KnowledgeSearchRequest(BaseModel):
    """Search request parameters."""

    query: str = Field(..., min_length=1, description="Natural language search query")
    city_id: str | None = Field(default=None, description="Optional city filter")
    country_id: str | None = Field(default=None, description="Optional country filter")
    categories: list[str] | None = Field(default=None, description="Optional category filters")
    top_k: int = Field(default=5, ge=1, le=20, description="Max evidence chunks to return")
    min_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Minimum similarity threshold")


class KnowledgeSearchResponse(BaseModel):
    """Response payload for knowledge retrieval."""

    query: str
    total_found: int
    evidence: list[KnowledgeEvidenceSchema] = Field(default_factory=list)
