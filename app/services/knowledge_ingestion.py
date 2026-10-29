"""Knowledge document ingestion, normalization, and deduplication pipeline."""

import html
import hashlib
import re
import unicodedata
from datetime import datetime, timezone
from typing import Any
import httpx

from app.core.logging import get_logger
from app.db.repositories.knowledge import KnowledgeRepository
from app.models.knowledge import (
    DocumentStatus,
    KnowledgeChunk,
    KnowledgeDocument,
)
from app.models.taxonomy import (
    AUTHORITY_TIER_SCORES,
    AuthorityTier,
    FreshnessPolicy,
    KnowledgeCategory,
    KnowledgeScope,
    is_valid_subcategory,
    normalize_category,
)
from app.providers.embedding.base import BaseEmbeddingProvider
from app.providers.embedding.factory import get_embedding_provider
from app.services.chunking import chunk_text

logger = get_logger("services.knowledge_ingestion")

# Safe HTML tag cleaner
TAG_RE = re.compile(r"<[^>]+>")
SCRIPT_STYLE_RE = re.compile(r"<(script|style|noscript|header|footer|nav)[^>]*>.*?</\1>", re.DOTALL | re.IGNORECASE)
CONTROL_CHAR_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def normalize_content(raw_text: str) -> str:
    """Normalize raw document text.

    Applies Unicode NFKC normalization, strips script/style tags, strips HTML tags,
    decodes entities, strips control characters, normalizes line endings, and removes
    redundant whitespace.
    """
    if not raw_text:
        return ""

    # 1. Unicode NFKC normalization
    text = unicodedata.normalize("NFKC", raw_text)

    # 2. Strip scripts, styles, header, footer, nav
    text = SCRIPT_STYLE_RE.sub(" ", text)

    # 3. Strip remaining HTML tags
    text = TAG_RE.sub(" ", text)

    # 4. Decode HTML entities
    text = html.unescape(text)

    # 5. Strip dangerous control characters (preserve newline and tab)
    text = CONTROL_CHAR_RE.sub("", text)

    # 6. Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # 7. Replace decorative rule separators
    text = re.sub(r"[-=_~*]{4,}", "\n", text)

    # 8. Normalize horizontal whitespace within lines
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.split("\n")]

    # 9. Normalize excessive vertical whitespace
    text = "\n".join(lines).strip()
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text


def compute_checksum(content: str) -> str:
    """Calculate deterministic SHA-256 checksum of normalized text."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


async def fetch_url_content(url: str, timeout: float = 10.0) -> tuple[str, str | None]:
    """Safely fetch and clean text content from an authoritative URL.

    Args:
        url: Target web URL (must start with http:// or https://).
        timeout: HTTP request timeout in seconds.

    Returns:
        Tuple of (cleaned_text_content, page_title_if_found).

    Raises:
        ValueError: If URL is invalid, unsafe, or exceeds size limits.
    """
    url_clean = url.strip()
    if not url_clean.startswith(("http://", "https://")):
        raise ValueError(f"Unsafe or unsupported URL scheme: {url_clean}")

    headers = {
        "User-Agent": "UrbanLens-Knowledge-Ingest/1.0 (+https://urbanlens.internal)",
        "Accept": "text/html,text/plain,application/xhtml+xml;q=0.9,*/*;q=0.8",
    }

    async with httpx.AsyncClient(timeout=timeout, follow_redirects=True, max_redirects=3) as client:
        resp = await client.get(url_clean, headers=headers)
        if resp.status_code != 200:
            raise ValueError(f"Failed to fetch URL ({resp.status_code}): {url_clean}")

        content_type = resp.headers.get("content-type", "").lower()
        if not any(t in content_type for t in ("text/", "json", "xml")):
            raise ValueError(f"Unsupported content type '{content_type}' from {url_clean}")

        # Enforce max body size (2MB)
        if len(resp.content) > 2 * 1024 * 1024:
            raise ValueError(f"Payload from {url_clean} exceeds safe size limit (2MB)")

        raw_body = resp.text

    # Extract title if present
    title_match = re.search(r"<title[^>]*>(.*?)</title>", raw_body, re.IGNORECASE | re.DOTALL)
    title = html.unescape(title_match.group(1).strip()) if title_match else None
    if title:
        title = re.sub(r"\s+", " ", title)

    cleaned = normalize_content(raw_body)
    return cleaned, title


class KnowledgeIngestionService:
    """Orchestrates document normalization, deduplication, chunking, and vector embedding."""

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
        authority_tier: str = AuthorityTier.TIER_1_OFFICIAL.value,
        authority_score: float | None = None,
        scope: str = KnowledgeScope.COUNTRY.value,
        country_id: str | None = None,
        city_id: str | None = None,
        category: str = KnowledgeCategory.CITY_INFORMATION.value,
        subcategory: str | None = None,
        language: str = "en",
        content_language: str = "en",
        source_type: str = "official",
        ingestion_method: str = "direct",
        canonical_url: str | None = None,
        freshness_policy: str = FreshnessPolicy.MODERATE_180D.value,
        review_required: bool = False,
        published_at: str | None = None,
        metadata: dict[str, Any] | None = None,
        reindex: bool = False,
    ) -> tuple[KnowledgeDocument, int]:
        """Ingest a knowledge document with normalization, deduplication, and chunking."""
        normalized = normalize_content(content)
        if len(normalized) < 20:
            raise ValueError("Document content is too short for indexing (minimum 20 characters)")

        checksum = compute_checksum(normalized)

        # Normalize taxonomy
        norm_category = normalize_category(category)
        if subcategory and not is_valid_subcategory(norm_category, subcategory):
            logger.debug("Subcategory '%s' not in taxonomy for '%s', preserving as custom", subcategory, norm_category)

        # Calculate authority score if omitted
        eff_authority_score = (
            authority_score
            if authority_score is not None
            else AUTHORITY_TIER_SCORES.get(authority_tier, 1.0)
        )

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
                authority_tier=existing.get("authority_tier", authority_tier),
                authority_score=float(existing.get("authority_score", eff_authority_score)),
                scope=existing.get("scope", scope),
                country_id=existing.get("country_id", country_id),
                city_id=existing.get("city_id", city_id),
                category=existing.get("category", norm_category),
                subcategory=existing.get("subcategory", subcategory),
                language=existing.get("language", language),
                content_language=existing.get("content_language", content_language),
                source_type=existing.get("source_type", source_type),
                ingestion_method=existing.get("ingestion_method", ingestion_method),
                canonical_url=existing.get("canonical_url", canonical_url or source_url),
                freshness_policy=existing.get("freshness_policy", freshness_policy),
                review_required=bool(existing.get("review_required", review_required)),
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
            authority_tier=authority_tier,
            authority_score=eff_authority_score,
            scope=scope,
            country_id=country_id.strip() if country_id else None,
            city_id=city_id.strip() if city_id else None,
            category=norm_category,
            subcategory=subcategory.strip() if subcategory else None,
            language=language.strip(),
            content_language=content_language.strip(),
            source_type=source_type,
            ingestion_method=ingestion_method,
            canonical_url=canonical_url or source_url,
            freshness_policy=freshness_policy,
            review_required=review_required,
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
                    authority_tier=doc.authority_tier,
                    authority_score=doc.authority_score,
                    scope=doc.scope,
                    city_id=doc.city_id,
                    country_id=doc.country_id,
                    category=doc.category,
                    subcategory=doc.subcategory,
                    fetched_at=doc.fetched_at,
                    updated_at=doc.updated_at,
                    freshness_policy=doc.freshness_policy,
                    metadata=dict(doc.metadata),
                )
            )

        # Replace existing chunks if reindexing
        if existing:
            self.repository.delete_chunks_by_document(doc_id)

        self.repository.add_chunks(chunks)
        logger.info("Ingested knowledge document %s with %d chunks", doc_id, len(chunks))

        return doc, len(chunks)

    async def ingest_from_url(
        self,
        url: str,
        title: str | None = None,
        source: str = "Official Web Resource",
        publisher: str | None = None,
        authority_tier: str = AuthorityTier.TIER_1_OFFICIAL.value,
        scope: str = KnowledgeScope.COUNTRY.value,
        country_id: str | None = None,
        city_id: str | None = None,
        category: str = KnowledgeCategory.CITY_INFORMATION.value,
        subcategory: str | None = None,
        reindex: bool = False,
    ) -> tuple[KnowledgeDocument, int]:
        """Fetch content from an authoritative URL and ingest it."""
        cleaned_text, detected_title = await fetch_url_content(url)
        final_title = title or detected_title or url

        return await self.ingest_document(
            title=final_title,
            content=cleaned_text,
            source=source,
            source_url=url,
            publisher=publisher,
            authority_tier=authority_tier,
            scope=scope,
            country_id=country_id,
            city_id=city_id,
            category=category,
            subcategory=subcategory,
            ingestion_method="url",
            canonical_url=url,
            reindex=reindex,
        )
