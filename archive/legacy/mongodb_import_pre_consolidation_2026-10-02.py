import argparse
import csv
import hashlib
import json
import os
import re
import sys
import tempfile
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from app.db.settings import MongoSettings


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = PROJECT_ROOT / "data"
DEFAULT_STATE_FILE = PROJECT_ROOT / "logs" / "etl_state.json"

DATA_FILES = {
    "city_aliases": "mappings/city_aliases.csv",
    "city_provider_identities": "mappings/city_provider_identities.csv",
    "weather_observations": "canonical/weather_observations.csv",
    "weather_forecasts_wmo": "canonical/weather_forecasts_wmo.csv",
    "air_quality_observations_global_weather": "canonical/air_quality_observations_global_weather.csv",
    "air_quality_observations_who": "canonical/air_quality_observations_who.csv",
    "source_registry": "canonical/source_registry.csv",
}

NATURAL_KEYS = {
    "city_aliases": ("city_id", "normalized_alias"),
    "city_provider_identities": ("provider", "provider_location_id"),
    "weather_observations": ("city_id", "provider", "observed_at", "source_row"),
    "weather_forecasts_wmo": ("city_id", "provider", "forecast_for"),
    "air_quality_observations_global_weather": ("city_id", "provider", "observed_at", "source_row"),
    "air_quality_observations_who": ("city_id", "source", "year", "source_row"),
    "source_registry": ("source_id",),
}

INSERT_ONLY_COLLECTIONS = frozenset({"weather_observations"})
NULL_MARKERS = frozenset({"", "null", "none", "nan", "na", "n/a", "not provided", "not available"})
INTEGER_FIELDS = frozenset({"worldcities_id", "geonames_id", "period", "year", "ranking_year", "rank", "source_row", "bytes"})
BOOLEAN_FIELDS = frozenset({"population_unavailable", "review_required", "rank_unavailable", "score_unavailable"})
DATE_FIELDS = frozenset({"observed_at", "fetched_at", "forecast_for", "forecast_fetched_at", "timestamp", "first_seen_at", "last_verified_at", "ingested_at", "retrieved_at", "expires_at"})


def natural_key(collection: str, row: dict[str, Any]) -> tuple[str, ...] | None:
    fields = NATURAL_KEYS.get(collection)
    if fields is None:
        return None
    values = tuple(str(row.get(field, "")).strip() for field in fields)
    if any(not value or value.lower() in NULL_MARKERS for value in values):
        return None
    return values


def scalar(value: Any, field: str) -> Any:
    if value is None:
        return None
    text = str(value).strip()
    if text.lower() in NULL_MARKERS:
        return None
    if field in BOOLEAN_FIELDS:
        if text.lower() in {"true", "1", "yes"}:
            return True
        if text.lower() in {"false", "0", "no"}:
            return False
    if field in INTEGER_FIELDS:
        try:
            return int(float(text))
        except ValueError:
            return text
    if field in DATE_FIELDS:
        try:
            return datetime.fromisoformat(text.replace("Z", "+00:00"))
        except ValueError:
            return text
    if re.fullmatch(r"-?\d+", text):
        if field.endswith("_id"):
            return text
        try:
            return int(text)
        except ValueError:
            return text
    if re.fullmatch(r"-?(?:\d+\.\d*|\.\d+)(?:[eE][+-]?\d+)?|-?\d+(?:[eE][+-]?\d+)", text):
        try:
            return float(text)
        except ValueError:
            return text
    return text


def to_document(row: dict[str, Any]) -> dict[str, Any]:
    return {field: scalar(value, field) for field, value in row.items()}


def csv_row_count(path: Path) -> int:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        return sum(1 for _ in csv.DictReader(stream))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


@dataclass(frozen=True)
class CsvPreflight:
    total_rows: int
    importable_rows: int
    skipped_missing_key: int


def validate_csv(collection: str, path: Path) -> CsvPreflight:
    seen: set[tuple[str, ...]] = set()
    total_rows = 0
    skipped_missing_key = 0
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if not reader.fieldnames:
            raise ValueError(f"{path}: missing CSV header")
        for row_number, row in enumerate(reader, start=2):
            total_rows += 1
            key = natural_key(collection, row)
            if key is None:
                skipped_missing_key += 1
                continue
            if key in seen:
                raise ValueError(f"{path}:{row_number}: duplicate natural key {key}")
            seen.add(key)
    return CsvPreflight(total_rows, len(seen), skipped_missing_key)


def index_specs() -> dict[str, list[tuple[list[tuple[str, int]], dict[str, bool]]]]:
    def unique_options(fields: tuple[str, ...]) -> dict[str, Any]:
        partial_filter = {}
        for field in fields:
            if field in INTEGER_FIELDS:
                partial_filter[field] = {"$type": "number"}
            elif field in DATE_FIELDS:
                partial_filter[field] = {"$type": "date"}
            else:
                partial_filter[field] = {"$type": "string", "$gt": ""}
        return {"unique": True, "partialFilterExpression": partial_filter}

    return {
        "city_aliases": [([("city_id", 1), ("normalized_alias", 1)], unique_options(("city_id", "normalized_alias")))],
        "city_provider_identities": [([("provider", 1), ("provider_location_id", 1)], unique_options(("provider", "provider_location_id")))],
        "weather_observations": [([("city_id", 1), ("provider", 1), ("observed_at", 1), ("source_row", 1)], unique_options(("city_id", "provider", "observed_at", "source_row")))],
        "weather_forecasts_wmo": [([("city_id", 1), ("provider", 1), ("forecast_for", 1)], unique_options(("city_id", "provider", "forecast_for")))],
        "air_quality_observations_global_weather": [([("city_id", 1), ("provider", 1), ("observed_at", 1), ("source_row", 1)], unique_options(("city_id", "provider", "observed_at", "source_row")))],
        "air_quality_observations_who": [([("city_id", 1), ("source", 1), ("year", 1), ("source_row", 1)], unique_options(("city_id", "source", "year", "source_row")))],
        "source_registry": [([("source_id", 1)], unique_options(("source_id",)))],
    }


def load_state(path: Path) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as stream:
        value = json.load(stream)
    return value if isinstance(value, dict) else {}


def save_state(path: Path, state: dict[str, dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_name = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as stream:
            temporary_name = stream.name
            json.dump(state, stream, indent=2, sort_keys=True)
            stream.write("\n")
            os.replace(temporary_name, path)
    finally:
        if temporary_name and os.path.exists(temporary_name):
            os.unlink(temporary_name)


def import_collection(
    db: Any,
    collection_name: str,
    path: Path,
    expected_rows: int,
    state: dict[str, dict[str, Any]],
    state_path: Path,
    batch_size: int,
    progress_every: int,
    resume: bool,
) -> tuple[int, int, int]:
    from pymongo import UpdateOne

    collection = db[collection_name]
    before = collection.count_documents({})
    file_hash = sha256_file(path)
    checkpoint = state.get(collection_name, {}) if resume else {}
    start_after = int(checkpoint.get("processed_rows", 0)) if checkpoint.get("sha256") == file_hash else 0
    start_after = min(start_after, expected_rows)
    operations = []
    operation_rows = 0
    processed = start_after
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        for row_number, row in enumerate(csv.DictReader(stream), start=1):
            if row_number <= start_after:
                continue
            processed = row_number
            if natural_key(collection_name, row) is None:
                continue
            document = to_document(row)
            key_fields = NATURAL_KEYS[collection_name]
            key = {field: document[field] for field in key_fields}
            update = {"$setOnInsert": document} if collection_name in INSERT_ONLY_COLLECTIONS else {"$set": document}
            operations.append(UpdateOne(key, update, upsert=True))
            operation_rows += 1
            if len(operations) >= batch_size:
                collection.bulk_write(operations, ordered=False)
                operations.clear()
                state[collection_name] = {"sha256": file_hash, "processed_rows": processed}
                save_state(state_path, state)
            if progress_every and processed and processed % progress_every == 0:
                print(f"[PROGRESS] {collection_name}: {processed}/{expected_rows} CSV rows")
    if operations:
        collection.bulk_write(operations, ordered=False)
    if processed < expected_rows:
        processed = expected_rows
    state[collection_name] = {"sha256": file_hash, "processed_rows": processed}
    save_state(state_path, state)
    after = collection.count_documents({})
    return before, after, operation_rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Resumable, non-destructive UrbanLens MongoDB ETL")
    parser.add_argument("--collections", nargs="+", choices=tuple(DATA_FILES), default=None)
    parser.add_argument("--batch-size", type=int, default=1000)
    parser.add_argument("--progress-every", type=int, default=5000)
    parser.add_argument("--state-file", type=Path, default=DEFAULT_STATE_FILE)
    parser.add_argument("--no-resume", action="store_true", help="Rescan all CSV rows; upserts remain idempotent.")
    parser.add_argument("--check-only", action="store_true", help="Validate selected CSVs without connecting to MongoDB.")
    args = parser.parse_args(argv)
    if args.batch_size < 1 or args.progress_every < 0:
        parser.error("batch size must be positive and progress interval cannot be negative")

    selected = args.collections or list(DATA_FILES)
    inputs: dict[str, tuple[Path, CsvPreflight]] = {}
    try:
        for name in selected:
            path = DATA_ROOT / DATA_FILES[name]
            if not path.is_file():
                raise FileNotFoundError(f"Missing dataset: {path}")
            inputs[name] = (path, validate_csv(name, path))
    except (OSError, ValueError) as error:
        print(f"[INVALID] {error}", file=sys.stderr)
        return 2

    for name, (path, stats) in inputs.items():
        print(
            f"[VALID] {name}: csv_rows={stats.total_rows}, importable={stats.importable_rows}, "
            f"skipped_missing_natural_key={stats.skipped_missing_key} ({path.relative_to(PROJECT_ROOT)})"
        )
    if args.check_only:
        return 0

    try:
        settings = MongoSettings.from_environment()
    except ValueError as error:
        print(str(error), file=sys.stderr)
        return 2

    try:
        from pymongo import MongoClient
    except ImportError:
        print("Install project dependencies before running an import.", file=sys.stderr)
        return 2

    client = MongoClient(settings.uri)
    try:
        db = client[settings.database]
        for name in selected:
            for keys, options in index_specs()[name]:
                db[name].create_index(keys, **options)
        state = load_state(args.state_file) if not args.no_resume else {}
        for name, (path, stats) in inputs.items():
            started = time.monotonic()
            before, after, written = import_collection(
                db, name, path, stats.total_rows, state, args.state_file,
                args.batch_size, args.progress_every, not args.no_resume,
            )
            print(
                f"[COUNT] {name}: csv_rows={stats.total_rows}, importable={stats.importable_rows}, "
                f"skipped_missing_key={stats.skipped_missing_key}, mongo_before={before}, "
                f"mongo_after={after}, rows_processed={written}, elapsed={time.monotonic() - started:.1f}s"
            )
    finally:
        client.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())