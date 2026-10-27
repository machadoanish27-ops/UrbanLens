"""Mock LLM provider for deterministic offline testing."""

import asyncio
import json
import time
from typing import Any, Callable

from app.providers.llm.base import BaseLLMProvider, LLMResponse, LLMStatus


class MockLLMProvider(BaseLLMProvider):
    """Deterministic, mock LLM provider for offline testing."""

    def __init__(
        self,
        canned_response: str | dict[str, Any] | None = None,
        response_factory: Callable[[str, str], str | dict[str, Any]] | None = None,
        model: str = "mock-model",
        simulate_error: str | None = None,
        simulate_timeout: bool = False,
        simulate_unavailable: bool = False,
        delay_seconds: float = 0.0,
    ) -> None:
        self.model = model
        self.canned_response = canned_response
        self.response_factory = response_factory
        self.simulate_error = simulate_error
        self.simulate_timeout = simulate_timeout
        self.simulate_unavailable = simulate_unavailable
        self.delay_seconds = delay_seconds

        # Call tracking
        self.call_count: int = 0
        self.last_system_prompt: str | None = None
        self.last_user_prompt: str | None = None
        self.last_temperature: float | None = None
        self.last_max_tokens: int | None = None

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        temperature: float = 0.2,
        max_tokens: int = 2000,
    ) -> LLMResponse:
        """Simulate LLM generation."""
        self.call_count += 1
        self.last_system_prompt = system_prompt
        self.last_user_prompt = user_prompt
        self.last_temperature = temperature
        self.last_max_tokens = max_tokens

        start = time.perf_counter()

        if self.delay_seconds > 0:
            await asyncio.sleep(self.delay_seconds)

        if self.simulate_unavailable:
            return LLMResponse(
                text="",
                provider="mock",
                model=self.model,
                latency_ms=(time.perf_counter() - start) * 1000,
                status=LLMStatus.UNAVAILABLE,
                warnings=("Mock provider simulated unavailable state.",),
            )

        if self.simulate_timeout:
            return LLMResponse(
                text="",
                provider="mock",
                model=self.model,
                latency_ms=(time.perf_counter() - start) * 1000,
                status=LLMStatus.TIMEOUT,
                warnings=("Mock provider simulated request timeout.",),
            )

        if self.simulate_error:
            return LLMResponse(
                text="",
                provider="mock",
                model=self.model,
                latency_ms=(time.perf_counter() - start) * 1000,
                status=LLMStatus.ERROR,
                warnings=(f"Mock provider simulated error: {self.simulate_error}",),
            )

        # Produce response text
        if self.response_factory is not None:
            raw = self.response_factory(system_prompt, user_prompt)
            text = json.dumps(raw) if isinstance(raw, dict) else str(raw)
        elif self.canned_response is not None:
            text = (
                json.dumps(self.canned_response)
                if isinstance(self.canned_response, dict)
                else str(self.canned_response)
            )
        else:
            default_resp = {
                "answer": "Mock grounded answer based on supplied evidence.",
                "recommendation": "Mock recommendation.",
                "key_points": ["Point 1: Grounded evidence used.", "Point 2: Verified canonical baseline."],
                "evidence_used": [],
                "sources": ["Mock canonical registry"],
                "confidence": 0.95,
                "warnings": [],
            }
            text = json.dumps(default_resp)

        latency = (time.perf_counter() - start) * 1000
        return LLMResponse(
            text=text,
            provider="mock",
            model=self.model,
            usage={"prompt_tokens": 120, "completion_tokens": 65, "total_tokens": 185},
            finish_reason="stop",
            latency_ms=latency,
            status=LLMStatus.SUCCESS,
            warnings=(),
        )
