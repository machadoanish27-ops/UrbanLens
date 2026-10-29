"""Tests for UrbanLens API foundation endpoints."""

import pytest
from fastapi.testclient import TestClient


def test_health_endpoint(client: TestClient) -> None:
    """Test standard application health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "urbanlens-api"
    assert "version" in data
    assert "X-Request-ID" in response.headers
    assert "X-Process-Time-MS" in response.headers


def test_health_db_endpoint(client: TestClient) -> None:
    """Test database health check returns valid JSON without leaking secrets."""
    response = client.get("/health/db")
    # Whether 200 (connected) or 503 (disconnected in offline/mock environment), response must be valid JSON
    assert response.status_code in (200, 503)
    data = response.json()
    assert "status" in data
    assert "database" in data
    assert "password" not in str(data).lower()
    assert "mongodb+srv" not in str(data).lower()


def test_cities_list_and_search(client: TestClient) -> None:
    """Test listing and filtering cities."""
    response = client.get("/api/v1/cities")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert len(body["data"]) >= 2
    assert body["meta"]["pagination"]["total"] >= 2

    # Query search
    search_resp = client.get("/api/v1/cities?q=Tokyo")
    assert search_resp.status_code == 200
    search_body = search_resp.json()
    assert len(search_body["data"]) == 1
    assert search_body["data"][0]["city_id"] == "tokyo_jp"


def test_city_details_and_alias_resolution(client: TestClient) -> None:
    """Test getting single city by canonical ID and alias."""
    response = client.get("/api/v1/cities/tokyo_jp")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["city_id"] == "tokyo_jp"
    assert len(body["data"]["aliases"]) >= 1

    # Alias resolution
    alias_resp = client.get("/api/v1/cities/Tokio")
    assert alias_resp.status_code == 200
    alias_body = alias_resp.json()
    assert alias_body["data"]["city_id"] == "tokyo_jp"


def test_city_not_found(client: TestClient) -> None:
    """Test 404 error format for non-existent city."""
    response = client.get("/api/v1/cities/non_existent_city")
    assert response.status_code == 404
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "RESOURCE_NOT_FOUND"
    assert "non_existent_city" in body["error"]["message"]


def test_city_overview(client: TestClient) -> None:
    """Test multi-dimensional city overview synthesis."""
    response = client.get("/api/v1/cities/tokyo_jp/overview")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    data = body["data"]
    assert data["city"]["city_id"] == "tokyo_jp"
    assert data["weather_summary"] is not None
    assert data["weather_summary"]["temperature_c"] == 19.5
    assert data["cost_of_living_summary"]["available"] is True


def test_countries_endpoints(client: TestClient) -> None:
    """Test country listing, details, and metrics."""
    # List countries
    list_resp = client.get("/api/v1/countries")
    assert list_resp.status_code == 200
    body = list_resp.json()
    assert body["success"] is True
    assert len(body["data"]) >= 2

    # Country details
    country_resp = client.get("/api/v1/countries/japan")
    assert country_resp.status_code == 200
    assert country_resp.json()["data"]["country_id"] == "japan"

    # Country metrics
    metrics_resp = client.get("/api/v1/countries/japan/metrics")
    assert metrics_resp.status_code == 200
    metrics_body = metrics_resp.json()
    assert metrics_body["data"]["country_id"] == "japan"
    assert len(metrics_body["data"]["metrics"]) >= 1
    assert len(metrics_body["data"]["gdp_metrics"]) >= 1


def test_country_not_found(client: TestClient) -> None:
    """Test country 404."""
    response = client.get("/api/v1/countries/atlantis")
    assert response.status_code == 404
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "RESOURCE_NOT_FOUND"


def test_weather_endpoints(client: TestClient) -> None:
    """Test weather observations and forecasts."""
    # Observation
    weather_resp = client.get("/api/v1/cities/tokyo_jp/weather")
    assert weather_resp.status_code == 200
    body = weather_resp.json()
    assert body["success"] is True
    assert body["data"]["latest"]["temperature_c"] == 19.5
    assert body["data"]["latest"]["provider"] == "global_weather"

    # Forecast
    forecast_resp = client.get("/api/v1/cities/tokyo_jp/weather/forecast")
    assert forecast_resp.status_code == 200
    forecast_body = forecast_resp.json()
    assert len(forecast_body["data"]["forecasts"]) >= 1
    assert forecast_body["data"]["forecasts"][0]["condition"] == "Clear"


def test_air_quality_endpoint(client: TestClient) -> None:
    """Test air quality endpoint preserves distinct datasets."""
    response = client.get("/api/v1/cities/tokyo_jp/air-quality")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert len(body["data"]["global_weather"]) >= 1
    assert len(body["data"]["who_annual"]) >= 1
    assert "GlobalWeather" in body["data"]["available_providers"]
    assert "WHO" in body["data"]["available_providers"]


def test_cost_of_living_endpoint(client: TestClient) -> None:
    """Test cost of living endpoint and explicit unavailable status."""
    # Available city
    response = client.get("/api/v1/cities/tokyo_jp/cost-of-living")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["metric_count"] >= 2

    # Unindexed city -> 200 with status='unavailable' and honest warning
    unavail_resp = client.get("/api/v1/cities/paris_fr/cost-of-living")
    assert unavail_resp.status_code == 200
    unavail_body = unavail_resp.json()
    assert unavail_body["success"] is True
    assert unavail_body["data"]["is_available"] is False
    assert unavail_body["data"]["status"] == "unavailable"
    assert unavail_body["data"]["metric_count"] == 0
    assert "not currently available" in unavail_body["data"]["warning"]


def test_universities_endpoints(client: TestClient) -> None:
    """Test university queries and rankings."""
    # City universities
    univ_resp = client.get("/api/v1/cities/tokyo_jp/universities")
    assert univ_resp.status_code == 200
    body = univ_resp.json()
    assert len(body["data"]) >= 1
    assert body["data"][0]["university_id"] == "u_tokyo"

    # University details
    detail_resp = client.get("/api/v1/universities/u_tokyo")
    assert detail_resp.status_code == 200
    detail_body = detail_resp.json()
    assert detail_body["data"]["name"] == "University of Tokyo"
    assert len(detail_body["data"]["rankings"]) >= 1

    # Rankings
    rank_resp = client.get("/api/v1/universities/u_tokyo/rankings")
    assert rank_resp.status_code == 200
    rank_body = rank_resp.json()
    assert len(rank_body["data"]) >= 1
    assert rank_body["data"][0]["ranking_metric"] == "QS World University Rankings"


def test_intelligence_agent_endpoints(client: TestClient) -> None:
    """Test domain agent catalog and orchestrator query execution."""
    # Catalog
    catalog_resp = client.get("/api/v1/intelligence/agents")
    assert catalog_resp.status_code == 200
    catalog_body = catalog_resp.json()
    assert len(catalog_body["data"]) == 7

    # City intelligence query GET
    intel_resp = client.get("/api/v1/cities/tokyo_jp/intelligence")
    assert intel_resp.status_code == 200
    intel_body = intel_resp.json()
    assert intel_body["success"] is True
    assert intel_body["data"]["city_id"] == "tokyo_jp"
    assert len(intel_body["data"]["results"]) == 7

    # POST query with general relocation intent executes all 7 agents
    post_resp = client.post("/api/v1/intelligence/query", json={"city_id": "tokyo_jp", "query": "Should I move to Tokyo? Overview"})
    assert post_resp.status_code == 200
    post_body = post_resp.json()
    assert post_body["data"]["city_id"] == "tokyo_jp"
    assert len(post_body["data"]["results"]) == 7

    # Targeted query routes to relevant agents
    targeted_resp = client.post("/api/v1/intelligence/query", json={"city_id": "tokyo_jp", "query": "cost of living and universities"})
    assert targeted_resp.status_code == 200
    targeted_body = targeted_resp.json()
    assert set(targeted_body["data"]["selected_agents"]) == {"cost_of_living", "education_culture"}
    assert len(targeted_body["data"]["results"]) == 2



def test_pagination_validation_and_limits(client: TestClient) -> None:
    """Test pagination bounds enforcement."""
    # page=0 is rejected (ge=1 constraint)
    resp = client.get("/api/v1/cities?page=0")
    assert resp.status_code == 422

    # page_size=101 is rejected (le=100 constraint)
    resp_limit = client.get("/api/v1/cities?page_size=101")
    assert resp_limit.status_code == 422


def test_unhandled_exception_returns_clean_json(client: TestClient) -> None:
    """Test that unexpected internal errors return structured JSON without stack traces."""
    # Requesting with invalid university ID
    resp = client.get("/api/v1/universities/non_existent_id")
    assert resp.status_code == 404
    body = resp.json()
    assert body["success"] is False
    assert body["error"]["code"] == "RESOURCE_NOT_FOUND"
    assert "Traceback" not in str(body)

