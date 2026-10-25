"""Cost of Living & Budget Intelligence Agent."""

from app.agents.base import BaseAgent
from app.db.repositories.cost_of_living import CostOfLivingRepository
from app.models.agent import AgentRequest, AgentResult, AgentStatus, SourceProvenance


class CostAgent(BaseAgent):
    """Agent 4: Cost of Living / Budget.
    
    Grounds municipal budget requirements, consumer price indices,
    and relative affordability metrics using verified basket benchmarks.
    """

    @property
    def agent_id(self) -> str:
        return "cost_of_living"

    @property
    def display_name(self) -> str:
        return "Cost-of-Living / Budget"

    @property
    def scope(self) -> str:
        return "Consumer basket metrics, rental indices, and city living expense benchmarks"

    def execute(self, request: AgentRequest) -> AgentResult:
        if not request.city_id:
            return self.create_unavailable_result("No city_id provided in request.", missing_data=("city_id",))

        if not self.database:
            return self.create_unavailable_result("Database connection not provided to agent.", missing_data=("database",))

        repo = CostOfLivingRepository(self.database)
        metrics = repo.get_by_city_id(request.city_id)

        if not metrics:
            return self.create_unavailable_result(
                f"No verified cost-of-living metrics found for city '{request.city_id}'. Estimates are strictly non-fabricated.",
                missing_data=("cost_of_living_metrics",),
            )

        sources = (
            SourceProvenance(
                source_id="cost_of_living",
                provider=metrics[0].get("source_id", "canonical_cost_dataset"),
                observed_at=str(metrics[0].get("observed_at")) if metrics[0].get("observed_at") else None,
            ),
        )

        metrics_map = {m["metric"]: m.get("value") for m in metrics if "metric" in m}

        return AgentResult(
            agent_id=self.agent_id,
            status=AgentStatus.COMPLETE,
            data={
                "city_id": request.city_id,
                "metrics_recorded_count": len(metrics),
                "metrics": metrics_map,
            },
            sources=sources,
            missing_data=(),
            detail="Canonical cost-of-living metrics retrieved without interpolation.",
        )
