"""Aggregated intelligence result representations."""

from dataclasses import dataclass, field
from typing import Any
from app.models.agent import AgentResult, AgentStatus, SourceProvenance
from app.models.knowledge import KnowledgeEvidence


@dataclass(frozen=True)
class AggregatedIntelligence:
    """Synthesized result aggregating multiple domain agent outputs with provenance."""

    city_id: str
    overall_status: AgentStatus
    results: tuple[AgentResult, ...]
    all_sources: tuple[SourceProvenance, ...] = field(default_factory=tuple)
    summary: str | None = None
    query: str | None = None
    location: dict[str, Any] = field(default_factory=dict)
    selected_agents: tuple[str, ...] = ()
    signals: tuple[dict[str, Any], ...] = ()
    knowledge_evidence: tuple[KnowledgeEvidence, ...] = ()
    warnings: tuple[str, ...] = ()
    sources: tuple[SourceProvenance, ...] = ()
    unavailable_fields: tuple[str, ...] = ()

