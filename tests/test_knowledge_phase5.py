"""Unit and integration tests for Phase 5: RAG Knowledge Layer."""

import asyncio
import math
import pytest
from unittest.mock import AsyncMock, MagicMock

from app.agents.location import LocationAgent
from app.agents.environment import EnvironmentAgent
from app.db.repositories.knowledge import KnowledgeRepository, cosine_similarity
from app.models.agent import AgentRequest, AgentStatus
from app.models.knowledge import (
    DocumentStatus,
    KnowledgeCategory,
    KnowledgeChunk,
    KnowledgeDocument,
    KnowledgeEvidence,
)
from app.orchestrator.context import OrchestrationContext
from app.orchestrator.orchestrator import UrbanLensOrchestrator
from app.providers.embedding.base import BaseEmbeddingProvider
from app.providers.embedding.factory import get_embedding_provider
from app.providers.embedding.hash_provider import DeterministicHashEmbeddingProvider
from app.schemas.knowledge import (
    KnowledgeDocumentCreate,
    KnowledgeDocumentResponse,
    KnowledgeEvidenceSchema,
    KnowledgeSearchResponse,
)
from app.services.chunking import chunk_text
from app.services.knowledge import KnowledgeService
from app.services.knowledge_ingestion import (
    KnowledgeIngestionService,
    compute_checksum,
    normalize_content,
)
from tests.conftest import MockDatabase


# ==============================================================================
# A. Document Models & Schemas
# ==============================================================================


def test_knowledge_document_model_defaults() -> None:
    doc = KnowledgeDocument(
        document_id="doc_test1",
        title="Tokyo Transit Guide",
        source="Tokyo Metropolitan Government",
        content="Comprehensive guide to the Tokyo subway and bus system.",
        checksum="abc123hash",
        city_id="tokyo_jp",
        category=KnowledgeCategory.TRANSPORT.value,
    )
    assert doc.document_id == "doc_test1"
    assert doc.language == "en"
    assert doc.status == DocumentStatus.ACTIVE.value
    assert doc.fetched_at is not None
    assert doc.source_url is None


def test_knowledge_evidence_schema_validation() -> None:
    schema = KnowledgeEvidenceSchema(
        evidence_id="ev_chk_1",
        document_id="doc_1",
        chunk_id="chk_1",
        title="Mumbai Cost Overview",
        source="Municipal Report",
        text="Average rental prices in Bandra West range from 45,000 to 75,000 INR.",
        category="housing",
        city_id="city_1356226629",
        retrieved_at="2026-10-27T00:00:00Z",
        retrieval_score=0.88,
    )
    assert schema.retrieval_score == 0.88
    assert schema.city_id == "city_1356226629"


# ==============================================================================
# B. Normalization & Checksumming
# ==============================================================================


def test_normalize_content() -> None:
    raw = "   Heading text  with   spaces\r\n\r\n\r\n=== Section ===\n\nBody text.   \n\n\n"
    normalized = normalize_content(raw)
    assert "\r" not in normalized
    assert "   " not in normalized
    assert "Heading text with spaces" in normalized
    assert "Body text." in normalized


def test_compute_checksum_deterministic() -> None:
    text1 = "Grounded municipal observations for Tokyo."
    text2 = "Grounded municipal observations for Tokyo."
    text3 = "Different text."
    assert compute_checksum(text1) == compute_checksum(text2)
    assert compute_checksum(text1) != compute_checksum(text3)


# ==============================================================================
# C. Chunking Engine
# ==============================================================================


def test_chunk_text_short_document() -> None:
    text = "Short text describing city climate and geography."
    chunks = chunk_text(text, chunk_size=600, overlap=100)
    assert len(chunks) == 1
    assert chunks[0] == text


def test_chunk_text_boundary_awareness() -> None:
    para1 = "Paris is the capital of France. " * 8  # ~256 chars
    para2 = "The city is divided into twenty arrondissements. " * 8  # ~384 chars
    para3 = "Public transport is operated by RATP. " * 8
    full_text = f"{para1}\n\n{para2}\n\n{para3}"

    chunks = chunk_text(full_text, chunk_size=500, overlap=100)
    assert len(chunks) >= 2
    for chunk in chunks:
        assert len(chunk) > 40


# ==============================================================================
# D. Embedding Abstraction
# ==============================================================================


def test_deterministic_hash_embedding_provider() -> None:
    async def _test():
        provider = DeterministicHashEmbeddingProvider(dimension=128)
        assert provider.dimension == 128
        assert provider.provider_name == "deterministic-hash"

        vec1 = await provider.embed_query("Tokyo metro public transit")
        vec2 = await provider.embed_query("Tokyo metro public transit")
        vec3 = await provider.embed_query("Desert agricultural irrigation")

        # Determinism
        assert vec1 == vec2

        # L2 Normalization
        norm1 = math.sqrt(sum(v * v for v in vec1))
        assert math.isclose(norm1, 1.0, rel_tol=1e-4)

        # Similarity
        sim_identical = cosine_similarity(vec1, vec2)
        sim_different = cosine_similarity(vec1, vec3)
        assert math.isclose(sim_identical, 1.0, rel_tol=1e-4)
        assert sim_different < sim_identical

    asyncio.run(_test())


def test_embedding_provider_empty_string() -> None:
    async def _test():
        provider = DeterministicHashEmbeddingProvider(dimension=64)
        vec = await provider.embed_query("")
        assert len(vec) == 64
        assert all(v == 0.0 for v in vec)

    asyncio.run(_test())


def test_embedding_factory() -> None:
    provider = get_embedding_provider("hash")
    assert isinstance(provider, DeterministicHashEmbeddingProvider)

    with pytest.raises(ValueError, match="OPENAI_API_KEY"):
        get_embedding_provider("openai")

    with pytest.raises(ValueError, match="Unknown or unsupported"):
        get_embedding_provider("nonexistent_provider")


# ==============================================================================
# E. Repository & CRUD
# ==============================================================================


def test_knowledge_repository_crud() -> None:
    db = MockDatabase()
    repo = KnowledgeRepository(db)

    doc = KnowledgeDocument(
        document_id="doc_mumbai_reloc",
        title="Mumbai Relocation Essentials",
        source="Official Portal",
        content="Key guidelines for settling in Mumbai.",
        checksum="hash_mumbai_123",
        city_id="city_1356226629",
        category="relocation",
    )
    saved = repo.add_document(doc)
    assert saved["document_id"] == "doc_mumbai_reloc"

    fetched = repo.get_document("doc_mumbai_reloc")
    assert fetched is not None
    assert fetched["title"] == "Mumbai Relocation Essentials"

    by_checksum = repo.get_document_by_checksum("hash_mumbai_123")
    assert by_checksum is not None
    assert by_checksum["document_id"] == "doc_mumbai_reloc"

    # Add chunks
    chunks = [
        KnowledgeChunk(
            chunk_id="doc_mumbai_reloc_chk_0",
            document_id="doc_mumbai_reloc",
            chunk_index=0,
            text="Rental agreements require police verification.",
            char_count=45,
            token_count=6,
            embedding=[0.1] * 128,
            city_id="city_1356226629",
            category="relocation",
        )
    ]
    added_count = repo.add_chunks(chunks)
    assert added_count == 1

    doc_chunks = repo.get_chunks_by_document("doc_mumbai_reloc")
    assert len(doc_chunks) == 1

    # Delete
    deleted = repo.delete_document("doc_mumbai_reloc")
    assert deleted is True
    assert repo.get_document("doc_mumbai_reloc") is None
    assert len(repo.get_chunks_by_document("doc_mumbai_reloc")) == 0


# ==============================================================================
# F. Ingestion Service (Idempotency & Deduplication)
# ==============================================================================


def test_knowledge_ingestion_idempotency() -> None:
    async def _test():
        db = MockDatabase()
        repo = KnowledgeRepository(db)
        ingestion = KnowledgeIngestionService(repo, embedding_provider=DeterministicHashEmbeddingProvider(64))

        content = "Tokyo has extensive commuter rail operated by JR East and Tokyo Metro."
        doc1, count1 = await ingestion.ingest_document(
            title="Tokyo Rail Overview",
            content=content,
            source="JR East / Tokyo Metro",
            city_id="tokyo_jp",
            category="transport",
        )
        assert count1 >= 1

        # Ingesting identical content again returns existing document without duplicate chunks
        doc2, count2 = await ingestion.ingest_document(
            title="Tokyo Rail Overview Duplicate",
            content=content,
            source="JR East / Tokyo Metro",
            city_id="tokyo_jp",
            category="transport",
        )
        assert doc2.document_id == doc1.document_id
        assert count2 == count1
        # Verify no duplicated chunks in storage
        all_chunks = repo.get_chunks_by_document(doc1.document_id)
        assert len(all_chunks) == count1

    asyncio.run(_test())


# ==============================================================================
# G. Retrieval Service & Metadata Filtering
# ==============================================================================


def test_knowledge_search_semantic_and_filters() -> None:
    async def _test():
        db = MockDatabase()
        repo = KnowledgeRepository(db)
        embedder = DeterministicHashEmbeddingProvider(128)
        ingestion = KnowledgeIngestionService(repo, embedding_provider=embedder)
        retrieval = KnowledgeService(repo, embedding_provider=embedder)

        # Ingest doc 1: Tokyo transit
        await ingestion.ingest_document(
            title="Tokyo Subway Network",
            content="Tokyo Metro operates 9 subway lines with high frequency and punctual service.",
            source="Tokyo Metro",
            city_id="tokyo_jp",
            category="transport",
        )

        # Ingest doc 2: Tokyo healthcare
        await ingestion.ingest_document(
            title="Tokyo Medical Care",
            content="Emergency medical care in Tokyo is accessible via the 119 hotline with multilingual support.",
            source="Bureau of Social Welfare",
            city_id="tokyo_jp",
            category="healthcare",
        )

        # Ingest doc 3: Mumbai transit
        await ingestion.ingest_document(
            title="Mumbai Local Train",
            content="Mumbai suburban railway comprises Western, Central, and Harbour lines.",
            source="Central Railway",
            city_id="city_1356226629",
            category="transport",
        )

        # 1. Search with city_id filter
        tokyo_transit = await retrieval.search_knowledge(
            query="subway lines and trains",
            city_id="tokyo_jp",
            categories=["transport"],
            top_k=5,
        )
        assert len(tokyo_transit) >= 1
        assert all(e.city_id == "tokyo_jp" for e in tokyo_transit)
        assert tokyo_transit[0].category == "transport"
        assert tokyo_transit[0].source == "Tokyo Metro"

        # 2. Search category filter
        tokyo_health = await retrieval.search_knowledge(
            query="hospital doctor emergency medical",
            city_id="tokyo_jp",
            categories=["healthcare"],
            top_k=5,
        )
        assert len(tokyo_health) >= 1
        assert tokyo_health[0].category == "healthcare"

        # 3. Search with high threshold yields clean empty result
        empty_res = await retrieval.search_knowledge(
            query="astronaut space mission on mars",
            city_id="tokyo_jp",
            min_score=0.99,
        )
        assert empty_res == []

    asyncio.run(_test())


# ==============================================================================
# H. Agent Knowledge Integration
# ==============================================================================


def test_location_agent_with_knowledge() -> None:
    async def _test():
        db = MockDatabase()
        repo = KnowledgeRepository(db)
        embedder = DeterministicHashEmbeddingProvider(64)
        ingestion = KnowledgeIngestionService(repo, embedding_provider=embedder)

        await ingestion.ingest_document(
            title="Tokyo Administrative Overview",
            content="Tokyo comprises 23 special wards, 26 cities, and suburban municipalities.",
            source="Tokyo Metropolitan Government",
            city_id="tokyo_jp",
            category="city_information",
        )

        agent = LocationAgent(db, knowledge_service=KnowledgeService(repo, embedding_provider=embedder))
        result = await agent.execute_async(AgentRequest(city_id="tokyo_jp", query="administrative wards in Tokyo"))

        assert result.status == AgentStatus.COMPLETE
        assert len(result.knowledge_evidence) >= 1
        ev = result.knowledge_evidence[0]
        assert ev.source == "Tokyo Metropolitan Government"
        assert "Tokyo" in ev.text
        # Source provenance should record knowledge source
        assert any(s.provider == "knowledge" for s in result.sources)

    asyncio.run(_test())


def test_environment_agent_with_knowledge() -> None:
    async def _test():
        db = MockDatabase()
        repo = KnowledgeRepository(db)
        embedder = DeterministicHashEmbeddingProvider(64)
        ingestion = KnowledgeIngestionService(repo, embedding_provider=embedder)

        await ingestion.ingest_document(
            title="Tokyo Climate Guidance",
            content="Tokyo experiences humid subtropical climate with mild winters and hot humid summers.",
            source="Japan Meteorological Agency",
            city_id="tokyo_jp",
            category="environment",
        )

        agent = EnvironmentAgent(db, knowledge_service=KnowledgeService(repo, embedding_provider=embedder))
        result = await agent.execute_async(AgentRequest(city_id="tokyo_jp", query="climate and seasons in Tokyo"))

        assert len(result.knowledge_evidence) >= 1
        assert result.knowledge_evidence[0].category == "environment"

    asyncio.run(_test())


# ==============================================================================
# I. Orchestrator Synthesis & Knowledge Grounding
# ==============================================================================


def test_orchestrator_synthesizes_knowledge_evidence() -> None:
    async def _test():
        db = MockDatabase()
        repo = KnowledgeRepository(db)
        embedder = DeterministicHashEmbeddingProvider(64)
        ingestion = KnowledgeIngestionService(repo, embedding_provider=embedder)

        await ingestion.ingest_document(
            title="Living in Tokyo Guide",
            content="Tokyo offers safe neighborhoods, punctual trains, and world-class culinary options.",
            source="Tokyo Relocation Bureau",
            city_id="tokyo_jp",
            category="relocation",
        )

        knowledge_svc = KnowledgeService(repo, embedding_provider=embedder)
        orch = UrbanLensOrchestrator(database=db, knowledge_service=knowledge_svc)

        ctx = OrchestrationContext(
            city_id="tokyo_jp",
            query="Should I move to Tokyo? Tell me about living and trains.",
        )
        synthesis = await orch.synthesize_async(ctx)

        assert synthesis.city_id == "tokyo_jp"
        assert len(synthesis.knowledge_evidence) >= 1
        assert "[Grounded Knowledge Evidence]" in synthesis.summary
        assert any(s.provider == "knowledge" for s in synthesis.sources)

    asyncio.run(_test())


# ==============================================================================
# J. API Route Integration Tests
# ==============================================================================


def test_api_knowledge_search_and_document_endpoints(client) -> None:
    # 1. Ingest document via API
    ingest_payload = {
        "title": "Tokyo Housing Regulations",
        "content": "Standard residential leases in Tokyo typically run for two years with renewal terms.",
        "source": "Ministry of Land, Infrastructure, Transport and Tourism",
        "city_id": "tokyo_jp",
        "category": "housing",
    }
    resp = client.post("/api/v1/knowledge/documents", json=ingest_payload)
    assert resp.status_code == 200
    data = resp.json()["data"]
    doc_id = data["document_id"]
    assert doc_id.startswith("doc_")
    assert data["chunks_count"] >= 1

    # 2. Get document by ID
    get_resp = client.get(f"/api/v1/knowledge/documents/{doc_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["data"]["title"] == "Tokyo Housing Regulations"

    # 3. Search knowledge via API
    search_resp = client.get(
        "/api/v1/knowledge/search",
        params={"query": "residential leases and housing", "city_id": "tokyo_jp"},
    )
    assert search_resp.status_code == 200
    search_data = search_resp.json()["data"]
    assert search_data["total_found"] >= 1
    assert search_data["evidence"][0]["category"] == "housing"

    # 4. Intelligence query endpoint returns knowledge_evidence
    query_resp = client.post(
        "/api/v1/intelligence/query",
        json={"city_id": "tokyo_jp", "query": "housing rules in Tokyo"},
    )
    assert query_resp.status_code == 200
    q_data = query_resp.json()["data"]
    assert "knowledge_evidence" in q_data
    assert len(q_data["knowledge_evidence"]) >= 1
