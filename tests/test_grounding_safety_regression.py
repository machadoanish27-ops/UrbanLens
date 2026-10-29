"""Regression tests for Phase 6: LLM Grounding Safety and anti-hallucination policies."""

import asyncio
import pytest

from app.models.agent import AgentResult, AgentStatus, SourceProvenance
from app.orchestrator.result import AggregatedIntelligence
from app.providers.llm.mock import MockLLMProvider
from app.services.llm import LLMService


def test_llm_grounding_context_separates_data_tiers():
    """Verify build_grounding_context creates distinct sections for Structured DB, Live, and Unavailable."""
    llm_svc = LLMService(provider=MockLLMProvider())
    aggregated = AggregatedIntelligence(
        city_id="city_1392685764",
        overall_status=AgentStatus.COMPLETE,
        location={"name": "Tokyo", "country_iso2": "JP", "population": 37977000},
        results=[],
        signals=(
            {"domain": "location", "metric": "city_population_density", "value": "unavailable", "source": "canonical_city_record"},
            {"domain": "environment", "metric": "temperature_c", "value": 18.5, "source": "open_meteo_live"},
            {"domain": "education_culture", "metric": "national_official_languages", "value": "Japanese", "source": "un_iso_languages"},
        ),
        warnings=("Cost of living data is not currently available for this city.",),
    )

    sys_prompt, user_prompt = llm_svc.build_grounding_context(aggregated, "What languages are spoken in Tokyo?")
    assert "DATA TIERS" in sys_prompt
    assert "=== SECTION A: CANONICAL DATABASE BENCHMARKS ===" in user_prompt
    assert "=== SECTION B: LIVE API OBSERVATIONS ===" in user_prompt
    assert "=== SECTION E: UNAVAILABLE DATA AND WARNINGS ===" in user_prompt
    assert "national_official_languages = Japanese" in user_prompt
    assert "temperature_c = 18.5" in user_prompt


def test_llm_synthesize_grounded_answer_unsupported_query_warning():
    """Verify that queries with zero evidence produce honest unavailability warnings."""
    async def _test():
        llm_svc = LLMService(provider=MockLLMProvider())
        empty_aggregated = AggregatedIntelligence(
            city_id="city_unknown",
            overall_status=AgentStatus.UNAVAILABLE,
            location={"name": "Atlantis", "country_iso2": "N/A"},
            results=[],
            signals=(),
            knowledge_evidence=(),
            warnings=("Target location not found in canonical index.",),
        )

        res = await llm_svc.synthesize_grounded_answer(empty_aggregated, "Tell me about the mythical city of Atlantis.")
        assert "UrbanLens does not currently have verified city-level data for this" in res.answer
        assert res.confidence == 0.0
        assert any("UrbanLens does not currently have verified city-level data" in w for w in res.warnings)

    asyncio.run(_test())


def test_llm_synthesize_links_signals_as_evidence_when_model_evidence_is_empty():
    """Verify structured database signals are automatically linked to evidence_used if model returned empty array."""
    async def _test():
        llm_svc = LLMService(provider=MockLLMProvider())
        aggregated = AggregatedIntelligence(
            city_id="city_1392685764",
            overall_status=AgentStatus.COMPLETE,
            location={"name": "Tokyo", "country_iso2": "JP", "population": 37977000},
            results=[],
            signals=(
                {"domain": "education_culture", "metric": "national_official_languages", "value": "Japanese", "source": "un_iso_languages"},
            ),
            knowledge_evidence=(),
        )

        res = await llm_svc.synthesize_grounded_answer(aggregated, "What is the official language?")
        assert len(res.evidence_used) > 0
        assert res.evidence_used[0].source == "un_iso_languages"

    asyncio.run(_test())
