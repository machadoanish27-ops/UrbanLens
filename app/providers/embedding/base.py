"""Abstract base class for embedding providers."""

from abc import ABC, abstractmethod


class BaseEmbeddingProvider(ABC):
    """Abstract interface for text embedding generation."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Name of the embedding provider."""

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Dimensionality of the generated embedding vectors."""

    @abstractmethod
    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Compute embedding vectors for a batch of text strings."""

    @abstractmethod
    async def embed_query(self, query: str) -> list[float]:
        """Compute embedding vector for a single query string."""
