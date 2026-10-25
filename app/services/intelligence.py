"""Intelligence service coordinating the UrbanLens orchestrator and multi-agent synthesis."""

from typing import Any
from pymongo.database import Database

from app.orchestrator.context import OrchestrationContext
from app.orchestrator.orchestrator import UrbanLensOrchestrator


class IntelligenceService:
    """Service providing multi-agent query execution and catalog listing."""

    def __init__(self, database: Database) -> None:
        self.database = database
        self.orchestrator = UrbanLensOrchestrator(database=database)

    def list_agents(self) -> list[dict[str, Any]]:
        """Return agent catalog with operational statuses."""
        return self.orchestrator.catalog()

    def query(
        self,
        city_id: str,
        query: str | None = None,
        target_agents: list[str] | None = None,
    ) -> dict[str, Any]:
        """Execute multi-agent intelligence query for a city."""
        context = OrchestrationContext(
            city_id=city_id,
            query=query,
            target_agents=tuple(target_agents) if target_agents else (),
        )
        aggregated = self.orchestrator.synthesize(context)

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
                    }
                    for s in r.sources
                ],
                "missing_data": list(r.missing_data),
                "detail": r.detail,
            })

        return {
            "city_id": aggregated.city_id,
            "query": aggregated.query,
            "overall_status": aggregated.overall_status.value,
            "summary": aggregated.summary,
            "results": results_data,
        }
