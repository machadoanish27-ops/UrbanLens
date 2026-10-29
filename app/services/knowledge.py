"""Knowledge retrieval service for UrbanLens RAG evidence grounding."""

import re
from datetime import datetime, timezone
from typing import Any

from app.core.logging import get_logger
from app.db.repositories.knowledge import KnowledgeRepository
from app.models.knowledge import KnowledgeEvidence
from app.models.taxonomy import AuthorityTier, FreshnessStatus, KnowledgeScope
from app.providers.embedding.base import BaseEmbeddingProvider
from app.providers.embedding.factory import get_embedding_provider

logger = get_logger("services.knowledge")


def detect_conflicts(evidence_items: list[KnowledgeEvidence]) -> list[dict[str, Any]]:
    """Detect potential source disagreements or contradictory factual claims in retrieved evidence.

    Flags cases where different publishers or sources report conflicting numerical ranges
    or opposing policies (e.g. required vs optional, prohibited vs allowed) for the same category.
    """
    conflicts: list[dict[str, Any]] = []
    if len(evidence_items) < 2:
        return conflicts

    # Group evidence items by category
    by_category: dict[str, list[KnowledgeEvidence]] = {}
    for ev in evidence_items:
        by_category.setdefault(ev.category, []).append(ev)

    opposing_pairs = [
        (r"\brequired\b", r"\boptional\b", "mandatory vs optional requirement"),
        (r"\bprohibited\b", r"\ballowed\b|\bpermitted\b", "prohibited vs permitted activity"),
        (r"\bfree\b", r"\bfee\b|\bcharge\b|\bcost\b", "free vs fee-based policy"),
    ]

    for cat, items in by_category.items():
        if len(items) < 2:
            continue

        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                item_a = items[i]
                item_b = items[j]

                # Only inspect items from distinct publishers or sources
                if (item_a.source or "").strip().lower() == (item_b.source or "").strip().lower():
                    continue

                text_a = item_a.text.lower()
                text_b = item_b.text.lower()

                # Check for contrasting keywords
                for pattern_1, pattern_2, note in opposing_pairs:
                    has_1_in_a = bool(re.search(pattern_1, text_a))
                    has_2_in_b = bool(re.search(pattern_2, text_b))
                    has_2_in_a = bool(re.search(pattern_2, text_a))
                    has_1_in_b = bool(re.search(pattern_1, text_b))

                    if (has_1_in_a and has_2_in_b) or (has_2_in_a and has_1_in_b):
                        conflicts.append({
                            "category": cat,
                            "source_a": item_a.source,
                            "source_b": item_b.source,
                            "evidence_id_a": item_a.evidence_id,
                            "evidence_id_b": item_b.evidence_id,
                            "difference_note": f"Potential divergence in {cat}: {note}",
                        })
                        break

    return conflicts


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
        subcategories: list[str] | None = None,
        scope: str | None = None,
        authority_tier: str | None = None,
        top_k: int = 5,
        min_score: float = 0.0,
    ) -> list[KnowledgeEvidence]:
        """Retrieve grounded knowledge evidence items matching query and metadata constraints.

        Args:
            query: Natural language query string.
            city_id: Optional canonical city ID for location-specific grounding.
            country_id: Optional canonical country ID.
            categories: Optional list of knowledge categories.
            subcategories: Optional list of subcategories.
            scope: Optional scope filter (global, country, region, city).
            authority_tier: Optional authority tier filter.
            top_k: Maximum evidence items to return.
            min_score: Minimum composite score threshold.

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
            subcategories=subcategories,
            scope=scope,
            authority_tier=authority_tier,
            top_k=top_k,
            min_score=min_score,
        )

        now_iso = datetime.now(timezone.utc).isoformat()
        evidence_list: list[KnowledgeEvidence] = []

        for c in chunks:
            # Look up document title and metadata if available
            doc_id = c.get("document_id", "")
            title = c.get("title")
            doc = None
            if not title or not c.get("fetched_at") or not c.get("source_url"):
                doc = self.repository.get_document(doc_id)
                if not title:
                    title = (doc or {}).get("title") or f"Knowledge Document ({doc_id})"

            chunk_id = c.get("chunk_id", "")
            doc_fetched_at = c.get("fetched_at") or (doc.get("fetched_at") if doc else None)
            doc_source_url = c.get("source_url") or (doc.get("source_url") if doc else None)
            doc_publisher = c.get("publisher") or (doc.get("publisher") if doc else None)

            evidence_list.append(
                KnowledgeEvidence(
                    evidence_id=f"ev_{chunk_id}" if chunk_id else f"ev_{len(evidence_list)}",
                    document_id=doc_id,
                    chunk_id=chunk_id,
                    title=title,
                    source=c.get("source") or (doc.get("source") if doc else "urbanlens_knowledge_base"),
                    source_url=doc_source_url,
                    publisher=doc_publisher,
                    authority_tier=c.get("authority_tier", AuthorityTier.TIER_1_OFFICIAL.value),
                    authority_score=float(c.get("authority_score", 1.0)),
                    scope=c.get("scope", KnowledgeScope.COUNTRY.value),
                    freshness_status=c.get("freshness_status", FreshnessStatus.FRESH.value),
                    fetched_at=doc_fetched_at,
                    updated_at=c.get("updated_at") or (doc.get("updated_at") if doc else None),
                    text=c.get("text", ""),
                    category=c.get("category", "city_information"),
                    subcategory=c.get("subcategory"),
                    city_id=c.get("city_id"),
                    country_id=c.get("country_id"),
                    retrieved_at=now_iso,
                    retrieval_score=c.get("retrieval_score"),
                    score_breakdown=dict(c.get("score_breakdown") or {}),
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
        authority_tier: str | None = None,
        scope: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[dict[str, Any]], int]:
        """List documents matching filters."""
        return self.repository.list_documents(
            city_id=city_id,
            country_id=country_id,
            category=category,
            authority_tier=authority_tier,
            scope=scope,
            page=page,
            page_size=page_size,
        )

    def delete_document(self, document_id: str) -> bool:
        """Delete document by document_id."""
        return self.repository.delete_document(document_id)

    def get_stats(self) -> dict[str, Any]:
        """Retrieve aggregated knowledge corpus statistics."""
        return self.repository.get_knowledge_stats()

    def list_sources(self) -> list[dict[str, Any]]:
        """Retrieve distinct authoritative sources and publishers."""
        return self.repository.list_sources()

    def audit_corpus(self) -> dict[str, Any]:
        """Run knowledge base data integrity and freshness audit."""
        return self.repository.audit_corpus()
