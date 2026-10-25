"""Aggregated intelligence result representations."""

from dataclasses import dataclass, field
from app.models.agent import AgentResult, AgentStatus, SourceProvenance


@dataclass(frozen=True)
class AggregatedIntelligence:
    """Synthesized result aggregating multiple domain agent outputs with provenance."""

    city_id: str
    overall_status: AgentStatus
    results: tuple[AgentResult, ...]
    all_sources: tuple[SourceProvenance, ...] = field(default_factory=tuple)
    summary: str | None = None
    query: str | None = None
