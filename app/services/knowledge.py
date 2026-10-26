"""Knowledge retrieval service for UrbanLens RAG evidence grounding."""

from datetime import datetime, timezone
from typing import Any

from app.core.logging import get_logger
from app.db.repositories.knowledge import KnowledgeRepository
from app.models.knowledge import KnowledgeEvidence
from app.providers.embedding.base import BaseEmbeddingProvider
from app.providers.embedding.factory import get_embedding_provider

logger = get_logger("services.knowledge")


class KnowledgeService:
    """Service providing semantic knowledge search, evidence extraction, and document access."""

    def __init__(
        self,
        repository: KnowledgeRepository,
        embedding_provider: BaseEmbeddingProvider | None = None,
    ) -> None:
        self.repository = repository
        self.embedding_provider = embedding_provider or get_embedding_provider()

    async def search_knowledge(
        self,
        query: str,
        city_id: str | None = None,
        country_id: str | None = None,
        categories: list[str] | None = None,
        top_k: int = 5,
        min_score: float = 0.0,
    ) -> list[KnowledgeEvidence]:
        """Retrieve grounded knowledge evidence items matching query and metadata constraints.

        Args:
            query: Natural language query string.
            city_id: Optional canonical city ID for location-specific grounding.
            country_id: Optional canonical country ID.
            categories: Optional list of knowledge categories.
            top_k: Maximum evidence items to return.
            min_score: Minimum cosine similarity threshold.

        Returns:
            List of KnowledgeEvidence objects with complete provenance.
        """
        if not query or not query.strip():
            return []

        # Generate query vector
        query_embedding = await self.embedding_provider.embed_query(query.strip())

        # Retrieve matched chunks from repository
        chunks = self.repository.search_chunks(
            query_embedding=query_embedding,
            city_id=city_id,
            country_id=country_id,
            categories=categories,
            top_k=top_k,
            min_score=min_score,
        )

        now_iso = datetime.now(timezone.utc).isoformat()
        evidence_list: list[KnowledgeEvidence] = []

        for c in chunks:
            # Look up document title if available
            doc_id = c.get("document_id", "")
            title = c.get("title")
            if not title:
                doc = self.repository.get_document(doc_id)
                title = (doc or {}).get("title") or f"Knowledge Document ({doc_id})"

            chunk_id = c.get("chunk_id", "")
            evidence_list.append(
                KnowledgeEvidence(
                    evidence_id=f"ev_{chunk_id}" if chunk_id else f"ev_{len(evidence_list)}",
                    document_id=doc_id,
                    chunk_id=chunk_id,
                    title=title,
                    source=c.get("source") or "urbanlens_knowledge_base",
                    source_url=c.get("source_url"),
                    publisher=c.get("publisher"),
                    text=c.get("text", ""),
                    category=c.get("category", "city_information"),
                    city_id=c.get("city_id"),
                    country_id=c.get("country_id"),
                    retrieved_at=now_iso,
                    retrieval_score=c.get("retrieval_score"),
                    metadata=dict(c.get("metadata") or {}),
                )
            )

        logger.debug(
            "Knowledge search for '%s' (city=%s, cat=%s) returned %d evidence items",
            query,
            city_id,
            categories,
            len(evidence_list),
        )
        return evidence_list

    def get_document(self, document_id: str) -> dict[str, Any] | None:
        """Fetch document by document_id."""
        return self.repository.get_document(document_id)

    def list_documents(
        self,
        city_id: str | None = None,
        country_id: str | None = None,
        category: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[dict[str, Any]], int]:
        """List documents matching filters."""
        return self.repository.list_documents(
            city_id=city_id,
            country_id=country_id,
            category=category,
            page=page,
            page_size=page_size,
        )

    def delete_document(self, document_id: str) -> bool:
        """Delete document by document_id."""
        return self.repository.delete_document(document_id)
