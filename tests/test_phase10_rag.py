"""Comprehensive unit and integration tests for Phase 10: Global RAG Knowledge Expansion."""

import asyncio
from datetime import datetime, timedelta, timezone
import pytest
from unittest.mock import AsyncMock, patch

from app.db.repositories.knowledge import KnowledgeRepository, cosine_similarity
from app.models.knowledge import (
    DocumentStatus,
    KnowledgeChunk,
    KnowledgeDocument,
    KnowledgeEvidence,
)
from app.models.taxonomy import (
    AUTHORITY_TIER_SCORES,
    AuthorityTier,
    FreshnessPolicy,
    FreshnessStatus,
    KnowledgeCategory,
    KnowledgeScope,
    TAXONOMY_TREE,
    calculate_freshness,
    is_valid_category,
    is_valid_subcategory,
    normalize_category,
)
from app.providers.embedding.hash_provider import DeterministicHashEmbeddingProvider
from app.schemas.knowledge import (
    KnowledgeDocumentCreate,
    KnowledgeDocumentResponse,
    KnowledgeEvidenceSchema,
    KnowledgeSearchResponse,
    KnowledgeStatsResponse,
)
from app.services.chunking import chunk_text, is_heading
from app.services.knowledge import KnowledgeService, detect_conflicts
from app.services.knowledge_ingestion import (
    KnowledgeIngestionService,
    compute_checksum,
    fetch_url_content,
    normalize_content,
)
from tests.conftest import MockDatabase


# ==============================================================================
# 1. TAXONOMY & NORMALIZATION TESTS
# ==============================================================================


def test_taxonomy_categories_and_subcategories() -> None:
    # Supported categories
    assert is_valid_category("immigration")
    assert is_valid_category("transport")
    assert is_valid_category("healthcare")
    assert is_valid_category("city_information")
    assert not is_valid_category("quantum_physics")

    # Supported subcategories
    assert is_valid_subcategory("immigration", "visa")
    assert is_valid_subcategory("immigration", "residency")
    assert is_valid_subcategory("transport", "metro")
    assert is_valid_subcategory("healthcare", "hospitals")
    assert not is_valid_subcategory("transport", "quantum_teleportation")


def test_taxonomy_normalization() -> None:
    assert normalize_category("transportation") == "transport"
    assert normalize_category("health") == "healthcare"
    assert normalize_category("accommodation") == "housing"
    assert normalize_category("city_info") == "city_information"
    assert normalize_category("unknown_domain") == "city_information"


# ==============================================================================
# 2. FRESHNESS CALCULATION TESTS
# ==============================================================================


def test_calculate_freshness_high_policy() -> None:
    now = datetime.now(timezone.utc)

    # 10 days old -> Fresh with high score
    recent_iso = (now - timedelta(days=10)).isoformat()
    status, score = calculate_freshness(recent_iso, category="immigration", policy=FreshnessPolicy.HIGH_90D.value)
    assert status == FreshnessStatus.FRESH
    assert 0.85 <= score <= 1.0

    # 120 days old -> Aging bracket (90-180)
    aging_iso = (now - timedelta(days=120)).isoformat()
    status, score = calculate_freshness(aging_iso, category="immigration", policy=FreshnessPolicy.HIGH_90D.value)
    assert status == FreshnessStatus.AGING
    assert 0.50 <= score <= 0.85

    # 250 days old -> Stale bracket (>180)
    stale_iso = (now - timedelta(days=250)).isoformat()
    status, score = calculate_freshness(stale_iso, category="immigration", policy=FreshnessPolicy.HIGH_90D.value)
    assert status == FreshnessStatus.STALE
    assert score <= 0.50


def test_calculate_freshness_static_and_unknown() -> None:
    status, score = calculate_freshness(None, category="city_information")
    assert status == FreshnessStatus.UNKNOWN
    assert score == 0.5

    status, score = calculate_freshness("2020-01-01T00:00:00Z", policy=FreshnessPolicy.STATIC.value)
    assert status == FreshnessStatus.FRESH
    assert score == 1.0


# ==============================================================================
# 3. AUTHORITY TIER TESTS
# ==============================================================================


def test_authority_tiers_weights() -> None:
    assert AUTHORITY_TIER_SCORES[AuthorityTier.TIER_1_OFFICIAL.value] == 1.0
    assert AUTHORITY_TIER_SCORES[AuthorityTier.TIER_2_INTERGOVERNMENTAL.value] == 0.85
    assert AUTHORITY_TIER_SCORES[AuthorityTier.TIER_3_SECONDARY.value] == 0.60
    assert AUTHORITY_TIER_SCORES[AuthorityTier.TIER_4_COMMUNITY.value] == 0.35


# ==============================================================================
# 4. NORMALIZATION & HTML STRIPPING TESTS
# ==============================================================================


def test_normalize_content_html_and_unicode() -> None:
    raw_html = """
    <html>
      <head><script>alert('xss');</script><style>.bad{color:red;}</style></head>
      <body>
        <h1>Official Tokyo Immigration Portal</h1>
        <p>Visas require <b>passport &amp; certificate</b> of eligibility.</p>
        <div>---====---</div>
        <p>Line 2 with   excessive    spaces.</p>
      </body>
    </html>
    """
    clean = normalize_content(raw_html)
    assert "alert" not in clean
    assert "<script>" not in clean
    assert "<style>" not in clean
    assert "<h1>" not in clean
    assert "Official Tokyo Immigration Portal" in clean
    assert "passport & certificate" in clean
    assert "excessive spaces." in clean


def test_compute_checksum() -> None:
    text = "Ministry of External Affairs official notice."
    c1 = compute_checksum(text)
    c2 = compute_checksum(text)
    assert c1 == c2
    assert len(c1) == 64


# ==============================================================================
# 5. STRUCTURE-AWARE CHUNKING TESTS
# ==============================================================================


def test_structure_aware_chunking_headings() -> None:
    assert is_heading("# Section Title")
    assert is_heading("ELIGIBILITY REQUIREMENTS:")
    assert not is_heading("This is just regular running narrative paragraph text that is relatively long.")

    text = """# Heading One
This is the introductory paragraph for section one explaining the first procedure in detail.

## Heading Two
This is the subsequent paragraph explaining the second procedure with full clarity and requirements."""

    chunks = chunk_text(text, chunk_size=300, overlap=50)
    assert len(chunks) >= 1
    # Check that headings are intact
    assert any("# Heading One" in c for c in chunks)


# ==============================================================================
# 6. COMPOSITE RETRIEVAL SCORING & CONFLICT DETECTION
# ==============================================================================


def test_composite_scoring_and_scope_filtering() -> None:
    db = MockDatabase()
    repo = KnowledgeRepository(db)
    embedder = DeterministicHashEmbeddingProvider(64)

    # Add Tokyo chunk (Tier 1, city scope)
    doc_tokyo = KnowledgeDocument(
        document_id="doc_t1",
        title="Tokyo Subway Guide",
        source="Tokyo Metro",
        content="Subway network details.",
        checksum="hash_t1",
        city_id="tokyo_jp",
        country_id="japan",
        category="transport",
        authority_tier=AuthorityTier.TIER_1_OFFICIAL.value,
        authority_score=1.0,
        scope=KnowledgeScope.CITY.value,
    )
    repo.add_document(doc_tokyo)

    chunk_tokyo = KnowledgeChunk(
        chunk_id="t1_chk0",
        document_id="doc_t1",
        chunk_index=0,
        text="Tokyo Metro operates 9 subway lines across the central ward area.",
        char_count=65,
        token_count=10,
        embedding=[0.1] * 64,
        source="Tokyo Metro",
        authority_tier=AuthorityTier.TIER_1_OFFICIAL.value,
        authority_score=1.0,
        scope=KnowledgeScope.CITY.value,
        city_id="tokyo_jp",
        country_id="japan",
        category="transport",
        fetched_at=datetime.now(timezone.utc).isoformat(),
    )
    repo.add_chunks([chunk_tokyo])

    # Add Mumbai chunk (Tier 3, city scope)
    chunk_mumbai = KnowledgeChunk(
        chunk_id="m1_chk0",
        document_id="doc_m1",
        chunk_index=0,
        text="Mumbai local trains run on Western and Central lines.",
        char_count=52,
        token_count=9,
        embedding=[0.1] * 64,
        source="Travel Blog",
        authority_tier=AuthorityTier.TIER_3_SECONDARY.value,
        authority_score=0.60,
        scope=KnowledgeScope.CITY.value,
        city_id="mumbai_in",
        country_id="india",
        category="transport",
        fetched_at=datetime.now(timezone.utc).isoformat(),
    )
    repo.add_chunks([chunk_mumbai])

    # Search for Tokyo
    query_emb = [0.1] * 64
    results = repo.search_chunks(
        query_embedding=query_emb,
        city_id="tokyo_jp",
        country_id="japan",
        categories=["transport"],
    )

    # Mumbai should be excluded because query is specific to Tokyo
    assert len(results) == 1
    assert results[0]["city_id"] == "tokyo_jp"
    assert "score_breakdown" in results[0]
    bd = results[0]["score_breakdown"]
    assert "semantic" in bd
    assert "authority" in bd
    assert "freshness" in bd
    assert "scope" in bd
    assert bd["scope"] == 1.0  # Exact city match
    assert bd["authority"] == 1.0  # Tier 1


def test_conflict_detection() -> None:
    ev1 = KnowledgeEvidence(
        evidence_id="ev_1",
        document_id="doc_1",
        chunk_id="chk_1",
        title="Official Visa Manual",
        source="Ministry of Foreign Affairs",
        text="Registration is strictly required within 14 days of entry for all residents.",
        category="immigration",
        authority_tier=AuthorityTier.TIER_1_OFFICIAL.value,
    )
    ev2 = KnowledgeEvidence(
        evidence_id="ev_2",
        document_id="doc_2",
        chunk_id="chk_2",
        title="Informal Expat Blog",
        source="Tokyo Expat Community",
        text="Registration is optional if staying less than 90 days on temporary status.",
        category="immigration",
        authority_tier=AuthorityTier.TIER_4_COMMUNITY.value,
    )

    conflicts = detect_conflicts([ev1, ev2])
    assert len(conflicts) == 1
    assert conflicts[0]["category"] == "immigration"
    assert "mandatory vs optional" in conflicts[0]["difference_note"]


# ==============================================================================
# 7. REPOSITORY AUDIT & STATS TESTS
# ==============================================================================


def test_repository_stats_and_audit() -> None:
    db = MockDatabase()
    repo = KnowledgeRepository(db)

    doc = KnowledgeDocument(
        document_id="doc_audit_test",
        title="London Transport Authority Guide",
        source="Transport for London",
        content="Oyster card and contactless payment instructions.",
        checksum="hash_audit_1",
        city_id="london_uk",
        country_id="uk",
        category="transport",
        authority_tier=AuthorityTier.TIER_1_OFFICIAL.value,
        scope=KnowledgeScope.CITY.value,
    )
    repo.add_document(doc)

    # Before adding chunk -> audit should detect unchunked doc
    audit_pre = repo.audit_corpus()
    assert audit_pre["unchunked_documents_count"] == 1
    assert "doc_audit_test" in audit_pre["unchunked_document_ids"]

    # Add chunk
    chunk = KnowledgeChunk(
        chunk_id="doc_audit_test_chk0",
        document_id="doc_audit_test",
        chunk_index=0,
        text="Oyster cards can be tapped at all London Underground gates.",
        char_count=58,
        token_count=10,
        embedding=[0.2] * 64,
        source="Transport for London",
        city_id="london_uk",
        category="transport",
        fetched_at=datetime.now(timezone.utc).isoformat(),
    )
    repo.add_chunks([chunk])

    # After chunk -> audit should be healthy
    audit_post = repo.audit_corpus()
    assert audit_post["unchunked_documents_count"] == 0
    assert audit_post["integrity_status"] == "healthy"

    # Stats check
    stats = repo.get_knowledge_stats()
    assert stats["total_documents"] == 1
    assert stats["total_chunks"] == 1
    assert stats["categories_breakdown"].get("transport") == 1
    assert "london_uk" in stats["cities_covered"]

    # Sources list check
    sources = repo.list_sources()
    assert len(sources) == 1
    assert sources[0]["source"] == "Transport for London"


# ==============================================================================
# 8. SAFE URL INGESTION TESTS (MOCKED)
# ==============================================================================


def test_fetch_url_content_rejections() -> None:
    async def _test():
        with pytest.raises(ValueError, match="Unsafe or unsupported URL scheme"):
            await fetch_url_content("file:///etc/passwd")

        with pytest.raises(ValueError, match="Unsafe or unsupported URL scheme"):
            await fetch_url_content("ftp://example.com/doc.txt")

    asyncio.run(_test())


# ==============================================================================
# 9. API ENDPOINTS INTEGRATION TESTS
# ==============================================================================


def test_api_knowledge_routes(client) -> None:
    # 1. Ingest via API
    payload = {
        "title": "Paris Metro Navigo System",
        "content": "The Navigo pass offers unlimited transit access across Île-de-France zones.",
        "source": "RATP Official",
        "authority_tier": "tier_1_official",
        "scope": "city",
        "city_id": "paris_fr",
        "country_id": "france",
        "category": "transport",
        "subcategory": "public_transport",
    }
    post_res = client.post("/api/v1/knowledge/documents", json=payload)
    assert post_res.status_code == 200
    doc_data = post_res.json()["data"]
    doc_id = doc_data["document_id"]
    assert doc_data["authority_tier"] == "tier_1_official"
    assert doc_data["scope"] == "city"

    # 2. Get stats endpoint
    stats_res = client.get("/api/v1/knowledge/stats")
    assert stats_res.status_code == 200
    stats_data = stats_res.json()["data"]
    assert "total_documents" in stats_data
    assert "categories_breakdown" in stats_data

    # 3. Get sources endpoint
    sources_res = client.get("/api/v1/knowledge/sources")
    assert sources_res.status_code == 200
    sources_list = sources_res.json()["data"]
    assert any(s["source"] == "RATP Official" for s in sources_list)

    # 4. Get audit endpoint
    audit_res = client.get("/api/v1/knowledge/audit")
    assert audit_res.status_code == 200
    audit_data = audit_res.json()["data"]
    assert "integrity_status" in audit_data

    # 5. Search endpoint with composite scoring
    search_res = client.get(
        "/api/v1/knowledge/search",
        params={"query": "Navigo pass transit metro", "city_id": "paris_fr"},
    )
    assert search_res.status_code == 200
    s_data = search_res.json()["data"]
    assert s_data["total_found"] >= 1
    evidence = s_data["evidence"][0]
    assert evidence["source"] == "RATP Official"
    assert "score_breakdown" in evidence
    assert evidence["score_breakdown"]["scope"] == 1.0

