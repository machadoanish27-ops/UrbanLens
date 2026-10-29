"""Audit and reporting utility for UrbanLens RAG Knowledge Layer."""

import argparse
import json
import sys
from typing import Any

from app.db.client import MongoClientManager
from app.db.repositories.knowledge import KnowledgeRepository
from app.services.knowledge import KnowledgeService


def run_audit(verbose: bool = False) -> int:
    """Run full knowledge base audit and print formatted report."""
    print("=" * 70)
    print("URBANLENS KNOWLEDGE LAYER AUDIT REPORT")
    print("=" * 70)

    try:
        db = MongoClientManager.get_database()
        repo = KnowledgeRepository(db)
        service = KnowledgeService(repo)
    except Exception as exc:
        print(f"[ERROR] Failed to connect to database: {exc}", file=sys.stderr)
        return 1

    stats = service.get_stats()
    audit = service.audit_corpus()
    sources = service.list_sources()

    print(f"\n1. CORPUS SUMMARY:")
    print(f"   Total Documents:        {stats['total_documents']}")
    print(f"   Total Chunks:           {stats['total_chunks']}")
    print(f"   Distinct Sources:       {len(sources)}")
    print(f"   Countries Covered ({len(stats['countries_covered'])}):  {', '.join(stats['countries_covered']) or 'None'}")
    print(f"   Cities Covered ({len(stats['cities_covered'])}):     {', '.join(stats['cities_covered']) or 'None'}")

    print(f"\n2. CATEGORY BREAKDOWN:")
    for cat, count in sorted(stats["categories_breakdown"].items(), key=lambda x: x[1], reverse=True):
        print(f"   - {cat:<24} : {count} documents")

    print(f"\n3. SCOPE BREAKDOWN:")
    for scope, count in sorted(stats["scope_breakdown"].items(), key=lambda x: x[1], reverse=True):
        print(f"   - {scope:<24} : {count} documents")

    print(f"\n4. AUTHORITY TIER BREAKDOWN:")
    for tier, count in sorted(stats["tier_breakdown"].items(), key=lambda x: x[1], reverse=True):
        print(f"   - {tier:<24} : {count} documents")

    print(f"\n5. FRESHNESS EVALUATION:")
    for f_stat, count in stats["freshness_summary"].items():
        print(f"   - {f_stat:<24} : {count} documents")

    print(f"\n6. INTEGRITY STATUS: [{audit['integrity_status'].upper()}]")
    print(f"   Unchunked Documents:    {audit['unchunked_documents_count']}")
    if audit["unchunked_documents_count"] > 0:
        print(f"     IDs: {audit['unchunked_document_ids']}")
    print(f"   Stale Documents:        {audit['stale_documents_count']}")
    print(f"   Duplicate Checksums:    {len(audit['duplicate_checksum_groups'])}")
    if audit["duplicate_checksum_groups"]:
        print(f"     Groups: {audit['duplicate_checksum_groups']}")

    if verbose and sources:
        print(f"\n7. REGISTERED SOURCES DETAIL:")
        for s in sources:
            print(f"   - {s['source']} ({s.get('publisher') or 'No publisher'})")
            print(f"     Tier: {s['authority_tier']} | Docs: {s['document_count']} | Categories: {', '.join(s['categories'])}")
            if s.get("source_url"):
                print(f"     URL: {s['source_url']}")

    print("\n" + "=" * 70)
    if audit["integrity_status"] == "healthy":
        print("[SUCCESS] Knowledge base is healthy and consistent.")
        return 0
    else:
        print("[WARNING] Integrity issues detected.")
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Audit UrbanLens Knowledge Base")
    parser.add_argument("--verbose", "-v", action="store_true", help="Print detailed sources catalog")
    args = parser.parse_args()
    sys.exit(run_audit(verbose=args.verbose))

