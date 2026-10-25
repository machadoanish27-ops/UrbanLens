"""Agent orchestrator service providing backward-compatible interface and multi-agent coordination."""

from typing import Protocol

from app.agents.catalog import AGENT_CATALOG
from app.models.agent import AgentRequest, AgentResult, AgentStatus
from app.orchestrator.orchestrator import UrbanLensOrchestrator


class Agent(Protocol):
    def execute(self, request: AgentRequest) -> AgentResult: ...


class AgentOrchestrator:
    """Compatibility orchestrator facade preserving earlier protocol tests while integrating with full architecture."""

    def __init__(self, agents: dict[str, Agent] | None = None) -> None:
        self._agents = agents or {}

    def catalog(self) -> list[dict[str, str | bool]]:
        return [
            {
                "agent_id": definition.agent_id,
                "display_name": definition.display_name,
                "scope": definition.scope,
                "configured": definition.agent_id in self._agents,
                "integration_status": definition.integration_status,
            }
            for definition in AGENT_CATALOG
        ]

    def execute(self, request: AgentRequest) -> tuple[AgentResult, ...]:
        results = []
        for definition in AGENT_CATALOG:
            agent = self._agents.get(definition.agent_id)
            if agent is None:
                results.append(
                    AgentResult(
                        agent_id=definition.agent_id,
                        status=AgentStatus.UNAVAILABLE,
                        missing_data=("integration",),
                        detail="TODO: configure this agent before use.",
                    )
                )
                continue
            results.append(agent.execute(request))
        return tuple(results)
