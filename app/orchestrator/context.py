"""Orchestration context for multi-agent execution and future RAG grounding."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Sequence


@dataclass(frozen=True)
class OrchestrationContext:
    """Context object encapsulating the user request, targets, and retrieval state."""

    city_id: str
    query: str | None = None
    target_agents: tuple[str, ...] = ()
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    retrieved_documents: Sequence[dict[str, Any]] = field(default_factory=tuple)
    metadata: dict[str, Any] = field(default_factory=dict)
