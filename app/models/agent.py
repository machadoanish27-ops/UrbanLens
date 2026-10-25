from dataclasses import dataclass, field
from enum import StrEnum
from typing import Mapping


class AgentStatus(StrEnum):
    COMPLETE = "complete"
    PARTIAL = "partial"
    UNAVAILABLE = "unavailable"
    STALE = "stale"
    ERROR = "error"


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


@dataclass(frozen=True)
class AgentResult:
    agent_id: str
    status: AgentStatus
    data: Mapping[str, object] = field(default_factory=dict)
    sources: tuple[SourceProvenance, ...] = ()
    missing_data: tuple[str, ...] = ()
    detail: str | None = None