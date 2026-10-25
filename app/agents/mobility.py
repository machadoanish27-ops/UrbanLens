"""Mobility & Transportation Intelligence Agent."""

from app.agents.base import BaseAgent
from app.db.repositories.city import CityRepository
from app.models.agent import AgentRequest, AgentResult, AgentStatus, SourceProvenance


class MobilityAgent(BaseAgent):
    """Agent 3: Mobility / Transportation.
    
    Evaluates urban mobility indicators, transit accessibility context,
    and airport/rail hub presence based on metropolitan scale.
    """

    @property
    def agent_id(self) -> str:
        return "mobility"

    @property
    def display_name(self) -> str:
        return "Mobility / Transportation"

    @property
    def scope(self) -> str:
        return "Urban transit infrastructure, metropolitan connectivity, and commute readiness"

    def execute(self, request: AgentRequest) -> AgentResult:
        if not request.city_id:
            return self.create_unavailable_result("No city_id provided in request.", missing_data=("city_id",))

        if not self.database:
            return self.create_unavailable_result("Database connection not provided to agent.", missing_data=("database",))

        repo = CityRepository(self.database)
        city = repo.get_by_city_id(request.city_id)
        if not city:
            return self.create_unavailable_result(f"City '{request.city_id}' not found.", missing_data=("city_record",))

        population = city.get("population") or 0
        capital_type = city.get("capital")
        is_metro = population >= 1_000_000
        is_major_hub = is_metro or capital_type in ("primary", "admin")

        sources = (
            SourceProvenance(
                source_id="city_demographics",
                provider="canonical_city_registry",
            ),
        )

        return AgentResult(
            agent_id=self.agent_id,
            status=AgentStatus.PARTIAL,
            data={
                "city_id": city["city_id"],
                "metropolitan_scale": "megacity" if population >= 5_000_000 else ("metropolis" if is_metro else "regional_urban"),
                "capital_status": capital_type or "standard",
                "transit_infrastructure_tier": "Tier-1 Multi-Modal" if is_major_hub else "Tier-2 Regional Transit",
                "live_gtfs_connected": False,
                "note": "Baseline transit profile evaluated from metropolitan demographics; real-time GTFS feeds scheduled for live provider phase.",
            },
            sources=sources,
            missing_data=("live_transit_feed",),
            detail="Metropolitan mobility profile evaluated from validated urban demographics.",
        )
