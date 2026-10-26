"""Deterministic feature hashing embedding provider."""

import hashlib
import math
import re
from app.providers.embedding.base import BaseEmbeddingProvider


class DeterministicHashEmbeddingProvider(BaseEmbeddingProvider):
    """Deterministic, open-source local embedding provider using signed feature hashing.

    Uses sha256 feature hashing with token unigrams and subword character n-grams.
    Vectors are L2-normalized, allowing cosine similarity to be computed via dot product.
    Requires no external network calls, API keys, or heavy machine learning models.
    """

    def __init__(self, dimension: int = 128) -> None:
        if dimension <= 0:
            raise ValueError(f"Dimension must be positive, got {dimension}")
        self._dimension = dimension

    @property
    def provider_name(self) -> str:
        return "deterministic-hash"

    @property
    def dimension(self) -> int:
        return self._dimension

    def _embed_single(self, text: str) -> list[float]:
        """Convert a single text string into a deterministic L2-normalized float vector."""
        if not text or not text.strip():
            return [0.0] * self._dimension

        vec = [0.0] * self._dimension

        # Tokenize words
        words = re.findall(r"\b\w+\b", text.lower())
        if not words:
            return [0.0] * self._dimension

        # Accumulate unigrams and char 3-grams
        tokens: list[str] = list(words)
        for w in words:
            if len(w) >= 3:
                for i in range(len(w) - 2):
                    tokens.append(w[i : i + 3])

        for tok in tokens:
            digest = hashlib.sha256(tok.encode("utf-8")).digest()
            # First 4 bytes determine bucket index
            bucket = int.from_bytes(digest[:4], byteorder="big") % self._dimension
            # 5th byte determines sign (+1 or -1) to reduce hash collisions
            sign = 1.0 if (digest[4] % 2 == 0) else -1.0
            vec[bucket] += sign

        # Compute L2 norm
        sq_sum = sum(v * v for v in vec)
        if sq_sum > 0.0:
            norm = math.sqrt(sq_sum)
            vec = [round(v / norm, 6) for v in vec]
        else:
            vec = [0.0] * self._dimension

        return vec

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Compute embedding vectors for a batch of texts."""
        return [self._embed_single(t) for t in texts]

    async def embed_query(self, query: str) -> list[float]:
        """Compute embedding vector for a single query."""
        return self._embed_single(query)
