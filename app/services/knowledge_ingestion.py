"""Knowledge document ingestion and normalization pipeline."""

import hashlib
import re
import uuid
from datetime import datetime, timezone
from typing import Any

from app.core.logging import get_logger
from app.db.repositories.knowledge import KnowledgeRepository
from app.models.knowledge import DocumentStatus, KnowledgeCategory, KnowledgeChunk, KnowledgeDocument
from app.providers.embedding.base import BaseEmbeddingProvider
from app.providers.embedding.factory import get_embedding_provider
from app.services.chunking import chunk_text

logger = get_logger("services.knowledge_ingestion")


def normalize_content(raw_text: str) -> str:
    """Normalize raw document text, removing redundant whitespace and safe formatting artifacts."""
    if not raw_text:
        return ""

    # Normalize line endings
    text = raw_text.replace("\r\n", "\n").replace("\r", "\n")

    # Replace decorative rule separators
    text = re.sub(r"[-=_~*]{4,}", "\n", text)

    # Normalize excessive vertical whitespace
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Normalize horizontal whitespace within lines
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.split("\n")]
    text = "\n".join(lines).strip()

    return text


def compute_checksum(content: str) -> str:
    """Calculate deterministic SHA-256 checksum of normalized text."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


class KnowledgeIngestionService:
    """Orchestrates document normalization, checksumming, chunking, and vector embedding."""

    def __init__(
        self,
        repository: KnowledgeRepository,
        embedding_provider: BaseEmbeddingProvider | None = None,
    ) -> None:
        self.repository = repository
        self.embedding_provider = embedding_provider or get_embedding_provider()

    async def ingest_document(
        self,
        title: str,
        content: str,
        source: str,
        source_url: str | None = None,
        publisher: str | None = None,
        country_id: str | None = None,
        city_id: str | None = None,
        category: str = KnowledgeCategory.CITY_INFORMATION.value,
        language: str = "en",
        published_at: str | None = None,
        metadata: dict[str, Any] | None = None,
        reindex: bool = False,
    ) -> tuple[KnowledgeDocument, int]:
        """Ingest a knowledge document with normalization, deduplication, and chunking.

        Args:
            title: Document title.
            content: Raw document text.
            source: Source publication or organization name.
            source_url: Original source URL.
            publisher: Publishing organization.
            country_id: Optional canonical country ID.
            city_id: Optional canonical city ID.
            category: Knowledge category from KnowledgeCategory enum.
            language: Language code (default "en").
            published_at: Original publication timestamp string.
            metadata: Supplemental metadata (e.g. is_official, authority_level).
            reindex: If True, re-chunk and re-embed existing document.

        Returns:
            Tuple of (KnowledgeDocument, chunk_count).
        """
        normalized = normalize_content(content)
        if len(normalized) < 20:
            raise ValueError("Document content is too short for indexing (minimum 20 characters)")

        checksum = compute_checksum(normalized)

        # Check for existing document by checksum
        existing = self.repository.get_document_by_checksum(checksum)
        if existing and not reindex:
            doc_id = existing["document_id"]
            existing_chunks = self.repository.get_chunks_by_document(doc_id)
            logger.info("Document with checksum %s already exists (doc_id=%s)", checksum, doc_id)
            doc = KnowledgeDocument(
                document_id=doc_id,
                title=existing.get("title", title),
                source=existing.get("source", source),
                source_url=existing.get("source_url", source_url),
                publisher=existing.get("publisher", publisher),
                country_id=existing.get("country_id", country_id),
                city_id=existing.get("city_id", city_id),
                category=existing.get("category", category),
                language=existing.get("language", language),
                published_at=existing.get("published_at", published_at),
                updated_at=existing.get("updated_at"),
                fetched_at=existing.get("fetched_at", datetime.now(timezone.utc).isoformat()),
                content=existing.get("content", normalized),
                checksum=checksum,
                metadata=existing.get("metadata", metadata or {}),
                status=existing.get("status", DocumentStatus.ACTIVE.value),
            )
            return doc, len(existing_chunks)

        # Generate unique document ID anchored to checksum prefix
        doc_id = existing["document_id"] if existing else f"doc_{checksum[:12]}"
        now_iso = datetime.now(timezone.utc).isoformat()

        doc = KnowledgeDocument(
            document_id=doc_id,
            title=title.strip(),
            source=source.strip(),
            source_url=source_url.strip() if source_url else None,
            publisher=publisher.strip() if publisher else None,
            country_id=country_id.strip() if country_id else None,
            city_id=city_id.strip() if city_id else None,
            category=category.strip(),
            language=language.strip(),
            published_at=published_at,
            updated_at=now_iso if existing else None,
            fetched_at=now_iso,
            content=normalized,
            checksum=checksum,
            metadata=dict(metadata or {}),
            status=DocumentStatus.ACTIVE.value,
        )

        # Save document
        self.repository.add_document(doc)

        # Generate chunks
        raw_chunks = chunk_text(normalized, chunk_size=600, overlap=100)
        if not raw_chunks:
            raw_chunks = [normalized]

        # Compute embeddings asynchronously for all chunks
        embeddings = await self.embedding_provider.embed_texts(raw_chunks)

        # Prepare KnowledgeChunk instances
        chunks: list[KnowledgeChunk] = []
        for idx, (text_chunk, emb) in enumerate(zip(raw_chunks, embeddings)):
            chunk_id = f"{doc_id}_chk_{idx}"
            chunks.append(
                KnowledgeChunk(
                    chunk_id=chunk_id,
                    document_id=doc_id,
                    chunk_index=idx,
                    text=text_chunk,
                    char_count=len(text_chunk),
                    token_count=len(text_chunk.split()),
                    embedding=emb,
                    source=doc.source,
                    source_url=doc.source_url,
                    publisher=doc.publisher,
                    city_id=doc.city_id,
                    country_id=doc.country_id,
                    category=doc.category,
                    metadata=dict(doc.metadata),
                )
            )

        # Replace existing chunks if reindexing
        if existing:
            self.repository.delete_chunks_by_document(doc_id)

        self.repository.add_chunks(chunks)
        logger.info("Ingested knowledge document %s with %d chunks", doc_id, len(chunks))

        return doc, len(chunks)
