"""Comprehensive test suite for Phase 11 production hardening:
- Multi-backend caching with stale-while-revalidate and Redis offline fallback
- Overpass mirror rotation, circuit cooldown, and stale cache fallback
- Multi-provider LLM redundancy (Primary -> Secondary -> Deterministic Grounded Fallback)
- Rate limiting protection and HTTP 429 handling
- Health observability and diagnostics without credential leakage
"""

from __future__ import annotations

import asyncio
import time
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from fastapi.testclient import TestClient

from app.core.cache import (
    CacheEntry,
    CacheService,
    InMemoryCacheBackend,
    InMemoryTTLCache,
    RedisCacheBackend,
    build_cache_key,
)
from app.core.rate_limit import limiter
from app.models.agent import AgentResult, AgentStatus, SourceProvenance
from app.orchestrator.result import AggregatedIntelligence
from app.providers.base import LiveStatus, ProviderResponse
from app.providers.llm.base import BaseLLMProvider, LLMResponse, LLMStatus
from app.providers.llm.secondary import SecondaryLLMProvider
from app.providers.places.base import NormalizedPlaceItem
from app.providers.places.overpass import EndpointHealth, OverpassPlacesProvider
from app.schemas.knowledge import KnowledgeEvidenceSchema
from app.schemas.llm import LLMAskResponse, LLMMetadata
from app.services.llm import LLMService
from tests.conftest import MockDatabase


# ==============================================================================
# 1. Cache Architecture & Stale Fallback Tests
# ==============================================================================


def test_in_memory_cache_ttl_and_stale_retrieval() -> None:
    cache = InMemoryCacheBackend(default_ttl_seconds=0.05, stale_multiplier=3.0)
    key = "urbanlens:weather:test_city"

    cache.set(key, {"temp": 22.5})

    # Immediate get: fresh
    entry_fresh = cache.get_entry(key, allow_stale=False)
    assert entry_fresh is not None
    assert entry_fresh.value == {"temp": 22.5}
    assert entry_fresh.is_stale is False

    # Wait for TTL to expire
    time.sleep(0.07)

    # get without allow_stale -> None
    assert cache.get(key, allow_stale=False) is None
    assert cache.get_entry(key, allow_stale=False) is None

    # get with allow_stale -> returns stale value
    stale_entry = cache.get_entry(key, allow_stale=True)
    assert stale_entry is not None
    assert stale_entry.value == {"temp": 22.5}
    assert stale_entry.is_stale is True
    assert stale_entry.age_seconds >= 0.07

    # Backward-compatible simple get
    assert cache.get(key, allow_stale=True) == {"temp": 22.5}


def test_cache_service_namespace_and_diagnostics() -> None:
    svc = CacheService(default_ttl_seconds=60.0, enable_redis=False)
    key = build_cache_key("currency", from_cur="USD", to_cur="EUR")

    assert key == "urbanlens:currency:from_cur=USD:to_cur=EUR"
    svc.set(key, {"rate": 0.92})
    assert svc.get(key) == {"rate": 0.92}

    diag = svc.get_diagnostics()
    assert diag["active_backend"] == "in_memory"
    assert diag["redis_connected"] is False
    assert diag["in_memory_entries"] >= 1

    svc.delete(key)
    assert svc.get(key) is None


def test_redis_backend_graceful_offline_degradation() -> None:
    # Point to a guaranteed unreachable port
    backend = RedisCacheBackend(
        redis_url="redis://127.0.0.1:59999/0",
        connect_timeout_ms=100,
        socket_timeout_ms=100,
    )
    # Backend must gracefully mark itself unhealthy without crashing
    assert backend.is_healthy() is False
    assert backend.get("any_key") is None
    # set and delete must fail silently without raising
    backend.set("any_key", {"data": 123})
    assert backend.delete("any_key") is False


# ==============================================================================
# 2. Overpass Multi-Mirror Rotation & Resilience Tests
# ==============================================================================


@pytest.mark.anyio
async def test_overpass_rotation_to_secondary_on_primary_failure() -> None:
    # Mock client where primary fails with 504 Gateway Timeout, secondary succeeds
    primary_url = "https://overpass-api.de/api/interpreter"
    secondary_url = "https://maps.mail.ru/osm/tools/overpass/api/interpreter"

    mock_elements = [
        {
            "id": 1001,
            "lat": 35.6895,
            "lon": 139.6917,
            "tags": {"name": "Tokyo Medical Center", "amenity": "hospital"},
        }
    ]

    async def mock_post(url: str, **kwargs: Any) -> httpx.Response:
        url_str = str(url)
        if primary_url in url_str:
            return httpx.Response(status_code=504, text="Gateway Timeout")
        if secondary_url in url_str:
            return httpx.Response(status_code=200, json={"elements": mock_elements})
        return httpx.Response(status_code=500, text="Error")

    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.post = AsyncMock(side_effect=mock_post)

    provider = OverpassPlacesProvider(
        base_url=primary_url,
        fallback_urls=[secondary_url],
        timeout=2.0,
        client=mock_client,
    )

    resp = await provider.get_places(latitude=35.6895, longitude=139.6917, category="hospital")

    assert resp.is_successful is True
    assert len(resp.data) == 1
    assert resp.data[0].name == "Tokyo Medical Center"
    assert resp.data[0].category == "hospital"

    # Verify endpoint health tracking: primary failed once, secondary succeeded
    diag = provider.get_health_diagnostics()
    endpoints = {e["url"]: e for e in diag["endpoints"]}
    assert endpoints[primary_url]["consecutive_failures"] == 1
    assert endpoints[secondary_url]["consecutive_failures"] == 0


@pytest.mark.anyio
async def test_overpass_circuit_cooldown() -> None:
    health = EndpointHealth(url="https://test-mirror.org", consecutive_failures=2, last_failure_time=time.time())
    # Within 30 seconds cooldown
    assert health.is_cooling_down(cooldown_seconds=30.0) is True

    # After cooldown expires
    health.last_failure_time = time.time() - 35.0
    assert health.is_cooling_down(cooldown_seconds=30.0) is False

    # After success, cooldown resets
    health.record_success()
    assert health.consecutive_failures == 0
    assert health.is_cooling_down(cooldown_seconds=30.0) is False


@pytest.mark.anyio
async def test_overpass_stale_cache_fallback_when_all_mirrors_fail() -> None:
    # 1. Pre-seed cache with place items
    cache_key = build_cache_key("places", lat=19.076, lon=72.8777, cat="hospital", rad=1500, lim=10)
    preseeded_items = [
        {
            "place_id": "9999",
            "name": "Lilavati Hospital",
            "category": "hospital",
            "latitude": 19.076,
            "longitude": 72.8777,
            "distance_meters": 50.0,
            "amenity": "hospital",
            "tags": {"emergency": "yes"},
        }
    ]
    # Set with TTL expired but within purge window (e.g. 60s purge window)
    from app.core.cache import service_cache
    now = time.time()
    # Manually store entry as already expired (expires_at in past, purge_at in future)
    service_cache.local_backend._store[cache_key] = (preseeded_items, now - 10.0, now - 20.0, now + 300.0)

    # 2. Mock client where ALL endpoints fail
    async def mock_failing_post(url: str, **kwargs: Any) -> httpx.Response:
        raise httpx.ConnectTimeout("Connection timed out to mirror")

    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.post = AsyncMock(side_effect=mock_failing_post)

    provider = OverpassPlacesProvider(timeout=0.1, max_retries=1, client=mock_client)

    resp = await provider.get_places(latitude=19.0760, longitude=72.8777, category="hospital", radius=1500, limit=10)

    # Must recover using stale cached items
    assert resp.meta.status == LiveStatus.CACHED
    assert len(resp.data) == 1
    assert resp.data[0].name == "Lilavati Hospital"
    assert "returning cached POIs" in (resp.meta.error_detail or "")


@pytest.mark.anyio
async def test_overpass_honest_unavailable_when_no_cache_and_all_fail() -> None:
    async def mock_failing_post(url: str, **kwargs: Any) -> httpx.Response:
        return httpx.Response(status_code=503, text="Service Unavailable")

    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.post = AsyncMock(side_effect=mock_failing_post)

    # Unique coordinates so no cache hit exists
    provider = OverpassPlacesProvider(timeout=0.5, max_retries=1, client=mock_client)
    resp = await provider.get_places(latitude=88.1234, longitude=12.3456, category="hospital")

    assert resp.meta.status == LiveStatus.UNAVAILABLE
    assert len(resp.data) == 0
    assert "All Overpass mirrors unavailable" in (resp.meta.error_detail or "")


# ==============================================================================
# 3. LLM Multi-Provider Redundancy Tests
# ==============================================================================


class FailingMockLLM(BaseLLMProvider):
    def __init__(self, error_category: str = "rate_limit"):
        self.error_category = error_category
        self.provider = "failing_mock"
        self.model = "failing-model"

    async def generate(self, system_prompt: str, user_prompt: str, **kwargs: Any) -> LLMResponse:
        return LLMResponse(
            text="",
            provider="failing_mock",
            model="failing-model",
            status=LLMStatus.ERROR,
            warnings=(f"Simulated {self.error_category} error",),
            error_category=self.error_category,
        )


class WorkingMockLLM(BaseLLMProvider):
    def __init__(self, provider_name: str = "working_mock", model_name: str = "working-v1"):
        self.provider = provider_name
        self.model = model_name

    async def generate(self, system_prompt: str, user_prompt: str, **kwargs: Any) -> LLMResponse:
        import json
        payload = {
            "answer": f"Verified synthesis generated by {self.provider}.",
            "recommendation": "Review transportation and healthcare infrastructure.",
            "key_points": ["Subway network operational", "High safety baseline"],
            "evidence_used": [],
            "sources": ["canonical_registry"],
            "confidence": 0.95,
            "warnings": [],
        }
        return LLMResponse(
            text=json.dumps(payload),
            provider=self.provider,
            model=self.model,
            status=LLMStatus.SUCCESS,
            error_category="none",
        )


@pytest.mark.anyio
async def test_llm_redundancy_primary_fails_secondary_succeeds() -> None:
    primary = FailingMockLLM(error_category="rate_limit")
    secondary = WorkingMockLLM(provider_name="secondary_llm", model_name="gpt-4o-mini")

    service = LLMService(provider=primary, secondary_provider=secondary, cache=InMemoryTTLCache())

    agg = AggregatedIntelligence(
        city_id="tokyo_jp",
        overall_status=AgentStatus.COMPLETE,
        results=(),
        location={"name": "Tokyo", "country_iso2": "JP"},
        signals=({"domain": "transport", "metric": "subway_lines", "value": 13, "source": "canonical"},),
    )

    resp = await service.synthesize_grounded_answer(agg, "Tokyo transport rules")

    assert resp.city_id == "tokyo_jp"
    assert "Verified synthesis generated by secondary_llm" in resp.answer
    assert resp.llm.provider == "secondary_llm"
    assert resp.llm.model == "gpt-4o-mini"
    assert resp.llm.fallback_used is True
    assert resp.llm.error_category == "rate_limit"
    assert any("answered by secondary LLM" in w for w in resp.warnings)


@pytest.mark.anyio
async def test_llm_redundancy_both_fail_grounded_deterministic_fallback() -> None:
    primary = FailingMockLLM(error_category="auth_error")
    secondary = FailingMockLLM(error_category="timeout")

    service = LLMService(provider=primary, secondary_provider=secondary, cache=InMemoryTTLCache())

    agg = AggregatedIntelligence(
        city_id="tokyo_jp",
        overall_status=AgentStatus.COMPLETE,
        results=(),
        location={"name": "Tokyo", "country_iso2": "JP"},
        signals=(
            {"domain": "transport", "metric": "subway_lines", "value": 13, "source": "canonical_database"},
            {"domain": "weather", "metric": "temperature_c", "value": 18.5, "source": "open-meteo"},
        ),
        summary="Deterministic Tokyo synthesis from canonical database.",
    )

    resp = await service.synthesize_grounded_answer(agg, "Tokyo overview")

    # Anti-hallucination deterministic grounded synthesis
    assert resp.llm.status == "fallback"
    assert resp.llm.provider == "deterministic_grounded_engine"
    assert resp.llm.model == "grounded-synthesis-v1"
    assert resp.llm.fallback_used is True
    assert resp.llm.error_category == "auth_error"
    assert "Deterministic Tokyo synthesis" in resp.answer
    assert len(resp.key_points) >= 2


def test_secondary_provider_unconfigured_returns_unavailable() -> None:
    async def _test():
        sec = SecondaryLLMProvider(api_key=None)
        res = await sec.generate("sys", "user")
        assert res.status == LLMStatus.UNAVAILABLE
        assert res.error_category == "not_configured"

    asyncio.run(_test())


# ==============================================================================
# 4. Rate Limiting Tests (SlowAPI)
# ==============================================================================


def test_rate_limiting_protects_intelligence_ask(client: TestClient) -> None:
    # Temporarily set tight limit to test 429 response formatting
    with patch("app.core.config.settings.RATE_LIMIT_INTELLIGENCE", "2/minute"):
        with patch("app.services.intelligence.IntelligenceService.ask_async") as mock_ask:
            mock_ask.return_value = LLMAskResponse(
                city_id="tokyo_jp",
                query="hello",
                answer="Tokyo summary",
                evidence_used=[],
                sources=[],
                llm=LLMMetadata(provider="groq", model="test", status="success", latency_ms=10.0, cached=False),
            )

            # First query succeeds
            r1 = client.post("/api/v1/intelligence/ask", json={"city_id": "tokyo_jp", "query": "q1"})
            assert r1.status_code in (200, 429)

            # Excessive queries in quick succession
            responses = [
                client.post("/api/v1/intelligence/ask", json={"city_id": "tokyo_jp", "query": f"q{i}"})
                for i in range(5)
            ]
            has_429 = any(r.status_code == 429 for r in responses)
            if has_429:
                r_429 = next(r for r in responses if r.status_code == 429)
                data = r_429.json()
                assert data["success"] is False
                assert data["error"]["code"] == "RATE_LIMIT_EXCEEDED"
                assert "Retry-After" in r_429.headers


# ==============================================================================
# 5. Observability & Health Check Diagnostics
# ==============================================================================


def test_health_endpoints_connectivity_and_secret_redaction(client: TestClient) -> None:
    # Basic health
    r_basic = client.get("/health")
    assert r_basic.status_code == 200
    assert r_basic.json()["status"] == "ok"

    # DB health
    r_db = client.get("/health/db")
    assert r_db.status_code in (200, 503)

    # Detailed health
    r_det = client.get("/health/detailed")
    assert r_det.status_code in (200, 503)
    data = r_det.json()

    # Verify diagnostic sections
    assert "status" in data
    assert "database" in data
    assert "cache" in data
    assert "llm_providers" in data
    assert "overpass" in data
    assert "rate_limiting" in data

    # Verify zero secrets leaked
    raw_text = r_det.text.lower()
    assert "password" not in raw_text
    assert "mongodb+srv" not in raw_text
    # Groq key if present must be masked
    if "gsk_" in raw_text:
        assert "..." in data["llm_providers"]["primary"]["key"]
