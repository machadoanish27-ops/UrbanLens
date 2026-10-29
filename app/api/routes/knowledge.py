"""Knowledge search, document management, and catalog audit API endpoints."""

from typing import Any
from fastapi import APIRouter, Depends, Query
from pymongo.database import Database

from app.core.exceptions import ResourceNotFoundException
from app.db.client import get_db
from app.db.repositories.knowledge import KnowledgeRepository
from app.schemas.common import ApiResponse, ResponseMeta
from app.schemas.knowledge import (
    KnowledgeConflictItem,
    KnowledgeDocumentCreate,
    KnowledgeDocumentResponse,
    KnowledgeEvidenceSchema,
    KnowledgeSearchResponse,
    KnowledgeStatsResponse,
)
from app.services.knowledge import KnowledgeService, detect_conflicts
from app.services.knowledge_ingestion import KnowledgeIngestionService

router = APIRouter(prefix="/knowledge", tags=["RAG Knowledge Layer"])


@router.get(
    "/search",
    response_model=ApiResponse[KnowledgeSearchResponse],
    summary="Semantic and metadata knowledge search with composite ranking",
)
async def search_knowledge(
    query: str = Query(..., min_length=1, description="Search query string"),
    city_id: str | None = Query(default=None, description="Optional city identifier"),
    country_id: str | None = Query(default=None, description="Optional country identifier"),
    category: str | None = Query(default=None, description="Optional category filter"),
    subcategory: str | None = Query(default=None, description="Optional subcategory filter"),
    scope: str | None = Query(default=None, description="Optional scope filter (global, country, city)"),
    authority_tier: str | None = Query(default=None, description="Optional authority tier filter"),
    top_k: int = Query(default=5, ge=1, le=20, description="Max results"),
    min_score: float = Query(default=0.0, ge=0.0, le=1.0, description="Minimum composite score threshold"),
    database: Database = Depends(get_db),
) -> ApiResponse[KnowledgeSearchResponse]:
    """Retrieve grounded knowledge evidence items matching query and metadata constraints."""
    repo = KnowledgeRepository(database)
    service = KnowledgeService(repo)

    categories = [category.strip()] if category else None
    subcategories = [subcategory.strip()] if subcategory else None

    evidence_items = await service.search_knowledge(
        query=query,
        city_id=city_id,
        country_id=country_id,
        categories=categories,
        subcategories=subcategories,
        scope=scope,
        authority_tier=authority_tier,
        top_k=top_k,
        min_score=min_score,
    )

    schema_evidence = [
        KnowledgeEvidenceSchema(
            evidence_id=ev.evidence_id,
            document_id=ev.document_id,
            chunk_id=ev.chunk_id,
            title=ev.title,
            source=ev.source,
            source_url=ev.source_url,
            publisher=ev.publisher,
            authority_tier=ev.authority_tier,
            authority_score=ev.authority_score,
            scope=ev.scope,
            freshness_status=ev.freshness_status,
            fetched_at=ev.fetched_at,
            updated_at=ev.updated_at,
            text=ev.text,
            category=ev.category,
            subcategory=ev.subcategory,
            city_id=ev.city_id,
            country_id=ev.country_id,
            retrieved_at=ev.retrieved_at,
            retrieval_score=ev.retrieval_score,
            score_breakdown=ev.score_breakdown,
            metadata=ev.metadata,
        )
        for ev in evidence_items
    ]

    raw_conflicts = detect_conflicts(evidence_items)
    conflicts = [
        KnowledgeConflictItem(
            category=c["category"],
            source_a=c["source_a"],
            source_b=c["source_b"],
            evidence_id_a=c["evidence_id_a"],
            evidence_id_b=c["evidence_id_b"],
            difference_note=c["difference_note"],
        )
        for c in raw_conflicts
    ]

    return ApiResponse(
        data=KnowledgeSearchResponse(
            query=query,
            total_found=len(schema_evidence),
            evidence=schema_evidence,
            conflict_detected=len(conflicts) > 0,
            conflicts=conflicts,
        ),
        meta=ResponseMeta(source="knowledge_search"),
    )


@router.post(
    "/documents",
    response_model=ApiResponse[KnowledgeDocumentResponse],
    summary="Ingest a knowledge document",
)
async def ingest_document(
    payload: KnowledgeDocumentCreate,
    database: Database = Depends(get_db),
) -> ApiResponse[KnowledgeDocumentResponse]:
    """Ingest, normalize, chunk, and embed a new knowledge document into the knowledge layer."""
    repo = KnowledgeRepository(database)
    ingestion_service = KnowledgeIngestionService(repo)

    doc, chunk_count = await ingestion_service.ingest_document(
        title=payload.title,
        content=payload.content,
        source=payload.source,
        source_url=payload.source_url,
        publisher=payload.publisher,
        authority_tier=payload.authority_tier,
        authority_score=payload.authority_score,
        scope=payload.scope,
        country_id=payload.country_id,
        city_id=payload.city_id,
        category=payload.category,
        subcategory=payload.subcategory,
        language=payload.language,
        content_language=payload.content_language,
        source_type=payload.source_type,
        ingestion_method=payload.ingestion_method,
        canonical_url=payload.canonical_url,
        freshness_policy=payload.freshness_policy,
        review_required=payload.review_required,
        published_at=payload.published_at,
        metadata=payload.metadata,
    )

    return ApiResponse(
        data=KnowledgeDocumentResponse(
            document_id=doc.document_id,
            title=doc.title,
            source=doc.source,
            source_url=doc.source_url,
            publisher=doc.publisher,
            authority_tier=doc.authority_tier,
            authority_score=doc.authority_score,
            scope=doc.scope,
            country_id=doc.country_id,
            city_id=doc.city_id,
            category=doc.category,
            subcategory=doc.subcategory,
            language=doc.language,
            content_language=doc.content_language,
            source_type=doc.source_type,
            ingestion_method=doc.ingestion_method,
            canonical_url=doc.canonical_url,
            freshness_policy=doc.freshness_policy,
            review_required=doc.review_required,
            published_at=doc.published_at,
            fetched_at=doc.fetched_at,
            checksum=doc.checksum,
            chunks_count=chunk_count,
            status=doc.status,
            metadata=doc.metadata,
        ),
        meta=ResponseMeta(source="knowledge_ingestion"),
    )


@router.get(
    "/stats",
    response_model=ApiResponse[KnowledgeStatsResponse],
    summary="Knowledge base statistics",
)
def get_knowledge_stats(
    database: Database = Depends(get_db),
) -> ApiResponse[KnowledgeStatsResponse]:
    """Retrieve aggregate counts by category, scope, authority tier, and freshness."""
    service = KnowledgeService(KnowledgeRepository(database))
    stats = service.get_stats()
    return ApiResponse(
        data=KnowledgeStatsResponse(**stats),
        meta=ResponseMeta(source="knowledge_stats"),
    )


@router.get(
    "/sources",
    response_model=ApiResponse[list[dict[str, Any]]],
    summary="List authoritative sources",
)
def list_knowledge_sources(
    database: Database = Depends(get_db),
) -> ApiResponse[list[dict[str, Any]]]:
    """Retrieve catalog of distinct registered knowledge publishers and sources."""
    service = KnowledgeService(KnowledgeRepository(database))
    sources = service.list_sources()
    return ApiResponse(
        data=sources,
        meta=ResponseMeta(source="knowledge_sources"),
    )


@router.get(
    "/audit",
    response_model=ApiResponse[dict[str, Any]],
    summary="Knowledge base audit and integrity check",
)
def audit_knowledge_corpus(
    database: Database = Depends(get_db),
) -> ApiResponse[dict[str, Any]]:
    """Evaluate integrity, identifying unchunked documents, stale documents, and duplicates."""
    service = KnowledgeService(KnowledgeRepository(database))
    audit_data = service.audit_corpus()
    return ApiResponse(
        data=audit_data,
        meta=ResponseMeta(source="knowledge_audit"),
    )


@router.get(
    "/documents/{document_id}",
    response_model=ApiResponse[KnowledgeDocumentResponse],
    summary="Get knowledge document by ID",
)
def get_document_by_id(
    document_id: str,
    database: Database = Depends(get_db),
) -> ApiResponse[KnowledgeDocumentResponse]:
    """Retrieve metadata and status for a knowledge document."""
    repo = KnowledgeRepository(database)
    service = KnowledgeService(repo)

    doc = service.get_document(document_id)
    if not doc:
        raise ResourceNotFoundException(f"Knowledge document '{document_id}' not found.")

    chunks = repo.get_chunks_by_document(document_id)

    return ApiResponse(
        data=KnowledgeDocumentResponse(
            document_id=doc["document_id"],
            title=doc.get("title", ""),
            source=doc.get("source", ""),
            source_url=doc.get("source_url"),
            publisher=doc.get("publisher"),
            authority_tier=doc.get("authority_tier", "tier_1_official"),
            authority_score=float(doc.get("authority_score", 1.0)),
            scope=doc.get("scope", "country"),
            country_id=doc.get("country_id"),
            city_id=doc.get("city_id"),
            category=doc.get("category", "city_information"),
            subcategory=doc.get("subcategory"),
            language=doc.get("language", "en"),
            content_language=doc.get("content_language", "en"),
            source_type=doc.get("source_type", "official"),
            ingestion_method=doc.get("ingestion_method", "curated_source"),
            canonical_url=doc.get("canonical_url"),
            freshness_policy=doc.get("freshness_policy", "moderate_180d"),
            review_required=bool(doc.get("review_required", False)),
            published_at=doc.get("published_at"),
            fetched_at=doc.get("fetched_at", ""),
            checksum=doc.get("checksum", ""),
            chunks_count=len(chunks),
            status=doc.get("status", "active"),
            metadata=doc.get("metadata", {}),
        ),
        meta=ResponseMeta(source="knowledge_document"),
    )
