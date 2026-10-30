"""Groq LLM provider implementation using official Groq SDK."""

import asyncio
import re
import time
from typing import Any

from app.core.config import settings
from app.providers.llm.base import BaseLLMProvider, LLMResponse, LLMStatus


def _sanitize_message(msg: str, secret_key: str | None = None) -> str:
    """Remove potential API keys or tokens from error messages."""
    sanitized = msg
    if secret_key and len(secret_key) > 6:
        sanitized = sanitized.replace(secret_key, "gsk_***")
    # Mask gsk_... tokens
    sanitized = re.sub(r"gsk_[A-Za-z0-9_-]{16,}", "gsk_***", sanitized)
    return sanitized


class GroqProvider(BaseLLMProvider):
    """Production Groq LLM provider with bounded execution and safe error handling."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        timeout_seconds: float | None = None,
    ) -> None:
        self.api_key = api_key if api_key is not None else settings.GROQ_API_KEY
        self.model = model if model is not None else settings.LLM_MODEL
        self.timeout_seconds = (
            timeout_seconds if timeout_seconds is not None else settings.LLM_TIMEOUT_SECONDS
        )

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        temperature: float = 0.2,
        max_tokens: int = 2000,
    ) -> LLMResponse:
        """Execute chat completion request against Groq API."""
        start = time.perf_counter()

        if not self.api_key or not self.api_key.strip():
            return LLMResponse(
                text="",
                provider="groq",
                model=self.model,
                latency_ms=(time.perf_counter() - start) * 1000,
                status=LLMStatus.UNAVAILABLE,
                warnings=("Groq API key not configured. LLM synthesis unavailable.",),
                error_category="not_configured",
            )

        try:
            from groq import (
                APIConnectionError,
                APIStatusError,
                APITimeoutError,
                AsyncGroq,
                AuthenticationError,
                RateLimitError,
            )
        except ImportError:
            return LLMResponse(
                text="",
                provider="groq",
                model=self.model,
                latency_ms=(time.perf_counter() - start) * 1000,
                status=LLMStatus.UNAVAILABLE,
                warnings=("groq python SDK not installed. Run 'pip install groq'.",),
                error_category="sdk_missing",
            )

        client = AsyncGroq(api_key=self.api_key.strip(), timeout=self.timeout_seconds)

        try:
            # Bounded retry: 1 initial attempt + 1 retry on transient connection error
            max_attempts = 2
            last_exc: Exception | None = None

            for attempt in range(1, max_attempts + 1):
                try:
                    response = await client.chat.completions.create(
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt},
                        ],
                        model=self.model,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        response_format={"type": "json_object"},
                    )

                    latency = (time.perf_counter() - start) * 1000
                    choice = response.choices[0] if response.choices else None
                    text_content = choice.message.content or "" if choice else ""
                    finish_reason = choice.finish_reason if choice else None

                    usage_dict = None
                    if response.usage:
                        usage_dict = {
                            "prompt_tokens": response.usage.prompt_tokens or 0,
                            "completion_tokens": response.usage.completion_tokens or 0,
                            "total_tokens": response.usage.total_tokens or 0,
                        }

                    return LLMResponse(
                        text=text_content,
                        provider="groq",
                        model=self.model,
                        usage=usage_dict,
                        finish_reason=finish_reason,
                        latency_ms=latency,
                        status=LLMStatus.SUCCESS,
                        warnings=(),
                    )

                except (APIConnectionError, APITimeoutError) as transient_err:
                    last_exc = transient_err
                    if attempt < max_attempts:
                        await asyncio.sleep(0.5)
                        continue
                    raise transient_err

        except AuthenticationError as auth_err:
            latency = (time.perf_counter() - start) * 1000
            safe_msg = _sanitize_message(str(auth_err), self.api_key)
            return LLMResponse(
                text="",
                provider="groq",
                model=self.model,
                latency_ms=latency,
                status=LLMStatus.UNAVAILABLE,
                warnings=(f"Groq authentication failure: {safe_msg}",),
                error_category="auth_error",
            )

        except RateLimitError as rate_err:
            latency = (time.perf_counter() - start) * 1000
            safe_msg = _sanitize_message(str(rate_err), self.api_key)
            return LLMResponse(
                text="",
                provider="groq",
                model=self.model,
                latency_ms=latency,
                status=LLMStatus.ERROR,
                warnings=(f"Groq rate limit exceeded: {safe_msg}",),
                error_category="rate_limit",
            )

        except (APITimeoutError, asyncio.TimeoutError) as timeout_err:
            latency = (time.perf_counter() - start) * 1000
            return LLMResponse(
                text="",
                provider="groq",
                model=self.model,
                latency_ms=latency,
                status=LLMStatus.TIMEOUT,
                warnings=(f"Groq request timed out after {self.timeout_seconds}s.",),
                error_category="timeout",
            )

        except APIStatusError as status_err:
            latency = (time.perf_counter() - start) * 1000
            safe_msg = _sanitize_message(str(status_err), self.api_key)
            return LLMResponse(
                text="",
                provider="groq",
                model=self.model,
                latency_ms=latency,
                status=LLMStatus.ERROR,
                warnings=(f"Groq status error: {safe_msg}",),
                error_category="status_error",
            )

        except Exception as exc:
            latency = (time.perf_counter() - start) * 1000
            safe_msg = _sanitize_message(str(exc), self.api_key)
            return LLMResponse(
                text="",
                provider="groq",
                model=self.model,
                latency_ms=latency,
                status=LLMStatus.ERROR,
                warnings=(f"Groq unexpected error: {safe_msg}",),
                error_category="unexpected_error",
            )
