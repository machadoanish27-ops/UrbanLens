"""Verification script for Phase 7 Frontend - FastAPI communication and contracts."""

import sys
from fastapi.testclient import TestClient
from app.main import app

def run_checks():
    client = TestClient(app)
    print("Testing Phase 7 API endpoints and CORS configuration...")

    # 1. CORS Preflight Check
    res = client.options(
        "/api/v1/cities",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "authorization,content-type",
        },
    )
    assert res.status_code == 200, f"CORS options failed: {res.status_code}"
    cors_origin = res.headers.get("access-control-allow-origin")
    assert cors_origin in ("*", "http://localhost:5173"), f"Invalid CORS origin header: {cors_origin}"
    print(f"  [PASS] CORS preflight: allow-origin={cors_origin}")

    # 2. Health checks
    res = client.get("/health")
    assert res.status_code == 200, f"Health check failed: {res.status_code}"
    print(f"  [PASS] GET /health -> {res.json()['status']}")

    res = client.get("/health/db")
    assert res.status_code == 200, f"DB Health check failed: {res.status_code}"
    print(f"  [PASS] GET /health/db -> connected={res.json().get('connected')}")

    # 3. Cities search
    res = client.get("/api/v1/cities?q=Tokyo&page_size=5")
    assert res.status_code == 200, f"Cities search failed: {res.status_code}"
    data = res.json()
    assert data["success"] is True
    assert len(data["data"]) > 0
    print(f"  [PASS] GET /api/v1/cities?q=Tokyo -> found {len(data['data'])} cities (first: {data['data'][0]['name']})")

    # 4. City detail
    city_id = "city_1392685764"
    res = client.get(f"/api/v1/cities/{city_id}")
    assert res.status_code == 200, f"City detail failed: {res.status_code}"
    assert res.json()["data"]["name"] == "Tokyo"
    print(f"  [PASS] GET /api/v1/cities/{city_id} -> {res.json()['data']['name']}")

    # 5. Live weather
    res = client.get(f"/api/v1/cities/{city_id}/weather/live")
    assert res.status_code == 200, f"Live weather failed: {res.status_code}"
    w_data = res.json()["data"]
    print(f"  [PASS] GET /api/v1/cities/{city_id}/weather/live -> status={w_data['meta']['status']}, provider={w_data['meta']['provider']}")

    # 6. Air quality
    res = client.get(f"/api/v1/cities/{city_id}/air-quality")
    assert res.status_code == 200, f"Air quality failed: {res.status_code}"
    aq_data = res.json()["data"]
    print(f"  [PASS] GET /api/v1/cities/{city_id}/air-quality -> providers={aq_data.get('available_providers')}")

    # 7. Universities
    res = client.get(f"/api/v1/cities/{city_id}/universities")
    assert res.status_code == 200, f"Universities failed: {res.status_code}"
    print(f"  [PASS] GET /api/v1/cities/{city_id}/universities -> count={len(res.json()['data'])}")

    # 8. Cost of living
    res = client.get(f"/api/v1/cities/{city_id}/cost-of-living")
    assert res.status_code == 200, f"Cost of living failed: {res.status_code}"
    print(f"  [PASS] GET /api/v1/cities/{city_id}/cost-of-living -> metrics count={len(res.json()['data']['metrics'])}")

    # 9. Ask Intelligence endpoint contract
    res = client.post(
        "/api/v1/intelligence/ask",
        json={"query": "What is the population and weather of Tokyo?", "city_id": "city_1392685764"},
    )
    assert res.status_code == 200, f"Ask intelligence failed: {res.status_code}"
    ask_data = res.json()["data"]
    assert "answer" in ask_data
    assert "key_points" in ask_data
    assert "evidence_used" in ask_data
    assert "sources" in ask_data
    assert "llm" in ask_data
    print(f"  [PASS] POST /api/v1/intelligence/ask -> model={ask_data['llm']['model']}, latency={ask_data['llm']['latency_ms']}ms, confidence={ask_data['confidence']}")

    print("\nALL FRONTEND-BACKEND CONTRACT CHECKS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_checks()
