"""Knowledge search and document management API endpoints."""

from fastapi import APIRouter, Depends, Query
from pymongo.database import Database

from app.core.exceptions import ResourceNotFoundException
from app.db.client import get_db
from app.db.repositories.knowledge import KnowledgeRepository
from app.schemas.common import ApiResponse, ResponseMeta
from app.schemas.knowledge import (
    KnowledgeDocumentCreate,
    KnowledgeDocumentResponse,
    KnowledgeEvidenceSchema,
    KnowledgeSearchResponse,
)
from app.services.knowledge import KnowledgeService
from app.services.knowledge_ingestion import KnowledgeIngestionService

router = APIRouter(prefix="/knowledge", tags=["RAG Knowledge Layer"])


@router.get(
    "/search",
    response_model=ApiResponse[KnowledgeSearchResponse],
    summary="Semantic and metadata knowledge search",
)
async def search_knowledge(
    query: str = Query(..., min_length=1, description="Search query string"),
    city_id: str | None = Query(default=None, description="Optional city identifier"),
    country_id: str | None = Query(default=None, description="Optional country identifier"),
    category: str | None = Query(default=None, description="Optional category filter"),
    top_k: int = Query(default=5, ge=1, le=20, description="Max results"),
    min_score: float = Query(default=0.0, ge=0.0, le=1.0, description="Minimum cosine similarity"),
    database: Database = Depends(get_db),
) -> ApiResponse[KnowledgeSearchResponse]:
    """Retrieve grounded knowledge evidence items matching query and metadata constraints."""
    repo = KnowledgeRepository(database)
    service = KnowledgeService(repo)

    categories = [category.strip()] if category else None
    evidence_items = await service.search_knowledge(
        query=query,
        city_id=city_id,
        country_id=country_id,
        categories=categories,
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
            text=ev.text,
            category=ev.category,
            city_id=ev.city_id,
            country_id=ev.country_id,
            retrieved_at=ev.retrieved_at,
            retrieval_score=ev.retrieval_score,
            metadata=ev.metadata,
        )
        for ev in evidence_items
    ]

    return ApiResponse(
        data=KnowledgeSearchResponse(
            query=query,
            total_found=len(schema_evidence),
            evidence=schema_evidence,
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
        country_id=payload.country_id,
        city_id=payload.city_id,
        category=payload.category,
        language=payload.language,
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
            country_id=doc.country_id,
            city_id=doc.city_id,
            category=doc.category,
            language=doc.language,
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
            country_id=doc.get("country_id"),
            city_id=doc.get("city_id"),
            category=doc.get("category", "city_information"),
            language=doc.get("language", "en"),
            published_at=doc.get("published_at"),
            fetched_at=doc.get("fetched_at", ""),
            checksum=doc.get("checksum", ""),
            chunks_count=len(chunks),
            status=doc.get("status", "active"),
            metadata=doc.get("metadata", {}),
        ),
        meta=ResponseMeta(source="knowledge_document"),
    )
