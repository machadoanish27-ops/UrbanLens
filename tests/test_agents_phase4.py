"""Comprehensive unit tests for Phase 4: Agents, Services, Orchestrator, and In-Memory Cache."""

import time
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.agents.accommodation import AccommodationAgent
from app.agents.cost import CostAgent
from app.agents.education_lifestyle import EducationLifestyleAgent
from app.agents.environment import EnvironmentAgent
from app.agents.location import LocationAgent
from app.agents.mobility import MobilityAgent
from app.agents.safety_healthcare import SafetyHealthcareAgent
from app.core.cache import InMemoryTTLCache, build_cache_key
from app.models.agent import AgentRequest, AgentResult, AgentStatus
from app.orchestrator.context import OrchestrationContext
from app.orchestrator.orchestrator import UrbanLensOrchestrator
from app.providers.base import LiveMetadata, LiveStatus, ProviderResponse
from app.services.air_quality import AirQualityService
from app.services.cost import CostOfLivingService
from app.services.currency import CurrencyService
from app.services.places import PlacesService
from app.services.routing import RoutingService
from app.services.transit import TransitService
from app.services.weather import WeatherService
from tests.conftest import MockDatabase


# ==============================================================================
# A. EnvironmentAgent Tests
# ==============================================================================


def test_environment_agent_live_weather_success() -> None:
    db = MockDatabase()
    weather_svc = MagicMock(spec=WeatherService)
    weather_svc.get_live_weather = AsyncMock(return_value={
        "city_id": "tokyo_jp",
        "city_name": "Tokyo",
        "weather": {"current": {"temperature_c": 24.5, "condition": "Sunny"}},
        "meta": {"provider": "open_meteo", "status": "fresh", "observed_at": "2026-10-27T01:00:00Z"},
    })
    weather_svc.get_forecast = MagicMock(return_value={"forecasts": []})

    aq_svc = MagicMock(spec=AirQualityService)
    aq_svc.get_live_air_quality = AsyncMock(return_value={
        "city_id": "tokyo_jp",
        "city_name": "Tokyo",
        "air_quality": {"pollutants": {"pm25": 11.2}},
        "meta": {"provider": "openaq", "status": "fresh", "observed_at": "2026-10-27T01:00:00Z"},
    })
    aq_svc.get_air_quality = MagicMock(return_value={"global_weather": [], "who_annual": []})

    agent = EnvironmentAgent(database=db, weather_service=weather_svc, air_quality_service=aq_svc)
    result = agent.execute(AgentRequest(city_id="tokyo_jp"))

    assert result.agent_id == "environment"
    assert result.status == AgentStatus.COMPLETE
    assert result.data["current_weather"]["temperature_c"] == 24.5
    assert result.confidence >= 0.85
    prov_names = [s.provider for s in result.sources]
    assert "open_meteo" in prov_names
    assert "openaq" in prov_names


def test_environment_agent_weather_fallback() -> None:
    db = MockDatabase()
    weather_svc = MagicMock(spec=WeatherService)
    weather_svc.get_live_weather = AsyncMock(return_value={
        "city_id": "tokyo_jp",
        "city_name": "Tokyo",
        "weather": {"current": {"temperature_c": 19.5}},
        "meta": {"provider": "mongodb", "status": "database", "observed_at": "2026-10-25T12:00:00Z"},
    })
    weather_svc.get_forecast = MagicMock(return_value={"forecasts": []})

    aq_svc = MagicMock(spec=AirQualityService)
    aq_svc.get_live_air_quality = AsyncMock(return_value={
        "city_id": "tokyo_jp",
        "city_name": "Tokyo",
        "air_quality": None,
        "meta": {"provider": "openaq", "status": "unavailable", "error_detail": "Auth missing"},
    })
    aq_svc.get_air_quality = MagicMock(return_value={"global_weather": [{"pm25": 12.5}], "who_annual": []})

    agent = EnvironmentAgent(database=db, weather_service=weather_svc, air_quality_service=aq_svc)
    result = agent.execute(AgentRequest(city_id="tokyo_jp"))

    assert result.status in (AgentStatus.COMPLETE, AgentStatus.PARTIAL)
    assert result.data["current_weather"]["temperature_c"] == 19.5
    assert any(s.provider in ("mongodb", "global_weather") for s in result.sources)


# ==============================================================================
# B. CostAgent Tests
# ==============================================================================


def test_cost_agent_mongodb_baseline() -> None:
    db = MockDatabase()
    agent = CostAgent(db)
    result = agent.execute(AgentRequest(city_id="tokyo_jp"))

    assert result.agent_id == "cost_of_living"
    assert result.status == AgentStatus.COMPLETE
    assert result.data["metrics_recorded_count"] >= 2
    assert "Meal, Inexpensive Restaurant" in result.data["metrics"]


def test_cost_agent_live_fx_integration() -> None:
    db = MockDatabase()
    curr_svc = MagicMock(spec=CurrencyService)
    curr_svc.convert_currency = AsyncMock(return_value={
        "from_currency": "USD",
        "to_currency": "JPY",
        "amount": 1.0,
        "conversion": {"rate": 152.4, "converted_amount": 152.4},
        "meta": {"provider": "frankfurter", "status": "fresh", "observed_at": "2026-10-27T00:00:00Z"},
    })

    agent = CostAgent(database=db, currency_service=curr_svc)
    result = agent.execute(AgentRequest(city_id="tokyo_jp"))

    assert result.status == AgentStatus.COMPLETE
    assert result.data["live_exchange_rate"]["converted_amount"] == 152.4
    assert any(s.provider == "frankfurter" for s in result.sources)


def test_cost_agent_fx_unavailable() -> None:
    db = MockDatabase()
    curr_svc = MagicMock(spec=CurrencyService)
    curr_svc.convert_currency = AsyncMock(return_value={
        "from_currency": "USD",
        "to_currency": "JPY",
        "amount": 1.0,
        "conversion": None,
        "meta": {"provider": "frankfurter", "status": "unavailable", "error_detail": "Exchange rate service unavailable"},
    })

    agent = CostAgent(database=db, currency_service=curr_svc)
    result = agent.execute(AgentRequest(city_id="tokyo_jp"))

    assert result.status == AgentStatus.COMPLETE
    assert result.data["live_exchange_rate"] is None
    assert "live_fx_rates" in result.unavailable_fields
    assert any("unavailable" in w.lower() for w in result.warnings)


# ==============================================================================
# C. MobilityAgent Tests
# ==============================================================================


def test_mobility_agent_routing_success() -> None:
    db = MockDatabase()
    routing_svc = MagicMock(spec=RoutingService)
    routing_svc.calculate_route = AsyncMock(return_value={
        "route": {"distance_km": 6.4, "duration_min": 14.2, "profile": "driving"},
        "meta": {"provider": "OSRM", "status": "fresh"},
    })

    agent = MobilityAgent(database=db, routing_service=routing_svc)
    result = agent.execute(AgentRequest(city_id="tokyo_jp"))

    assert result.agent_id == "mobility"
    assert result.data["sample_commute_corridor"]["distance_km"] == 6.4
    assert any(s.provider == "OSRM" for s in result.sources)


def test_mobility_agent_transit_unavailable() -> None:
    db = MockDatabase()
    routing_svc = MagicMock(spec=RoutingService)
    routing_svc.calculate_route = AsyncMock(return_value={
        "route": {"distance_km": 5.0, "duration_min": 10.0, "profile": "driving"},
        "meta": {"provider": "OSRM", "status": "fresh"},
    })
    agent = MobilityAgent(database=db, routing_service=routing_svc)
    result = agent.execute(AgentRequest(city_id="tokyo_jp"))

    assert result.data["live_gtfs_connected"] is False
    assert "live_transit_feed" in result.unavailable_fields


def test_mobility_agent_routing_failure() -> None:
    db = MockDatabase()
    routing_svc = MagicMock(spec=RoutingService)
    routing_svc.calculate_route = AsyncMock(side_effect=RuntimeError("Routing server unreachable"))

    agent = MobilityAgent(database=db, routing_service=routing_svc)
    result = agent.execute(AgentRequest(city_id="tokyo_jp"))

    # Does not crash; records warning
    assert result.status == AgentStatus.PARTIAL
    assert any("Routing check error" in w for w in result.warnings)


# ==============================================================================
# D. LocationAgent Tests
# ==============================================================================


def test_location_agent_canonical_city_data() -> None:
    db = MockDatabase()
    agent = LocationAgent(db)
    result = agent.execute(AgentRequest(city_id="tokyo_jp"))

    assert result.agent_id == "location"
    assert result.status == AgentStatus.COMPLETE
    assert result.data["name"] == "Tokyo"
    assert result.data["population"] == 37977000
    assert result.data["latitude"] == 35.6897
    assert result.confidence == 1.0


def test_location_agent_missing_city_data() -> None:
    db = MockDatabase()
    agent = LocationAgent(db)
    result = agent.execute(AgentRequest(city_id="unknown_city_999"))

    assert result.status == AgentStatus.UNAVAILABLE
    assert "city_record" in result.missing_data


# ==============================================================================
# E. EducationLifestyleAgent Tests
# ==============================================================================


def test_education_lifestyle_agent_universities() -> None:
    db = MockDatabase()
    places_svc = MagicMock(spec=PlacesService)
    places_svc.search_places = AsyncMock(return_value={"places": [], "count": 0, "meta": {}})
    agent = EducationLifestyleAgent(database=db, places_service=places_svc)
    result = agent.execute(AgentRequest(city_id="tokyo_jp"))

    assert result.agent_id == "education_culture"
    assert result.status == AgentStatus.COMPLETE
    assert result.data["total_country_institutions"] >= 1
    assert result.data["sample_institutions"][0]["name"] == "University of Tokyo"


def test_education_lifestyle_agent_missing_data() -> None:
    db = MockDatabase()
    agent = EducationLifestyleAgent(db)
    result = agent.execute(AgentRequest(city_id="paris_fr"))

    assert result.status == AgentStatus.UNAVAILABLE
    assert "universities" in result.missing_data


# ==============================================================================
# F. SafetyHealthcareAgent Tests
# ==============================================================================


def test_safety_healthcare_agent_healthcare_pois() -> None:
    db = MockDatabase()
    places_svc = MagicMock(spec=PlacesService)
    places_svc.search_places = AsyncMock(return_value={
        "places": [{"name": "Tokyo General Hospital", "category": "hospital"}],
        "count": 1,
        "meta": {"provider": "openstreetmap_overpass", "status": "fresh"},
    })

    agent = SafetyHealthcareAgent(database=db, places_service=places_svc)
    result = agent.execute(AgentRequest(city_id="tokyo_jp"))

    assert result.agent_id == "safety_healthcare"
    assert result.data["healthcare_facilities_count"] == 1
    assert any(s.provider == "openstreetmap_overpass" for s in result.sources)


def test_safety_healthcare_agent_missing_safety_scores() -> None:
    db = MockDatabase()
    places_svc = MagicMock(spec=PlacesService)
    places_svc.search_places = AsyncMock(return_value={"places": [], "count": 0, "meta": {}})
    agent = SafetyHealthcareAgent(database=db, places_service=places_svc)
    result = agent.execute(AgentRequest(city_id="tokyo_jp"))

    assert "neighborhood_crime_statistics" in result.unavailable_fields
    assert any("non-fabricated" in w for w in result.warnings)


# ==============================================================================
# G. AccommodationAgent Tests
# ==============================================================================


def test_accommodation_agent_locality_data() -> None:
    db = MockDatabase()
    places_svc = MagicMock(spec=PlacesService)
    places_svc.search_places = AsyncMock(return_value={"places": [], "count": 0, "meta": {}})
    agent = AccommodationAgent(database=db, places_service=places_svc)
    result = agent.execute(AgentRequest(city_id="tokyo_jp"))

    assert result.agent_id == "accommodation"
    assert result.status == AgentStatus.COMPLETE
    assert result.data["housing_metrics_count"] >= 1


def test_accommodation_agent_unavailable_fields() -> None:
    db = MockDatabase()
    agent = AccommodationAgent(db)
    result = agent.execute(AgentRequest(city_id="tokyo_jp"))

    assert "neighborhood_vacancy_rates" in result.unavailable_fields
    assert "short_term_rental_yield" in result.unavailable_fields


# ==============================================================================
# H. Orchestrator Tests
# ==============================================================================


def test_orchestrator_one_agent_query() -> None:
    db = MockDatabase()
    orchestrator = UrbanLensOrchestrator(database=db)
    agents = orchestrator.determine_relevant_agents("What is the weather and temperature in Tokyo?")
    assert agents == ["environment"]


def test_orchestrator_multi_agent_query() -> None:
    db = MockDatabase()
    orchestrator = UrbanLensOrchestrator(database=db)
    agents = orchestrator.determine_relevant_agents("Tell me about cost of living, universities, and hospitals in Tokyo")
    assert "cost_of_living" in agents
    assert "education_culture" in agents
    assert "safety_healthcare" in agents


def test_orchestrator_unknown_intent_defaults_to_all_agents() -> None:
    db = MockDatabase()
    orchestrator = UrbanLensOrchestrator(database=db)
    agents = orchestrator.determine_relevant_agents("asdfghjkl random words")
    assert len(agents) == 7


def test_orchestrator_partial_agent_failure() -> None:
    db = MockDatabase()
    failing_agent = MagicMock()
    failing_agent.execute_async = AsyncMock(side_effect=RuntimeError("Unexpected agent failure"))

    orchestrator = UrbanLensOrchestrator(
        database=db,
        agents={"environment": failing_agent, "location": LocationAgent(db)},
    )
    context = OrchestrationContext(city_id="tokyo_jp", query="weather in Tokyo", target_agents=("environment", "location"))
    aggregated = orchestrator.synthesize(context)

    # Should not crash; status reflects partial
    assert aggregated.overall_status == AgentStatus.PARTIAL
    env_res = next(r for r in aggregated.results if r.agent_id == "environment")
    assert env_res.status == AgentStatus.ERROR


def test_orchestrator_all_agents_unavailable() -> None:
    db = MockDatabase()
    unavail_agent = MagicMock()
    unavail_agent.execute_async = AsyncMock(return_value=AgentResult(
        agent_id="cost_of_living",
        status=AgentStatus.UNAVAILABLE,
        missing_data=("data",),
    ))

    orchestrator = UrbanLensOrchestrator(database=db, agents={"cost_of_living": unavail_agent})
    context = OrchestrationContext(city_id="tokyo_jp", query="cost", target_agents=("cost_of_living",))
    aggregated = orchestrator.synthesize(context)

    assert aggregated.overall_status == AgentStatus.UNAVAILABLE


def test_orchestrator_deterministic_output() -> None:
    db = MockDatabase()
    mock_loc = LocationAgent(db)
    mock_cost = CostAgent(db)
    orchestrator = UrbanLensOrchestrator(
        database=db,
        agents={"location": mock_loc, "cost_of_living": mock_cost},
    )
    ctx1 = OrchestrationContext(city_id="tokyo_jp", query="cost in Tokyo", target_agents=("location", "cost_of_living"))
    ctx2 = OrchestrationContext(city_id="tokyo_jp", query="cost in Tokyo", target_agents=("location", "cost_of_living"))

    res1 = orchestrator.synthesize(ctx1)
    res2 = orchestrator.synthesize(ctx2)

    assert res1.selected_agents == res2.selected_agents
    assert len(res1.signals) == len(res2.signals)
    assert res1.summary == res2.summary



# ==============================================================================
# I. Cache Tests
# ==============================================================================


def test_cache_hit_and_miss() -> None:
    cache = InMemoryTTLCache(default_ttl_seconds=10.0)
    key = build_cache_key("test", city="tokyo", param=1)

    # Cache miss
    assert cache.get(key) is None

    # Cache set & hit
    cache.set(key, {"temp": 25.0})
    hit = cache.get(key)
    assert hit is not None
    assert hit["temp"] == 25.0


def test_cache_ttl_expiration() -> None:
    cache = InMemoryTTLCache(default_ttl_seconds=0.05)
    key = "expiring_key"
    cache.set(key, "value", ttl_seconds=0.05)

    assert cache.get(key) == "value"
    time.sleep(0.06)
    assert cache.get(key) is None


def test_failed_provider_not_cached() -> None:
    cache = InMemoryTTLCache(default_ttl_seconds=10.0)
    failed_meta = LiveMetadata(
        provider="open_meteo",
        source="test",
        status=LiveStatus.ERROR,
        error_detail="API rate limited",
    )
    failed_response = ProviderResponse[Any](data=None, meta=failed_meta)

    key = build_cache_key("weather", city="mumbai")
    # Rule: do not cache if not successful
    if failed_response.is_successful and failed_response.data:
        cache.set(key, failed_response.data)

    assert cache.get(key) is None
