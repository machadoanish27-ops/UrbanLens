"""Schemas for LLM intelligence queries, responses, and grounded evidence citations."""

from typing import Any
from pydantic import BaseModel, Field


class EvidenceUsedItem(BaseModel):
    """Citation of a specific grounded evidence item utilized in the answer."""

    evidence_id: str | None = None
    title: str | None = None
    source: str | None = None
    source_url: str | None = None
    claim: str | None = None


class LLMMetadata(BaseModel):
    """Execution telemetry for the LLM call."""

    provider: str
    model: str
    status: str
    latency_ms: float = 0.0
    cached: bool = False
    usage: dict[str, int] | None = None
    fallback_used: bool = False
    error_category: str = "none"


class LLMIntelligenceResponse(BaseModel):
    """Structured response validated from raw LLM JSON generation."""

    answer: str
    recommendation: str | None = None
    key_points: list[str] = Field(default_factory=list)
    evidence_used: list[EvidenceUsedItem] = Field(default_factory=list)
    sources: list[str] = Field(default_factory=list)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    warnings: list[str] = Field(default_factory=list)


class LLMAskRequest(BaseModel):
    """Request payload for natural language intelligence query via LLM reasoning."""

    query: str = Field(..., min_length=1, description="Natural language intelligence query")
    city_id: str | None = Field(
        default=None,
        description="Optional canonical city identifier. If omitted, resolved from query text.",
    )


class LLMAskResponse(BaseModel):
    """Synthesized LLM response with grounded evidence, recommendations, and telemetry."""

    city_id: str
    city_name: str | None = None
    country: str | None = None
    query: str
    answer: str
    recommendation: str | None = None
    key_points: list[str] = Field(default_factory=list)
    evidence_used: list[EvidenceUsedItem] = Field(default_factory=list)
    sources: list[str] = Field(default_factory=list)
    confidence: float = 1.0
    warnings: list[str] = Field(default_factory=list)
    llm: LLMMetadata
