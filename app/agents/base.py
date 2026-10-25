"""Base abstract agent contract for UrbanLens domain intelligence agents."""

from abc import ABC, abstractmethod
from typing import Any
from pymongo.database import Database

from app.models.agent import AgentRequest, AgentResult, AgentStatus, SourceProvenance


class BaseAgent(ABC):
    """Abstract base class for all domain-specific intelligence agents."""

    def __init__(self, database: Database | None = None) -> None:
        self.database = database

    @property
    @abstractmethod
    def agent_id(self) -> str:
        """Unique identifier for this agent domain."""
        ...

    @property
    @abstractmethod
    def display_name(self) -> str:
        """Human-readable name of the agent."""
        ...

    @property
    @abstractmethod
    def scope(self) -> str:
        """Domain coverage description."""
        ...

    @abstractmethod
    def execute(self, request: AgentRequest) -> AgentResult:
        """Execute agent analysis for the provided request and return grounded results."""
        ...

    def create_unavailable_result(self, detail: str, missing_data: tuple[str, ...] = ()) -> AgentResult:
        """Helper to construct a standardized unavailable result."""
        return AgentResult(
            agent_id=self.agent_id,
            status=AgentStatus.UNAVAILABLE,
            data={},
            sources=(),
            missing_data=missing_data,
            detail=detail,
        )
