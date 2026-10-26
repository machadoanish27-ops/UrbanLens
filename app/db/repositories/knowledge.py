"""Repository for knowledge documents and vectorized chunks in MongoDB."""

from typing import Any
from pymongo.database import Database

from app.db.repositories.base import BaseRepository, clean_mongo_doc
from app.models.knowledge import KnowledgeChunk, KnowledgeDocument


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
            "country_id": doc.country_id,
            "city_id": doc.city_id,
            "category": doc.category,
            "language": doc.language,
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
                "city_id": c.city_id,
                "country_id": c.country_id,
                "category": c.category,
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

    # Semantic & metadata retrieval

    def search_chunks(
        self,
        query_embedding: list[float],
        city_id: str | None = None,
        country_id: str | None = None,
        categories: list[str] | None = None,
        top_k: int = 5,
        min_score: float = 0.0,
    ) -> list[dict[str, Any]]:
        """Search chunks with metadata filtering and cosine similarity ranking.

        Args:
            query_embedding: L2-normalized embedding vector of the search query.
            city_id: Optional city filter. Matches specific city or national/general records.
            country_id: Optional country filter.
            categories: Optional list of knowledge categories to include.
            top_k: Maximum candidate chunks to return.
            min_score: Minimum cosine similarity threshold.

        Returns:
            Ranked list of matching chunk dictionaries with 'retrieval_score' field.
        """
        filters: dict[str, Any] = {}

        if city_id:
            # Match chunks specific to the city, or general national/global chunks
            filters["$or"] = [
                {"city_id": city_id},
                {"city_id": None},
                {"city_id": {"$exists": False}},
            ]

        if country_id and not city_id:
            filters["$or"] = [
                {"country_id": country_id},
                {"country_id": None},
                {"country_id": {"$exists": False}},
            ]

        if categories:
            filters["category"] = {"$in": categories}

        cursor = self.chunks_repo.collection.find(filters)
        scored_candidates: list[tuple[float, dict[str, Any]]] = []

        for raw_chunk in cursor:
            chunk = clean_mongo_doc(raw_chunk)
            if not chunk:
                continue

            emb = chunk.get("embedding")
            if not emb:
                continue

            score = cosine_similarity(query_embedding, emb)
            if score >= min_score:
                chunk["retrieval_score"] = round(score, 4)
                scored_candidates.append((score, chunk))

        # Sort descending by score
        scored_candidates.sort(key=lambda x: x[0], reverse=True)
        return [c for _, c in scored_candidates[:top_k]]
