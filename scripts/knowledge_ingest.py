"""CLI ingestion tool for the UrbanLens RAG Knowledge Layer."""

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any

from app.db.client import MongoClientManager
from app.db.repositories.knowledge import KnowledgeRepository
from app.models.taxonomy import (
    AuthorityTier,
    FreshnessPolicy,
    KnowledgeCategory,
    KnowledgeScope,
    normalize_category,
)
from app.providers.embedding.factory import get_embedding_provider
from app.services.chunking import chunk_text
from app.services.knowledge_ingestion import KnowledgeIngestionService, normalize_content


async def process_file(
    filepath: Path,
    ingestion_service: KnowledgeIngestionService | None,
    dry_run: bool = False,
    reindex: bool = False,
    override_country: str | None = None,
    override_city: str | None = None,
) -> int:
    """Process a single JSON document file or array of documents."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as exc:
        print(f"[ERROR] Failed to read {filepath}: {exc}", file=sys.stderr)
        return 0

    items = data if isinstance(data, list) else [data]
    ingested_count = 0

    for idx, item in enumerate(items, 1):
        title = item.get("title")
        content = item.get("content")
        source = item.get("source")

        if not title or not content or not source:
            print(f"[SKIP] Item {idx} in {filepath.name} missing title/content/source")
            continue

        category = normalize_category(item.get("category", KnowledgeCategory.CITY_INFORMATION.value))
        subcategory = item.get("subcategory")
        scope = item.get("scope", KnowledgeScope.COUNTRY.value)
        authority_tier = item.get("authority_tier", AuthorityTier.TIER_1_OFFICIAL.value)
        authority_score = item.get("authority_score")
        country_id = override_country or item.get("country_id")
        city_id = override_city or item.get("city_id")
        source_url = item.get("source_url")
        publisher = item.get("publisher")
        freshness_policy = item.get("freshness_policy", FreshnessPolicy.MODERATE_180D.value)

        if dry_run:
            clean = normalize_content(content)
            chunks = chunk_text(clean, chunk_size=600, overlap=100)
            print(f"[DRY-RUN] Ingest '{title}' ({source}) -> Cat: {category}/{subcategory} | Scope: {scope} | Tier: {authority_tier} | Chunks: {len(chunks)}")
            ingested_count += 1
        else:
            assert ingestion_service is not None
            doc, chunk_count = await ingestion_service.ingest_document(
                title=title,
                content=content,
                source=source,
                source_url=source_url,
                publisher=publisher,
                authority_tier=authority_tier,
                authority_score=authority_score,
                scope=scope,
                country_id=country_id,
                city_id=city_id,
                category=category,
                subcategory=subcategory,
                freshness_policy=freshness_policy,
                reindex=reindex,
            )
            print(f"[INGESTED] {doc.document_id}: '{doc.title}' ({chunk_count} chunks)")
            ingested_count += 1

    return ingested_count


async def run_ingestion(args: argparse.Namespace) -> int:
    """Run CLI ingestion workflow."""
    dry_run = args.dry_run
    reindex = args.reindex

    ingestion_service = None
    if not dry_run:
        db = MongoClientManager.get_database()
        repo = KnowledgeRepository(db)
        embedder = get_embedding_provider()
        ingestion_service = KnowledgeIngestionService(repo, embedding_provider=embedder)

    total_ingested = 0

    if args.url:
        print(f"Fetching from URL: {args.url}")
        if dry_run:
            from app.services.knowledge_ingestion import fetch_url_content
            text, title = await fetch_url_content(args.url)
            chunks = chunk_text(text, chunk_size=600, overlap=100)
            print(f"[DRY-RUN] URL content fetched ({len(text)} chars) -> Title: '{title}' -> {len(chunks)} chunks")
            total_ingested += 1
        else:
            assert ingestion_service is not None
            doc, chunk_count = await ingestion_service.ingest_from_url(
                url=args.url,
                title=args.title,
                source=args.source or "Official Web Resource",
                publisher=args.publisher,
                authority_tier=args.tier or AuthorityTier.TIER_1_OFFICIAL.value,
                scope=args.scope or KnowledgeScope.COUNTRY.value,
                country_id=args.country,
                city_id=args.city,
                category=args.category or KnowledgeCategory.CITY_INFORMATION.value,
                subcategory=args.subcategory,
                reindex=reindex,
            )
            print(f"[INGESTED URL] {doc.document_id}: '{doc.title}' ({chunk_count} chunks)")
            total_ingested += 1

    elif args.file:
        filepath = Path(args.file)
        if not filepath.exists():
            print(f"[ERROR] File not found: {filepath}", file=sys.stderr)
            return 1
        total_ingested += await process_file(
            filepath,
            ingestion_service,
            dry_run=dry_run,
            reindex=reindex,
            override_country=args.country,
            override_city=args.city,
        )

    elif args.dir:
        dirpath = Path(args.dir)
        if not dirpath.exists():
            print(f"[ERROR] Directory not found: {dirpath}", file=sys.stderr)
            return 1

        json_files = sorted(dirpath.glob("**/*.json"))
        print(f"Scanning directory {dirpath}: found {len(json_files)} JSON config files")
        for f in json_files:
            count = await process_file(
                f,
                ingestion_service,
                dry_run=dry_run,
                reindex=reindex,
                override_country=args.country,
                override_city=args.city,
            )
            total_ingested += count
    else:
        # Default to app/data/curated_sources
        default_dir = Path("app/data/curated_sources")
        if default_dir.exists():
            json_files = sorted(default_dir.glob("**/*.json"))
            print(f"Scanning default directory {default_dir}: found {len(json_files)} JSON config files")
            for f in json_files:
                count = await process_file(
                    f,
                    ingestion_service,
                    dry_run=dry_run,
                    reindex=reindex,
                    override_country=args.country,
                    override_city=args.city,
                )
                total_ingested += count
        else:
            print("No source specified. Provide --file, --dir, or --url.", file=sys.stderr)
            return 1

    mode_str = "[DRY-RUN COMPLETED]" if dry_run else "[INGESTION COMPLETED]"
    print(f"\n{mode_str} Successfully processed {total_ingested} documents.")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="UrbanLens Knowledge Layer Ingestion CLI")
    parser.add_argument("--file", help="Path to JSON file containing document(s)")
    parser.add_argument("--dir", help="Path to directory containing JSON document files")
    parser.add_argument("--url", help="Authoritative URL to fetch and ingest")
    parser.add_argument("--title", help="Explicit title for URL or file ingestion")
    parser.add_argument("--source", help="Source publication/agency name")
    parser.add_argument("--publisher", help="Publishing organization")
    parser.add_argument("--category", help="Knowledge category")
    parser.add_argument("--subcategory", help="Knowledge subcategory")
    parser.add_argument("--tier", default=AuthorityTier.TIER_1_OFFICIAL.value, help="Authority tier")
    parser.add_argument("--scope", default=KnowledgeScope.COUNTRY.value, help="Applicability scope")
    parser.add_argument("--country", help="Canonical country identifier")
    parser.add_argument("--city", help="Canonical city identifier")
    parser.add_argument("--dry-run", action="store_true", help="Parse and validate without saving to MongoDB")
    parser.add_argument("--reindex", action="store_true", help="Re-chunk and re-embed existing documents")

    args = parser.parse_args()
    sys.exit(asyncio.run(run_ingestion(args)))


if __name__ == "__main__":
    main()

