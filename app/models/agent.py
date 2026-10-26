from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Mapping
from app.models.knowledge import KnowledgeEvidence


class AgentStatus(StrEnum):
    COMPLETE = "complete"
    PARTIAL = "partial"
    UNAVAILABLE = "unavailable"
    STALE = "stale"
    ERROR = "error"
    FRESH = "fresh"
    DATABASE = "database"


@dataclass(frozen=True)
class AgentRequest:
    city_id: str | None = None
    query: str | None = None


@dataclass(frozen=True)
class SourceProvenance:
    source_id: str
    provider: str | None = None
    observed_at: str | None = None
    retrieved_at: str | None = None
    source_version: str | None = None
    confidence: float | None = None


@dataclass(frozen=True)
class AgentResult:
    agent_id: str
    status: AgentStatus
    data: Mapping[str, object] = field(default_factory=dict)
    sources: tuple[SourceProvenance, ...] = ()
    knowledge_evidence: tuple[KnowledgeEvidence, ...] = ()
    missing_data: tuple[str, ...] = ()
    detail: str | None = None
    summary: str | None = None
    confidence: float = 1.0
    warnings: tuple[str, ...] = ()
    unavailable_fields: tuple[str, ...] = ()
    observed_at: str | None = None
    fetched_at: str | None = None