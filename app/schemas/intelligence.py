"""Intelligence, agent results, and orchestrator query schemas."""

from typing import Any
from pydantic import BaseModel, Field


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


class AgentResultSchema(BaseModel):
    """Standardized output produced by a domain agent."""

    agent_id: str
    status: str
    data: dict[str, Any] = Field(default_factory=dict)
    sources: list[SourceProvenanceSchema] = Field(default_factory=list)
    missing_data: list[str] = Field(default_factory=list)
    detail: str | None = None


class IntelligenceQueryRequest(BaseModel):
    """Request payload for multi-agent intelligence queries."""

    city_id: str
    query: str | None = None
    agents: list[str] | None = Field(
        default=None,
        description="Optional subset of agent IDs to execute. If omitted, all relevant agents are consulted.",
    )


class IntelligenceQueryResponse(BaseModel):
    """Synthesized multi-agent intelligence response."""

    city_id: str
    query: str | None = None
    overall_status: str
    results: list[AgentResultSchema] = Field(default_factory=list)
