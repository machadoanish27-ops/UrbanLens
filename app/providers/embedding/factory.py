"""Embedding provider factory."""

from app.core.config import settings
from app.providers.embedding.base import BaseEmbeddingProvider
from app.providers.embedding.hash_provider import DeterministicHashEmbeddingProvider


def get_embedding_provider(provider_type: str | None = None) -> BaseEmbeddingProvider:
    """Return an active embedding provider instance according to configuration."""
    chosen = (provider_type or getattr(settings, "EMBEDDING_PROVIDER", "hash")).lower()

    if chosen in ("hash", "local", "deterministic"):
        dim = getattr(settings, "EMBEDDING_DIMENSION", 128)
        return DeterministicHashEmbeddingProvider(dimension=dim)

    if chosen == "openai":
        raise ValueError(
            "OpenAI embedding provider requested but OPENAI_API_KEY is not configured in environment."
        )

    if chosen == "huggingface":
        raise ValueError(
            "HuggingFace embedding provider requested but model path is not configured."
        )

    raise ValueError(f"Unknown or unsupported embedding provider: '{chosen}'")
