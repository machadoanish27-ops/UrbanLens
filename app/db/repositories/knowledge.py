"""Repository for knowledge documents and vectorized chunks in MongoDB."""

from typing import Any
from pymongo.database import Database

from app.db.repositories.base import BaseRepository, clean_mongo_doc
from app.models.knowledge import KnowledgeChunk, KnowledgeDocument
from app.models.taxonomy import (
    AUTHORITY_TIER_SCORES,
    AuthorityTier,
    FreshnessPolicy,
    FreshnessStatus,
    KnowledgeScope,
    calculate_freshness,
    get_country_for_city,
    resolve_city_id,
)


def cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """Compute cosine similarity between two float vectors.

    Assumes vectors are L2-normalized; dot product equals cosine similarity.
    """
    if not vec_a or not vec_b or len(vec_a) != len(vec_b):
        return 0.0
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    # Bound to [0.0, 1.0] for positive relevance metrics
    return max(0.0, min(1.0, dot))


class KnowledgeRepository(BaseRepository):
    """Repository accessing 'knowledge_documents' and 'knowledge_chunks' collections."""

    def __init__(self, database: Database) -> None:
        super().__init__(database, "knowledge_documents")
        self.chunks_repo = BaseRepository(database, "knowledge_chunks")

    # Document operations

    def add_document(self, doc: KnowledgeDocument | dict[str, Any]) -> dict[str, Any]:
        """Insert or replace a knowledge document."""
        data = doc if isinstance(doc, dict) else {
            "document_id": doc.document_id,
            "title": doc.title,
            "source": doc.source,
            "source_url": doc.source_url,
            "publisher": doc.publisher,
            "authority_tier": getattr(doc, "authority_tier", AuthorityTier.TIER_1_OFFICIAL.value),
            "authority_score": getattr(doc, "authority_score", 1.0),
            "scope": getattr(doc, "scope", KnowledgeScope.COUNTRY.value),
            "country_id": doc.country_id,
            "city_id": doc.city_id,
            "category": doc.category,
            "subcategory": getattr(doc, "subcategory", None),
            "language": doc.language,
            "content_language": getattr(doc, "content_language", "en"),
            "source_type": getattr(doc, "source_type", "official"),
            "ingestion_method": getattr(doc, "ingestion_method", "direct"),
            "canonical_url": getattr(doc, "canonical_url", doc.source_url),
            "freshness_policy": getattr(doc, "freshness_policy", FreshnessPolicy.MODERATE_180D.value),
            "review_required": getattr(doc, "review_required", False),
            "published_at": doc.published_at,
            "updated_at": doc.updated_at,
            "fetched_at": doc.fetched_at,
            "content": doc.content,
            "checksum": doc.checksum,
            "metadata": doc.metadata,
            "status": doc.status,
        }
        self.collection.replace_one(
            {"document_id": data["document_id"]},
            data,
            upsert=True,
        )
        return data

    def get_document(self, document_id: str) -> dict[str, Any] | None:
        """Fetch a knowledge document by document_id."""
        return self.find_one({"document_id": document_id})

    def get_document_by_checksum(self, checksum: str) -> dict[str, Any] | None:
        """Fetch a knowledge document by content checksum."""
        return self.find_one({"checksum": checksum})

    def delete_document(self, document_id: str) -> bool:
        """Delete document and its corresponding chunks."""
        self.delete_chunks_by_document(document_id)
        res = self.collection.delete_one({"document_id": document_id})
        return res.deleted_count > 0

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
        """List documents matching filters with pagination."""
        filters: dict[str, Any] = {}
        if city_id:
            filters["city_id"] = city_id
        if country_id:
            filters["country_id"] = country_id
        if category:
            filters["category"] = category
        if authority_tier:
            filters["authority_tier"] = authority_tier
        if scope:
            filters["scope"] = scope

        sort = [("fetched_at", -1)]
        return self.find_paginated(filters, sort=sort, page=page, page_size=page_size)

    # Chunk operations

    def add_chunks(self, chunks: list[KnowledgeChunk | dict[str, Any]]) -> int:
        """Insert or replace vectorized chunks."""
        if not chunks:
            return 0

        count = 0
        for c in chunks:
            data = c if isinstance(c, dict) else {
                "chunk_id": c.chunk_id,
                "document_id": c.document_id,
                "chunk_index": c.chunk_index,
                "text": c.text,
                "char_count": c.char_count,
                "token_count": c.token_count,
                "embedding": c.embedding,
                "source": c.source,
                "source_url": c.source_url,
                "publisher": c.publisher,
                "authority_tier": getattr(c, "authority_tier", AuthorityTier.TIER_1_OFFICIAL.value),
                "authority_score": getattr(c, "authority_score", 1.0),
                "scope": getattr(c, "scope", KnowledgeScope.COUNTRY.value),
                "city_id": c.city_id,
                "country_id": c.country_id,
                "category": c.category,
                "subcategory": getattr(c, "subcategory", None),
                "fetched_at": getattr(c, "fetched_at", None),
                "updated_at": getattr(c, "updated_at", None),
                "freshness_policy": getattr(c, "freshness_policy", None),
                "metadata": c.metadata,
            }
            self.chunks_repo.collection.replace_one(
                {"chunk_id": data["chunk_id"]},
                data,
                upsert=True,
            )
            count += 1
        return count

    def get_chunks_by_document(self, document_id: str) -> list[dict[str, Any]]:
        """Fetch all chunks belonging to a document ordered by index."""
        cursor = self.chunks_repo.collection.find({"document_id": document_id}).sort("chunk_index", 1)
        return [clean_mongo_doc(c) for c in cursor if c]

    def delete_chunks_by_document(self, document_id: str) -> int:
        """Remove all chunks associated with a document."""
        res = self.chunks_repo.collection.delete_many({"document_id": document_id})
        return res.deleted_count

    # Advanced semantic & metadata retrieval with composite scoring

    def search_chunks(
        self,
        query_embedding: list[float],
        city_id: str | None = None,
        country_id: str | None = None,
        categories: list[str] | None = None,
        subcategories: list[str] | None = None,
        scope: str | None = None,
        authority_tier: str | None = None,
        top_k: int = 5,
        min_score: float = 0.0,
    ) -> list[dict[str, Any]]:
        """Search chunks with metadata filtering, composite multi-attribute scoring.

        Composite Scoring Formula:
          composite = (0.55 * semantic_similarity)
                    + (0.25 * authority_score)
                    + (0.10 * freshness_score)
                    + (0.10 * scope_relevance)

        Args:
            query_embedding: L2-normalized embedding vector of the search query.
            city_id: Optional target city identifier.
            country_id: Optional target country identifier.
            categories: Optional list of knowledge categories.
            subcategories: Optional list of subcategories.
            scope: Optional scope constraint.
            authority_tier: Optional minimum or specific authority tier.
            top_k: Maximum candidate chunks to return.
            min_score: Minimum composite score threshold.

        Returns:
            Ranked list of matching chunk dictionaries with 'retrieval_score',
            'freshness_status', and 'score_breakdown'.
        """
        filters: dict[str, Any] = {}

        canon_city = resolve_city_id(city_id)
        matched_cities = [city_id, canon_city] if city_id else []
        target_country = (
            country_id
            or (get_country_for_city(city_id) if city_id else None)
            or (get_country_for_city(canon_city) if canon_city else None)
        )

        if city_id:
            # Match chunks specific to the city, or general country/global chunks for this city's country.
            # Strictly exclude chunks dedicated to other distinct cities or other countries.
            city_or_conditions: list[dict[str, Any]] = [
                {"city_id": {"$in": matched_cities}}
            ]
            if target_country:
                city_or_conditions.append({
                    "city_id": {"$in": [None, ""]},
                    "$or": [
                        {"country_id": target_country},
                        {"scope": "global"},
                        {"country_id": {"$in": [None, ""]}},
                    ],
                })
            else:
                city_or_conditions.append({
                    "city_id": {"$in": [None, ""]},
                    "scope": {"$in": ["country", "global", "region"]},
                })
            filters["$or"] = city_or_conditions
        elif target_country:
            filters["$or"] = [
                {"country_id": target_country},
                {"country_id": {"$in": [None, ""]}},
                {"country_id": {"$exists": False}},
                {"scope": "global"},
            ]

        if categories:
            filters["category"] = {"$in": categories}

        if subcategories:
            filters["subcategory"] = {"$in": subcategories}

        if scope:
            filters["scope"] = scope

        if authority_tier:
            filters["authority_tier"] = authority_tier

        cursor = self.chunks_repo.collection.find(filters)
        scored_candidates: list[tuple[float, dict[str, Any]]] = []

        for raw_chunk in cursor:
            chunk = clean_mongo_doc(raw_chunk)
            if not chunk:
                continue

            emb = chunk.get("embedding")
            if not emb:
                continue

            # 1. Semantic Similarity [0.0 - 1.0]
            sim_score = cosine_similarity(query_embedding, emb)

            # 2. Authority Score [0.0 - 1.0]
            tier = chunk.get("authority_tier", AuthorityTier.TIER_1_OFFICIAL.value)
            auth_score = float(chunk.get("authority_score") or AUTHORITY_TIER_SCORES.get(tier, 1.0))

            # 3. Freshness Score [0.0 - 1.0]
            fetched_at = chunk.get("fetched_at")
            if not fetched_at and chunk.get("document_id"):
                parent_doc = self.get_document(chunk["document_id"])
                fetched_at = parent_doc.get("fetched_at") if parent_doc else None

            updated_at = chunk.get("updated_at")
            cat = chunk.get("category", "")
            policy = chunk.get("freshness_policy")
            fresh_status, fresh_score = calculate_freshness(fetched_at, updated_at, cat, policy)

            # 4. Scope Relevance [0.0 - 1.0]
            chunk_city = chunk.get("city_id")
            chunk_country = chunk.get("country_id")
            chunk_scope = chunk.get("scope", KnowledgeScope.COUNTRY.value)

            if city_id:
                if chunk_city in matched_cities:
                    scope_score = 1.0
                elif chunk_scope == KnowledgeScope.REGION.value:
                    scope_score = 0.9
                elif chunk_country and target_country and chunk_country == target_country:
                    scope_score = 0.8
                elif chunk_scope == KnowledgeScope.GLOBAL.value or (not chunk_city and not chunk_country):
                    scope_score = 0.5
                else:
                    scope_score = 0.2
            elif target_country:
                if chunk_country == target_country:
                    scope_score = 1.0
                elif chunk_scope == KnowledgeScope.GLOBAL.value:
                    scope_score = 0.7
                else:
                    scope_score = 0.3
            else:
                scope_score = 1.0

            # Composite Formula: 0.55 semantic + 0.25 authority + 0.10 freshness + 0.10 scope
            composite = (0.55 * sim_score) + (0.25 * auth_score) + (0.10 * fresh_score) + (0.10 * scope_score)

            if composite >= min_score:
                chunk["retrieval_score"] = round(composite, 4)
                chunk["freshness_status"] = fresh_status.value
                chunk["score_breakdown"] = {
                    "semantic": round(sim_score, 4),
                    "authority": round(auth_score, 4),
                    "freshness": round(fresh_score, 4),
                    "scope": round(scope_score, 4),
                    "composite": round(composite, 4),
                }
                scored_candidates.append((composite, chunk))

        # Sort descending by composite score
        scored_candidates.sort(key=lambda x: x[0], reverse=True)
        return [c for _, c in scored_candidates[:top_k]]

    # Analytics, Audit & Stats

    def get_knowledge_stats(self) -> dict[str, Any]:
        """Aggregate statistical summary across documents and chunks."""
        total_docs = self.collection.count_documents({})
        total_chunks = self.chunks_repo.collection.count_documents({})

        cat_counts: dict[str, int] = {}
        scope_counts: dict[str, int] = {}
        tier_counts: dict[str, int] = {}
        countries_covered_set: set[str] = set()
        cities_covered_set: set[str] = set()
        freshness_counts = {"fresh": 0, "aging": 0, "stale": 0, "unknown": 0}

        for doc in self.collection.find({}):
            cat = doc.get("category") or "unspecified"
            cat_counts[cat] = cat_counts.get(cat, 0) + 1

            scope = doc.get("scope") or "country"
            scope_counts[scope] = scope_counts.get(scope, 0) + 1

            tier = doc.get("authority_tier") or AuthorityTier.TIER_1_OFFICIAL.value
            tier_counts[tier] = tier_counts.get(tier, 0) + 1

            cid = doc.get("country_id")
            if cid:
                countries_covered_set.add(cid)

            city = doc.get("city_id")
            if city:
                cities_covered_set.add(city)

            status, _ = calculate_freshness(
                doc.get("fetched_at"),
                doc.get("updated_at"),
                doc.get("category"),
                doc.get("freshness_policy"),
            )
            freshness_counts[status.value] = freshness_counts.get(status.value, 0) + 1

        return {
            "total_documents": total_docs,
            "total_chunks": total_chunks,
            "categories_breakdown": dict(sorted(cat_counts.items(), key=lambda x: x[1], reverse=True)),
            "scope_breakdown": dict(sorted(scope_counts.items(), key=lambda x: x[1], reverse=True)),
            "tier_breakdown": dict(sorted(tier_counts.items(), key=lambda x: x[1], reverse=True)),
            "countries_covered": sorted(countries_covered_set),
            "cities_covered": sorted(cities_covered_set),
            "freshness_summary": freshness_counts,
        }

    def list_sources(self) -> list[dict[str, Any]]:
        """List distinct authoritative sources registered in the knowledge layer."""
        sources_map: dict[str, dict[str, Any]] = {}
        for doc in self.collection.find({}):
            src = doc.get("source")
            if not src:
                continue
            if src not in sources_map:
                sources_map[src] = {
                    "source": src,
                    "publisher": doc.get("publisher"),
                    "authority_tier": doc.get("authority_tier") or AuthorityTier.TIER_1_OFFICIAL.value,
                    "source_url": doc.get("source_url"),
                    "categories": set(),
                    "document_count": 0,
                }
            cat = doc.get("category")
            if cat:
                sources_map[src]["categories"].add(cat)
            sources_map[src]["document_count"] += 1

        res = []
        for item in sources_map.values():
            res.append({
                "source": item["source"],
                "publisher": item["publisher"],
                "authority_tier": item["authority_tier"],
                "source_url": item["source_url"],
                "categories": sorted(item["categories"]),
                "document_count": item["document_count"],
            })
        res.sort(key=lambda x: x["document_count"], reverse=True)
        return res

    def audit_corpus(self) -> dict[str, Any]:
        """Perform data integrity audit of knowledge corpus."""
        total_docs = self.collection.count_documents({})
        docs_without_chunks: list[str] = []
        stale_docs: list[str] = []
        checksum_map: dict[str, list[str]] = {}

        for doc in self.collection.find({}):
            doc_id = doc.get("document_id")
            if not doc_id:
                continue

            if self.chunks_repo.collection.count_documents({"document_id": doc_id}) == 0:
                docs_without_chunks.append(doc_id)

            status, _ = calculate_freshness(
                doc.get("fetched_at"),
                doc.get("updated_at"),
                doc.get("category"),
                doc.get("freshness_policy"),
            )
            if status == FreshnessStatus.STALE:
                stale_docs.append(doc_id)

            csum = doc.get("checksum")
            if csum:
                checksum_map.setdefault(csum, []).append(doc_id)

        duplicate_checksums = [
            {"checksum": csum, "count": len(d_ids), "documents": d_ids}
            for csum, d_ids in checksum_map.items()
            if len(d_ids) > 1
        ]

        return {
            "total_documents": total_docs,
            "unchunked_documents_count": len(docs_without_chunks),
            "unchunked_document_ids": docs_without_chunks,
            "stale_documents_count": len(stale_docs),
            "stale_document_ids": stale_docs,
            "duplicate_checksum_groups": duplicate_checksums,
            "integrity_status": "healthy" if not docs_without_chunks and not duplicate_checksums else "needs_attention",
        }
