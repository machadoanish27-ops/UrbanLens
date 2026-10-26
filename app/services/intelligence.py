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

        return {
            "city_id": aggregated.city_id,
            "query": aggregated.query,
            "overall_status": aggregated.overall_status.value,
            "location": dict(aggregated.location),
            "selected_agents": list(aggregated.selected_agents),
            "results": results_data,
            "signals": list(aggregated.signals),
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
