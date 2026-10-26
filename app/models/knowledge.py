"""Knowledge models for UrbanLens RAG knowledge layer."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any


class KnowledgeCategory(StrEnum):
    """Recognized categories for knowledge documents and evidence."""

    RELOCATION = "relocation"
    GOVERNMENT = "government"
    TRANSPORT = "transport"
    HEALTHCARE = "healthcare"
    EDUCATION = "education"
    SAFETY = "safety"
    CULTURE = "culture"
    LIFESTYLE = "lifestyle"
    HOUSING = "housing"
    IMMIGRATION = "immigration"
    ENVIRONMENT = "environment"
    CITY_INFORMATION = "city_information"


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
    country_id: str | None = None
    city_id: str | None = None
    category: str = KnowledgeCategory.CITY_INFORMATION.value
    language: str = "en"
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
    city_id: str | None = None
    country_id: str | None = None
    category: str = KnowledgeCategory.CITY_INFORMATION.value
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
    source_url: str | None = None
    publisher: str | None = None
    city_id: str | None = None
    country_id: str | None = None
    retrieved_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    retrieval_score: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
