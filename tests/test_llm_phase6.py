"""Unit and integration test suite for Phase 6: Groq LLM Intelligence Layer."""

import asyncio
import json
from unittest.mock import AsyncMock, patch

import pytest
from starlette.testclient import TestClient

from app.core.cache import InMemoryTTLCache
from app.core.config import Settings
from app.models.agent import AgentResult, AgentStatus, SourceProvenance
from app.models.knowledge import KnowledgeEvidence
from app.orchestrator.context import OrchestrationContext
from app.orchestrator.orchestrator import UrbanLensOrchestrator
from app.orchestrator.result import AggregatedIntelligence
from app.providers.llm.base import BaseLLMProvider, LLMResponse, LLMStatus
from app.providers.llm.factory import get_llm_provider
from app.providers.llm.groq import GroqProvider, _sanitize_message
from app.providers.llm.mock import MockLLMProvider
from app.schemas.llm import (
    EvidenceUsedItem,
    LLMAskRequest,
    LLMAskResponse,
    LLMIntelligenceResponse,
    LLMMetadata,
)
from app.services.llm import LLMService
from tests.conftest import MockDatabase


# ==============================================================================
# 1. Base Provider & Mock Provider Tests
# ==============================================================================


def test_mock_llm_provider_generation() -> None:
    async def _test():
        provider = MockLLMProvider(model="mock-120b")
        resp = await provider.generate(
            system_prompt="System prompt",
            user_prompt="User question",
            temperature=0.3,
            max_tokens=500,
        )

        assert resp.status == LLMStatus.SUCCESS
        assert resp.provider == "mock"
        assert resp.model == "mock-120b"
        assert resp.latency_ms >= 0.0
        assert resp.usage is not None
        assert provider.call_count == 1
        assert provider.last_temperature == 0.3
        assert provider.last_max_tokens == 500

        # Validate that default mock response is valid JSON matching LLMIntelligenceResponse
        data = json.loads(resp.text)
        parsed = LLMIntelligenceResponse(**data)
        assert parsed.confidence > 0.0

    asyncio.run(_test())


def test_mock_llm_provider_timeout_and_error_simulation() -> None:
    async def _test():
        # Timeout simulation
        timeout_p = MockLLMProvider(simulate_timeout=True)
        t_resp = await timeout_p.generate("sys", "user")
        assert t_resp.status == LLMStatus.TIMEOUT
        assert "timeout" in t_resp.warnings[0].lower()

        # Error simulation
        error_p = MockLLMProvider(simulate_error="Internal gateway error")
        e_resp = await error_p.generate("sys", "user")
        assert e_resp.status == LLMStatus.ERROR
        assert "Internal gateway error" in e_resp.warnings[0]

        # Unavailable simulation
        unavail_p = MockLLMProvider(simulate_unavailable=True)
        u_resp = await unavail_p.generate("sys", "user")
        assert u_resp.status == LLMStatus.UNAVAILABLE

    asyncio.run(_test())


# ==============================================================================
# 2. Configuration & Settings Tests
# ==============================================================================


def test_llm_settings_loading_and_properties() -> None:
    s = Settings(
        LLM_PROVIDER="groq",
        LLM_MODEL="openai/gpt-oss-120b",
        LLM_TEMPERATURE=0.15,
        LLM_MAX_TOKENS=1500,
        LLM_TIMEOUT_SECONDS=25.0,
        GROQ_API_KEY="gsk_test_mock_secret_key_123456789",
    )

    # Upper and lowercase attribute access
    assert s.LLM_PROVIDER == "groq"
    assert s.llm_provider == "groq"
    assert s.llm_model == "openai/gpt-oss-120b"
    assert s.llm_temperature == 0.15
    assert s.llm_max_tokens == 1500
    assert s.llm_timeout_seconds == 25.0
    assert s.groq_api_key == "gsk_test_mock_secret_key_123456789"

    # Redaction property
    assert "gsk_" in s.safe_groq_api_key
    assert "mock_secret" not in s.safe_groq_api_key


# ==============================================================================
# 3. Provider Factory Tests
# ==============================================================================


def test_llm_provider_factory() -> None:
    mock_p = get_llm_provider("mock", model="custom-mock")
    assert isinstance(mock_p, MockLLMProvider)
    assert mock_p.model == "custom-mock"

    groq_p = get_llm_provider("groq", api_key="test_key", model="openai/gpt-oss-120b")
    assert isinstance(groq_p, GroqProvider)
    assert groq_p.model == "openai/gpt-oss-120b"

    with pytest.raises(ValueError, match="Unsupported LLM provider 'unsupported'"):
        get_llm_provider("unsupported")


# ==============================================================================
# 4. Groq Provider Missing Key & Secret Redaction Tests
# ==============================================================================


def test_groq_provider_missing_api_key_fails_gracefully() -> None:
    async def _test():
        # Empty API key must return UNAVAILABLE without raising exceptions
        provider = GroqProvider(api_key="")
        resp = await provider.generate("sys", "user")

        assert resp.status == LLMStatus.UNAVAILABLE
        assert "not configured" in resp.warnings[0]
        assert resp.text == ""

    asyncio.run(_test())


def test_secret_redaction_utility() -> None:
    secret = "gsk_supersecretkey123456789"
    raw_error = f"Request to Groq failed with key {secret} on header Authorization: Bearer {secret}"
    sanitized = _sanitize_message(raw_error, secret)

    assert secret not in sanitized
    assert "gsk_***" in sanitized


# ==============================================================================
# 5. Grounding Prompt & Context Package Generation
# ==============================================================================


def test_grounding_context_builder_separates_sources() -> None:
    agg = AggregatedIntelligence(
        city_id="tokyo_jp",
        overall_status=AgentStatus.COMPLETE,
        results=(
            AgentResult(
                agent_id="location",
                status=AgentStatus.COMPLETE,
                summary="Tokyo administrative overview.",
            ),
            AgentResult(
                agent_id="environment",
                status=AgentStatus.COMPLETE,
                summary="Current weather: 18C partly cloudy.",
            ),
        ),
        location={"name": "Tokyo", "country_iso2": "JP", "population": 37000000},
        signals=(
            {"domain": "location", "metric": "boundary", "value": "23 Special Wards", "source": "canonical_city_registry"},
            {"domain": "environment", "metric": "temperature_c", "value": 18.0, "source": "open-meteo"},
        ),
        knowledge_evidence=(
            KnowledgeEvidence(
                evidence_id="ev_doc1_chk0",
                document_id="doc1",
                chunk_id="chk0",
                title="Tokyo Metro Guide",
                source="Tokyo Bureau of Transportation",
                source_url="https://kotsu.metro.tokyo.jp",
                publisher="TMG",
                text="The Tokyo subway network operates 13 lines.",
                category="transport",
                city_id="tokyo_jp",
                country_id="japan",
                retrieval_score=0.45,
            ),
        ),
        sources=(
            SourceProvenance(source_id="canonical_city_registry", provider="mongodb"),
            SourceProvenance(source_id="open-meteo", provider="open-meteo"),
            SourceProvenance(source_id="Tokyo Bureau of Transportation", provider="knowledge"),
        ),
    )

    service = LLMService(provider=MockLLMProvider())
    sys_prompt, user_prompt = service.build_grounding_context(agg, "Tell me about Tokyo subway and weather")

    assert "STRICT GROUNDING RULES:" in sys_prompt
    assert "=== SECTION A: CANONICAL DATABASE BENCHMARKS ===" in user_prompt
    assert "=== SECTION B: LIVE API OBSERVATIONS ===" in user_prompt
    assert "=== SECTION C: RAG KNOWLEDGE EVIDENCE (DOCUMENT CHUNKS) ===" in user_prompt
    assert "=== SECTION D: DOMAIN AGENT EVALUATIONS ===" in user_prompt
    assert "Tokyo Metro Guide" in user_prompt
    assert "https://kotsu.metro.tokyo.jp" in user_prompt


def test_no_evidence_query_returns_insufficient_evidence() -> None:
    async def _test():
        agg = AggregatedIntelligence(
            city_id="unresolved_city",
            overall_status=AgentStatus.UNAVAILABLE,
            results=(),
            signals=(),
            knowledge_evidence=(),
            warnings=("Target city could not be resolved.",),
        )

        service = LLMService(provider=MockLLMProvider())
        resp = await service.synthesize_grounded_answer(agg, "What is the weather in Atlantis?")

        assert "Insufficient grounded evidence available" in resp.answer
        assert resp.confidence == 0.0
        assert resp.llm.status == "no_evidence"

    asyncio.run(_test())


# ==============================================================================
# 6. LLM Structured Output Parsing & Fallback Tests
# ==============================================================================


def test_llm_service_successful_structured_response() -> None:
    async def _test():
        structured_payload = {
            "answer": "Tokyo operates an extensive multi-modal transit network with 13 subway lines.",
            "recommendation": "Use a contactless IC card (Suica/Pasmo) for transit navigation.",
            "key_points": [
                "Subway network comprises 13 lines.",
                "Punctuality rate exceeds 99%.",
            ],
            "evidence_used": [
                {
                    "evidence_id": "ev_doc1_chk0",
                    "title": "Tokyo Transit Overview",
                    "source": "Tokyo Bureau of Transportation",
                    "source_url": "https://kotsu.metro.tokyo.jp",
                    "claim": "Tokyo subway has 13 lines.",
                }
            ],
            "sources": ["Tokyo Bureau of Transportation", "open-meteo"],
            "confidence": 0.98,
            "warnings": [],
        }

        mock_p = MockLLMProvider(canned_response=structured_payload)
        service = LLMService(provider=mock_p, cache=InMemoryTTLCache())

        agg = AggregatedIntelligence(
            city_id="tokyo_jp",
            overall_status=AgentStatus.COMPLETE,
            results=(),
            location={"name": "Tokyo", "country_iso2": "JP"},
            signals=({"domain": "transport", "metric": "subway_lines", "value": 13, "source": "canonical"},),
        )

        res = await service.synthesize_grounded_answer(agg, "Tokyo transport rules")

        assert res.city_id == "tokyo_jp"
        assert "Tokyo operates an extensive" in res.answer
        assert len(res.evidence_used) == 1
        assert res.evidence_used[0].source_url == "https://kotsu.metro.tokyo.jp"
        assert res.confidence == 0.98
        assert res.llm.status == "success"

    asyncio.run(_test())


def test_llm_service_fallback_on_invalid_json() -> None:
    async def _test():
        # Provider returns malformed non-JSON string
        mock_p = MockLLMProvider(canned_response="This is raw plain text without JSON markers.")
        service = LLMService(provider=mock_p, cache=InMemoryTTLCache())

        agg = AggregatedIntelligence(
            city_id="tokyo_jp",
            overall_status=AgentStatus.COMPLETE,
            results=(),
            location={"name": "Tokyo"},
            signals=({"domain": "location", "metric": "name", "value": "Tokyo", "source": "mongodb"},),
            summary="Deterministic Tokyo summary synthesized across agents.",
        )

        res = await service.synthesize_grounded_answer(agg, "Tokyo overview")

        # Must fall back gracefully without crashing
        assert "Deterministic Tokyo summary" in res.answer
        assert res.llm.status == "fallback"
        assert any("LLM synthesis unavailable" in w for w in res.warnings)

    asyncio.run(_test())


def test_llm_service_fallback_on_provider_error() -> None:
    async def _test():
        mock_p = MockLLMProvider(simulate_error="Connection refused to upstream")
        service = LLMService(provider=mock_p, cache=InMemoryTTLCache())

        agg = AggregatedIntelligence(
            city_id="tokyo_jp",
            overall_status=AgentStatus.COMPLETE,
            results=(),
            location={"name": "Tokyo"},
            summary="Deterministic baseline overview.",
        )

        res = await service.synthesize_grounded_answer(agg, "Tokyo overview")

        assert res.llm.status == "fallback"
        assert any("LLM synthesis unavailable" in w for w in res.warnings)
        assert "Deterministic baseline overview" in res.answer

    asyncio.run(_test())


def test_llm_service_in_memory_caching() -> None:
    async def _test():
        mock_p = MockLLMProvider(canned_response={"answer": "Cached answer test", "key_points": [], "evidence_used": [], "sources": [], "confidence": 0.9, "warnings": []})
        cache = InMemoryTTLCache(default_ttl_seconds=60.0)
        service = LLMService(provider=mock_p, cache=cache)

        agg = AggregatedIntelligence(
            city_id="tokyo_jp",
            overall_status=AgentStatus.COMPLETE,
            results=(),
            location={"name": "Tokyo"},
            signals=({"domain": "transport", "metric": "subway", "value": 13, "source": "canonical"},),
        )

        # 1st call executes provider
        res1 = await service.synthesize_grounded_answer(agg, "Tokyo caching test")
        assert res1.llm.cached is False
        assert mock_p.call_count == 1

        # 2nd call returns from cache
        res2 = await service.synthesize_grounded_answer(agg, "Tokyo caching test")
        assert res2.llm.cached is True
        assert mock_p.call_count == 1  # No additional provider call

    asyncio.run(_test())


# ==============================================================================
# 7. Orchestrator + LLM Integration Tests
# ==============================================================================


def test_orchestrator_ask_async_integration() -> None:
    async def _test():
        db = MockDatabase()
        mock_p = MockLLMProvider(
            canned_response={
                "answer": "Tokyo is verified as a global megacity with comprehensive transport networks.",
                "recommendation": "Plan commute routes via high-capacity rail lines.",
                "key_points": ["Megacity scale confirmed", "Live weather observed"],
                "evidence_used": [],
                "sources": ["canonical_city_registry"],
                "confidence": 0.95,
                "warnings": [],
            }
        )

        llm_svc = LLMService(provider=mock_p)
        orch = UrbanLensOrchestrator(database=db, llm_service=llm_svc)

        ask_res = await orch.ask_async(query="Should I move to Tokyo for work?", city_id="tokyo_jp")

        assert ask_res.city_id == "tokyo_jp"
        assert ask_res.city_name == "Tokyo"
        assert "Tokyo is verified as a global megacity" in ask_res.answer
        assert ask_res.llm.status == "success"
        assert mock_p.call_count == 1

    asyncio.run(_test())


# ==============================================================================
# 8. API Endpoint Tests (POST /api/v1/intelligence/ask)
# ==============================================================================


def test_api_intelligence_ask_endpoint(client: TestClient) -> None:
    # Test POST /api/v1/intelligence/ask with mock provider
    with patch("app.services.intelligence.IntelligenceService.ask_async") as mock_ask:
        mock_ask.return_value = LLMAskResponse(
            city_id="tokyo_jp",
            city_name="Tokyo",
            country="JP",
            query="Tell me about living in Tokyo",
            answer="Tokyo is an exceptionally safe and interconnected metropolitan area.",
            recommendation="Consider proximity to JR Yamanote line.",
            key_points=["Subway system spans 13 lines", "Low crime rates"],
            evidence_used=[
                EvidenceUsedItem(
                    evidence_id="ev_tokyo_transit",
                    title="Tokyo Transit System",
                    source="Tokyo Bureau of Transportation",
                    source_url="https://kotsu.metro.tokyo.jp",
                    claim="Subway system spans 13 lines",
                )
            ],
            sources=["Tokyo Bureau of Transportation", "canonical_registry"],
            confidence=0.96,
            warnings=[],
            llm=LLMMetadata(
                provider="groq",
                model="openai/gpt-oss-120b",
                status="success",
                latency_ms=45.2,
                cached=False,
            ),
        )

        payload = {"city_id": "tokyo_jp", "query": "Tell me about living in Tokyo"}
        resp = client.post("/api/v1/intelligence/ask", json=payload)

        assert resp.status_code == 200
        json_data = resp.json()
        assert json_data["success"] is True
        data = json_data["data"]
        assert data["city_id"] == "tokyo_jp"
        assert data["city_name"] == "Tokyo"
        assert "exceptionally safe" in data["answer"]
        assert len(data["evidence_used"]) == 1
        assert data["evidence_used"][0]["source_url"] == "https://kotsu.metro.tokyo.jp"
        assert data["llm"]["provider"] == "groq"
        assert data["llm"]["status"] == "success"
