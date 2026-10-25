"""Unit tests for the 7 modular domain agents and the UrbanLens orchestrator."""

from app.agents.accommodation import AccommodationAgent
from app.agents.cost import CostAgent
from app.agents.education_lifestyle import EducationLifestyleAgent
from app.agents.environment import EnvironmentAgent
from app.agents.location import LocationAgent
from app.agents.mobility import MobilityAgent
from app.agents.safety_healthcare import SafetyHealthcareAgent
from app.models.agent import AgentRequest, AgentStatus
from app.orchestrator.context import OrchestrationContext
from app.orchestrator.orchestrator import UrbanLensOrchestrator
from tests.conftest import MockDatabase


def test_location_agent_execution() -> None:
    db = MockDatabase()
    agent = LocationAgent(db)
    result = agent.execute(AgentRequest(city_id="tokyo_jp"))

    assert result.agent_id == "location"
    assert result.status == AgentStatus.COMPLETE
    assert result.data["city_id"] == "tokyo_jp"
    assert result.data["name"] == "Tokyo"
    assert len(result.sources) >= 1


def test_environment_agent_execution() -> None:
    db = MockDatabase()
    agent = EnvironmentAgent(db)
    result = agent.execute(AgentRequest(city_id="tokyo_jp"))

    assert result.agent_id == "environment"
    assert result.status == AgentStatus.COMPLETE
    assert result.data["current_weather"] is not None
    assert result.data["air_quality_global_weather"] is not None
    assert result.data["air_quality_who_annual"] is not None
    assert len(result.sources) >= 2


def test_mobility_agent_execution() -> None:
    db = MockDatabase()
    agent = MobilityAgent(db)
    result = agent.execute(AgentRequest(city_id="tokyo_jp"))

    assert result.agent_id == "mobility"
    assert result.data["metropolitan_scale"] == "megacity"
    assert "transit_infrastructure_tier" in result.data


def test_cost_agent_execution() -> None:
    db = MockDatabase()
    agent = CostAgent(db)

    # Available city
    result_tokyo = agent.execute(AgentRequest(city_id="tokyo_jp"))
    assert result_tokyo.agent_id == "cost_of_living"
    assert result_tokyo.status == AgentStatus.COMPLETE
    assert result_tokyo.data["metrics_recorded_count"] >= 2

    # Unavailable city
    result_paris = agent.execute(AgentRequest(city_id="paris_fr"))
    assert result_paris.status == AgentStatus.UNAVAILABLE
    assert "cost_of_living_metrics" in result_paris.missing_data


def test_accommodation_agent_execution() -> None:
    db = MockDatabase()
    agent = AccommodationAgent(db)
    result = agent.execute(AgentRequest(city_id="tokyo_jp"))

    assert result.agent_id == "accommodation"
    assert result.status == AgentStatus.COMPLETE
    assert result.data["housing_metrics_count"] >= 1


def test_education_lifestyle_agent_execution() -> None:
    db = MockDatabase()
    agent = EducationLifestyleAgent(db)
    result = agent.execute(AgentRequest(city_id="tokyo_jp"))

    assert result.agent_id == "education_culture"
    assert result.status == AgentStatus.COMPLETE
    assert result.data["total_country_institutions"] >= 1
    assert result.data["sample_institutions"][0]["name"] == "University of Tokyo"


def test_safety_healthcare_agent_execution() -> None:
    db = MockDatabase()
    agent = SafetyHealthcareAgent(db)
    result = agent.execute(AgentRequest(city_id="tokyo_jp"))

    assert result.agent_id == "safety_healthcare"
    assert "environmental_health" in result.data
    assert len(result.data["national_health_indicators"]) >= 1


def test_orchestrator_multi_agent_synthesis() -> None:
    db = MockDatabase()
    orchestrator = UrbanLensOrchestrator(database=db)
    context = OrchestrationContext(city_id="tokyo_jp", query="climate and universities")
    aggregated = orchestrator.synthesize(context)

    assert aggregated.city_id == "tokyo_jp"
    assert len(aggregated.results) == 7
    assert aggregated.overall_status in (AgentStatus.COMPLETE, AgentStatus.PARTIAL)
    assert len(aggregated.all_sources) > 0
    assert "UrbanLens intelligence synthesized" in (aggregated.summary or "")
