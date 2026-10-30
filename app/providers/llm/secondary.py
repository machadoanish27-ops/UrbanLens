"""Secondary LLM provider supporting standard OpenAI-compatible HTTP chat completion endpoints."""

from __future__ import annotations

import asyncio
import re
import time
from typing import Any
import httpx

from app.core.config import settings
from app.providers.llm.base import BaseLLMProvider, LLMResponse, LLMStatus


def _sanitize_message(msg: str, secret_key: str | None = None) -> str:
    """Mask credentials and bearer tokens from error messages."""
    sanitized = msg
    if secret_key and len(secret_key) > 6:
        sanitized = sanitized.replace(secret_key, "sec_***")
    sanitized = re.sub(r"sk-[A-Za-z0-9_-]{16,}", "sk-***", sanitized)
    sanitized = re.sub(r"Bearer\s+[A-Za-z0-9_.-]+", "Bearer ***", sanitized)
    return sanitized


class SecondaryLLMProvider(BaseLLMProvider):
    """Failover secondary LLM provider interfacing with OpenAI-compatible chat completion APIs."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
        timeout_seconds: float | None = None,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self.api_key = (
            api_key if api_key is not None else settings.SECONDARY_LLM_API_KEY
        )
        self.base_url = (
            base_url or settings.SECONDARY_LLM_BASE_URL
        ).rstrip("/")
        self.model = model or settings.SECONDARY_LLM_MODEL
        self.timeout_seconds = (
            timeout_seconds if timeout_seconds is not None else settings.SECONDARY_LLM_TIMEOUT_SECONDS
        )
        self._external_client = client

    @property
    def provider(self) -> str:
        return "secondary_llm"

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        temperature: float = 0.2,
        max_tokens: int = 2000,
    ) -> LLMResponse:
        """Execute chat completion request against secondary LLM endpoint."""
        start = time.perf_counter()

        if not self.api_key or not self.api_key.strip():
            return LLMResponse(
                text="",
                provider="secondary_llm",
                model=self.model,
                latency_ms=(time.perf_counter() - start) * 1000,
                status=LLMStatus.UNAVAILABLE,
                warnings=("Secondary LLM API key not configured.",),
                error_category="not_configured",
            )

        headers = {
            "Authorization": f"Bearer {self.api_key.strip()}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        endpoint_url = f"{self.base_url}/chat/completions"
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "response_format": {"type": "json_object"},
        }

        try:
            if self._external_client:
                response = await self._external_client.post(
                    endpoint_url,
                    json=payload,
                    headers=headers,
                    timeout=self.timeout_seconds,
                )
            else:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        endpoint_url,
                        json=payload,
                        headers=headers,
                        timeout=self.timeout_seconds,
                    )

            latency = (time.perf_counter() - start) * 1000

            if response.status_code == 401:
                return LLMResponse(
                    text="",
                    provider="secondary_llm",
                    model=self.model,
                    latency_ms=latency,
                    status=LLMStatus.UNAVAILABLE,
                    warnings=("Secondary LLM authentication failure (HTTP 401).",),
                    error_category="auth_error",
                )

            if response.status_code == 429:
                return LLMResponse(
                    text="",
                    provider="secondary_llm",
                    model=self.model,
                    latency_ms=latency,
                    status=LLMStatus.ERROR,
                    warnings=("Secondary LLM rate limit exceeded (HTTP 429).",),
                    error_category="rate_limit",
                )

            if response.status_code != 200:
                safe_err = _sanitize_message(response.text[:200], self.api_key)
                return LLMResponse(
                    text="",
                    provider="secondary_llm",
                    model=self.model,
                    latency_ms=latency,
                    status=LLMStatus.ERROR,
                    warnings=(f"Secondary LLM returned HTTP {response.status_code}: {safe_err}",),
                    error_category="status_error",
                )

            data = response.json()
            choices = data.get("choices") or []
            choice = choices[0] if choices else {}
            msg = choice.get("message") or {}
            text_content = msg.get("content") or ""
            finish_reason = choice.get("finish_reason")
            usage_dict = data.get("usage")

            return LLMResponse(
                text=text_content,
                provider="secondary_llm",
                model=self.model,
                usage=usage_dict,
                finish_reason=finish_reason,
                latency_ms=latency,
                status=LLMStatus.SUCCESS,
                warnings=(),
                error_category="none",
            )

        except httpx.TimeoutException:
            latency = (time.perf_counter() - start) * 1000
            return LLMResponse(
                text="",
                provider="secondary_llm",
                model=self.model,
                latency_ms=latency,
                status=LLMStatus.TIMEOUT,
                warnings=(f"Secondary LLM timed out after {self.timeout_seconds}s.",),
                error_category="timeout",
            )
        except Exception as exc:
            latency = (time.perf_counter() - start) * 1000
            safe_msg = _sanitize_message(str(exc), self.api_key)
            return LLMResponse(
                text="",
                provider="secondary_llm",
                model=self.model,
                latency_ms=latency,
                status=LLMStatus.ERROR,
                warnings=(f"Secondary LLM connection error: {safe_msg}",),
                error_category="connection_error",
            )
