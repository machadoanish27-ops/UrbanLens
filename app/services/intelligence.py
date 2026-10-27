"""Intelligence service coordinating the UrbanLens orchestrator and multi-agent synthesis."""

from typing import TYPE_CHECKING, Any
from pymongo.database import Database

from app.orchestrator.context import OrchestrationContext
from app.orchestrator.result import AggregatedIntelligence

if TYPE_CHECKING:
    from app.orchestrator.orchestrator import UrbanLensOrchestrator


class IntelligenceService:
    """Service providing multi-agent query execution and catalog listing."""

    def __init__(self, database: Database) -> None:
        from app.orchestrator.orchestrator import UrbanLensOrchestrator
        self.database = database
        self.orchestrator = UrbanLensOrchestrator(database=database)

    def list_agents(self) -> list[dict[str, Any]]:
        """Return agent catalog with operational statuses."""
        return self.orchestrator.catalog()

    def _serialize_aggregated(self, aggregated: AggregatedIntelligence) -> dict[str, Any]:
        """Convert AggregatedIntelligence into a JSON-serializable dictionary."""
        results_data = []
        for r in aggregated.results:
            results_data.append({
                "agent_id": r.agent_id,
                "status": r.status.value,
                "data": dict(r.data),
                "sources": [
                    {
                        "source_id": s.source_id,
                        "provider": s.provider,
                        "observed_at": s.observed_at,
                        "retrieved_at": s.retrieved_at,
                        "source_version": s.source_version,
                        "confidence": s.confidence,
                    }
                    for s in r.sources
                ],
                "missing_data": list(r.missing_data),
                "unavailable_fields": list(r.unavailable_fields),
                "warnings": list(r.warnings),
                "knowledge_evidence": [
                    {
                        "evidence_id": ev.evidence_id,
                        "document_id": ev.document_id,
                        "chunk_id": ev.chunk_id,
                        "title": ev.title,
                        "source": ev.source,
                        "source_url": ev.source_url,
                        "publisher": ev.publisher,
                        "text": ev.text,
                        "category": ev.category,
                        "city_id": ev.city_id,
                        "country_id": ev.country_id,
                        "retrieved_at": ev.retrieved_at,
                        "retrieval_score": ev.retrieval_score,
                        "metadata": dict(ev.metadata),
                    }
                    for ev in getattr(r, "knowledge_evidence", ())
                ],
                "detail": r.detail,
                "summary": r.summary,
                "confidence": r.confidence,
                "observed_at": r.observed_at,
                "fetched_at": r.fetched_at,
            })

        sources_data = [
            {
                "source_id": s.source_id,
                "provider": s.provider,
                "observed_at": s.observed_at,
                "retrieved_at": s.retrieved_at,
                "source_version": s.source_version,
                "confidence": s.confidence,
            }
            for s in aggregated.sources
        ]

        aggregated_evidence = [
            {
                "evidence_id": ev.evidence_id,
                "document_id": ev.document_id,
                "chunk_id": ev.chunk_id,
                "title": ev.title,
                "source": ev.source,
                "source_url": ev.source_url,
                "publisher": ev.publisher,
                "text": ev.text,
                "category": ev.category,
                "city_id": ev.city_id,
                "country_id": ev.country_id,
                "retrieved_at": ev.retrieved_at,
                "retrieval_score": ev.retrieval_score,
                "metadata": dict(ev.metadata),
            }
            for ev in getattr(aggregated, "knowledge_evidence", ())
        ]

        return {
            "city_id": aggregated.city_id,
            "query": aggregated.query,
            "overall_status": aggregated.overall_status.value,
            "location": dict(aggregated.location),
            "selected_agents": list(aggregated.selected_agents),
            "results": results_data,
            "signals": list(aggregated.signals),
            "knowledge_evidence": aggregated_evidence,
            "summary": aggregated.summary,
            "warnings": list(aggregated.warnings),
            "sources": sources_data,
        }

    async def query_async(
        self,
        city_id: str | None = None,
        query: str | None = None,
        target_agents: list[str] | None = None,
    ) -> dict[str, Any]:
        """Asynchronously execute multi-agent intelligence query."""
        context = OrchestrationContext(
            city_id=city_id,
            query=query,
            target_agents=tuple(target_agents) if target_agents else (),
        )
        aggregated = await self.orchestrator.synthesize_async(context)
        return self._serialize_aggregated(aggregated)

    def query(
        self,
        city_id: str | None = None,
        query: str | None = None,
        target_agents: list[str] | None = None,
    ) -> dict[str, Any]:
        """Synchronously execute multi-agent intelligence query."""
        context = OrchestrationContext(
            city_id=city_id,
            query=query,
            target_agents=tuple(target_agents) if target_agents else (),
        )
        aggregated = self.orchestrator.synthesize(context)
        return self._serialize_aggregated(aggregated)

    async def ask_async(
        self,
        query: str,
        city_id: str | None = None,
    ) -> Any:
        """Execute multi-agent retrieval and synthesize grounded response via LLM reasoning."""
        return await self.orchestrator.ask_async(query=query, city_id=city_id)

    def ask(
        self,
        query: str,
        city_id: str | None = None,
    ) -> Any:
        """Synchronously execute multi-agent retrieval and synthesize grounded response via LLM reasoning."""
        return self.orchestrator.ask(query=query, city_id=city_id)

