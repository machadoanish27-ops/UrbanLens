"""Factory for instantiating LLM providers."""

from app.core.config import settings
from app.providers.llm.base import BaseLLMProvider
from app.providers.llm.groq import GroqProvider
from app.providers.llm.mock import MockLLMProvider


def get_llm_provider(
    provider_type: str | None = None,
    api_key: str | None = None,
    model: str | None = None,
    timeout_seconds: float | None = None,
) -> BaseLLMProvider:
    """Instantiate and return the configured LLM provider."""
    ptype = (provider_type or settings.LLM_PROVIDER).strip().lower()

    if ptype == "groq":
        return GroqProvider(
            api_key=api_key,
            model=model,
            timeout_seconds=timeout_seconds,
        )

    if ptype == "mock":
        return MockLLMProvider(model=model or "mock-model")

    raise ValueError(
        f"Unsupported LLM provider '{ptype}'. Supported providers: 'groq', 'mock'."
    )
