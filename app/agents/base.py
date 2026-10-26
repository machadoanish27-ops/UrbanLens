"""Base abstract agent contract for UrbanLens domain intelligence agents."""

import asyncio
import concurrent.futures
from abc import ABC, abstractmethod
from typing import Any
from pymongo.database import Database

from app.models.agent import AgentRequest, AgentResult, AgentStatus, SourceProvenance
from app.models.knowledge import KnowledgeEvidence


class BaseAgent(ABC):
    """Abstract base class for all domain-specific intelligence agents."""

    def __init__(
        self,
        database: Database | None = None,
        knowledge_service: Any = None,
    ) -> None:
        self.database = database
        self.knowledge_service = knowledge_service
        if self.knowledge_service is None and database is not None:
            try:
                from app.db.repositories.knowledge import KnowledgeRepository
                from app.services.knowledge import KnowledgeService
                self.knowledge_service = KnowledgeService(KnowledgeRepository(database))
            except Exception:
                self.knowledge_service = None

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

    async def execute_async(self, request: AgentRequest) -> AgentResult:
        """Execute agent analysis asynchronously. Default delegates to synchronous execute."""
        return self.execute(request)

    def execute(self, request: AgentRequest) -> AgentResult:
        """Execute agent analysis synchronously. If subclasses only implement execute_async, runs it."""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                return pool.submit(asyncio.run, self.execute_async(request)).result()
        return asyncio.run(self.execute_async(request))

    def create_unavailable_result(
        self,
        detail: str,
        missing_data: tuple[str, ...] = (),
        warnings: tuple[str, ...] = (),
        confidence: float = 0.0,
    ) -> AgentResult:
        """Helper to construct a standardized unavailable result."""
        return AgentResult(
            agent_id=self.agent_id,
            status=AgentStatus.UNAVAILABLE,
            data={},
            sources=(),
            knowledge_evidence=(),
            missing_data=missing_data,
            unavailable_fields=missing_data,
            detail=detail,
            summary=detail,
            warnings=warnings,
            confidence=confidence,
        )

    async def retrieve_knowledge_evidence(
        self,
        query: str | None,
        city_id: str | None,
        categories: list[str],
        top_k: int = 2,
        min_score: float = 0.1,
    ) -> list[KnowledgeEvidence]:
        """Query knowledge service if configured and query provided."""
        if not getattr(self, "knowledge_service", None) or not query:
            return []
        try:
            return await self.knowledge_service.search_knowledge(
                query=query,
                city_id=city_id,
                categories=categories,
                top_k=top_k,
                min_score=min_score,
            )
        except Exception:
            return []


