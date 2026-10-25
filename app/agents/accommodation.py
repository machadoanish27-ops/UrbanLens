"""Accommodation & Locality Intelligence Agent."""

from app.agents.base import BaseAgent
from app.db.repositories.cost_of_living import CostOfLivingRepository
from app.models.agent import AgentRequest, AgentResult, AgentStatus, SourceProvenance


class AccommodationAgent(BaseAgent):
    """Agent 5: Accommodation / Locality.
    
    Examines residential rental benchmarks, neighborhood housing density,
    and locality pricing dynamics.
    """

    @property
    def agent_id(self) -> str:
        return "accommodation"

    @property
    def display_name(self) -> str:
        return "Accommodation / Locality"

    @property
    def scope(self) -> str:
        return "Residential rental benchmarks, neighborhood density, and housing indices"

    def execute(self, request: AgentRequest) -> AgentResult:
        if not request.city_id:
            return self.create_unavailable_result("No city_id provided in request.", missing_data=("city_id",))

        if not self.database:
            return self.create_unavailable_result("Database connection not provided to agent.", missing_data=("database",))

        repo = CostOfLivingRepository(self.database)
        metrics = repo.get_by_city_id(request.city_id)

        rental_metrics = {}
        for m in metrics:
            metric_name = m.get("metric", "").lower()
            if any(term in metric_name for term in ("rent", "apartment", "price per square")):
                rental_metrics[m["metric"]] = {
                    "value": m.get("value"),
                    "unit": m.get("unit"),
                }

        if not rental_metrics:
            return self.create_unavailable_result(
                f"No verified residential rental metrics available for city '{request.city_id}'.",
                missing_data=("rental_housing_metrics",),
            )

        sources = (
            SourceProvenance(
                source_id="cost_of_living",
                provider="canonical_cost_dataset",
            ),
        )

        return AgentResult(
            agent_id=self.agent_id,
            status=AgentStatus.COMPLETE,
            data={
                "city_id": request.city_id,
                "housing_metrics_count": len(rental_metrics),
                "housing_metrics": rental_metrics,
            },
            sources=sources,
            missing_data=(),
            detail="Housing and accommodation benchmarks grounded in validated basket entries.",
        )
