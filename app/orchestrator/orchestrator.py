"""UrbanLens multi-agent orchestrator."""

from typing import Sequence
from pymongo.database import Database

from app.agents.accommodation import AccommodationAgent
from app.agents.base import BaseAgent
from app.agents.catalog import AGENT_CATALOG
from app.agents.cost import CostAgent
from app.agents.education_lifestyle import EducationLifestyleAgent
from app.agents.environment import EnvironmentAgent
from app.agents.location import LocationAgent
from app.agents.mobility import MobilityAgent
from app.agents.safety_healthcare import SafetyHealthcareAgent
from app.models.agent import AgentRequest, AgentResult, AgentStatus, SourceProvenance
from app.orchestrator.context import OrchestrationContext
from app.orchestrator.result import AggregatedIntelligence


class UrbanLensOrchestrator:
    """Multi-agent orchestrator coordinating domain agents to generate grounded city intelligence."""

    def __init__(
        self,
        database: Database | None = None,
        agents: dict[str, BaseAgent] | None = None,
    ) -> None:
        self.database = database
        if agents is not None:
            self._agents = agents
        elif database is not None:
            self._agents = {
                "location": LocationAgent(database),
                "environment": EnvironmentAgent(database),
                "mobility": MobilityAgent(database),
                "cost_of_living": CostAgent(database),
                "accommodation": AccommodationAgent(database),
                "education_culture": EducationLifestyleAgent(database),
                "safety_healthcare": SafetyHealthcareAgent(database),
            }
        else:
            self._agents = {}

    def catalog(self) -> list[dict[str, str | bool]]:
        """Return catalog of available agents and their active configuration state."""
        return [
            {
                "agent_id": definition.agent_id,
                "display_name": definition.display_name,
                "scope": definition.scope,
                "configured": definition.agent_id in self._agents,
                "integration_status": "ready" if definition.agent_id in self._agents else definition.integration_status,
            }
            for definition in AGENT_CATALOG
        ]

    def execute_agents(
        self,
        request: AgentRequest,
        target_agent_ids: Sequence[str] | None = None,
    ) -> tuple[AgentResult, ...]:
        """Execute selected agents or all 7 catalog agents."""
        results: list[AgentResult] = []
        target_ids = set(target_agent_ids) if target_agent_ids else {d.agent_id for d in AGENT_CATALOG}

        for definition in AGENT_CATALOG:
            if definition.agent_id not in target_ids:
                continue

            agent = self._agents.get(definition.agent_id)
            if agent is None:
                results.append(
                    AgentResult(
                        agent_id=definition.agent_id,
                        status=AgentStatus.UNAVAILABLE,
                        missing_data=("integration",),
                        detail="Agent not configured or database offline.",
                    )
                )
                continue

            try:
                res = agent.execute(request)
                results.append(res)
            except Exception as exc:
                results.append(
                    AgentResult(
                        agent_id=definition.agent_id,
                        status=AgentStatus.ERROR,
                        detail=f"Agent execution encountered error: {str(exc)}",
                        missing_data=("execution_error",),
                    )
                )

        return tuple(results)

    def synthesize(self, context: OrchestrationContext) -> AggregatedIntelligence:
        """Synthesize multi-agent outputs into unified grounded intelligence."""
        agent_req = AgentRequest(city_id=context.city_id, query=context.query)
        results = self.execute_agents(agent_req, target_agent_ids=context.target_agents or None)

        all_sources: list[SourceProvenance] = []
        for r in results:
            all_sources.extend(r.sources)

        statuses = [r.status for r in results]
        if all(s == AgentStatus.COMPLETE for s in statuses):
            overall = AgentStatus.COMPLETE
        elif any(s in (AgentStatus.COMPLETE, AgentStatus.PARTIAL) for s in statuses):
            overall = AgentStatus.PARTIAL
        else:
            overall = AgentStatus.UNAVAILABLE

        # Summary for future LLM integration
        summary = (
            f"UrbanLens intelligence synthesized across {len(results)} agent domains "
            f"with status '{overall.value}'. Total grounded sources: {len(all_sources)}."
        )

        return AggregatedIntelligence(
            city_id=context.city_id,
            overall_status=overall,
            results=results,
            all_sources=tuple(all_sources),
            summary=summary,
            query=context.query,
        )
