"""Intelligence, agent results, and orchestrator query schemas."""

from typing import Any
from pydantic import BaseModel, Field

from app.schemas.knowledge import KnowledgeEvidenceSchema


class AgentCatalogItem(BaseModel):
    """Metadata regarding a domain agent's scope and state."""

    agent_id: str
    display_name: str
    scope: str
    configured: bool
    integration_status: str


class SourceProvenanceSchema(BaseModel):
    """Provenance indicator for agent grounding."""

    source_id: str
    provider: str | None = None
    observed_at: str | None = None
    retrieved_at: str | None = None
    source_version: str | None = None
    confidence: float | None = None


class AgentResultSchema(BaseModel):
    """Standardized output produced by a domain agent."""

    agent_id: str
    status: str
    data: dict[str, Any] = Field(default_factory=dict)
    sources: list[SourceProvenanceSchema] = Field(default_factory=list)
    knowledge_evidence: list[KnowledgeEvidenceSchema] = Field(default_factory=list)
    missing_data: list[str] = Field(default_factory=list)
    unavailable_fields: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    detail: str | None = None
    summary: str | None = None
    confidence: float = 1.0
    observed_at: str | None = None
    fetched_at: str | None = None


class IntelligenceSignalSchema(BaseModel):
    """Normalized metric signal extracted from agent observations."""

    domain: str
    metric: str
    value: Any
    source: str | None = None


class IntelligenceQueryRequest(BaseModel):
    """Request payload for multi-agent intelligence queries."""

    city_id: str | None = Field(
        default=None,
        description="Optional canonical city identifier. If omitted, resolved from query text.",
    )
    query: str | None = Field(
        default=None,
        description="Natural language intelligence query.",
    )
    agents: list[str] | None = Field(
        default=None,
        description="Optional subset of agent IDs to execute. If omitted, deterministically routed.",
    )


class IntelligenceQueryResponse(BaseModel):
    """Synthesized multi-agent intelligence response."""

    city_id: str
    query: str | None = None
    overall_status: str
    location: dict[str, Any] = Field(default_factory=dict)
    selected_agents: list[str] = Field(default_factory=list)
    results: list[AgentResultSchema] = Field(default_factory=list)
    signals: list[dict[str, Any]] = Field(default_factory=list)
    knowledge_evidence: list[KnowledgeEvidenceSchema] = Field(default_factory=list)
    summary: str | None = None
    warnings: list[str] = Field(default_factory=list)
    sources: list[SourceProvenanceSchema] = Field(default_factory=list)
