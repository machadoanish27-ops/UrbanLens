import argparse
import csv
import json
import math
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = PROJECT_ROOT / "data"
DATASETS = {
    "cities": "canonical/cities.csv",
    "city_aliases": "mappings/city_aliases.csv",
    "city_provider_identities": "mappings/city_provider_identities.csv",
    "countries": "canonical/countries.csv",
    "country_metrics": "canonical/country_metrics.csv",
    "gdp_country_metrics": "canonical/gdp_country_metrics.csv",
    "cost_of_living": "canonical/cost_of_living.csv",
    "universities": "canonical/universities.csv",
    "university_rankings": "canonical/university_rankings.csv",
    "weather_observations": "canonical/weather_observations.csv",
    "weather_forecasts_wmo": "canonical/weather_forecasts_wmo.csv",
    "air_quality_observations_global_weather": "canonical/air_quality_observations_global_weather.csv",
    "air_quality_observations_who": "canonical/air_quality_observations_who.csv",
    "source_registry": "canonical/source_registry.csv",
}
NATURAL_KEYS = {
    "cities": ("city_id",),
    "city_aliases": ("city_id", "normalized_alias"),
    "city_provider_identities": ("provider", "provider_location_id"),
    "countries": ("country_id",),
    "country_metrics": ("country_id", "metric", "period"),
    "gdp_country_metrics": ("country_id", "metric", "period"),
    "universities": ("university_id",),
    "university_rankings": ("university_id", "ranking_metric", "ranking_year", "source_record_key"),
    "weather_observations": ("city_id", "provider", "observed_at", "source_row"),
    "weather_forecasts_wmo": ("city_id", "provider", "forecast_for"),
    "air_quality_observations_global_weather": ("city_id", "provider", "observed_at", "source_row"),
    "air_quality_observations_who": ("city_id", "source", "year", "source_row"),
    "source_registry": ("source_id",),
}
PROVENANCE_FIELDS = {
    "cities": ("source_id",),
    "country_metrics": ("source_id",),
    "gdp_country_metrics": ("source_id",),
    "cost_of_living": ("source_id",),
    "universities": ("source_id",),
    "university_rankings": ("source_id",),
    "weather_observations": ("provider", "source_row"),
    "weather_forecasts_wmo": ("provider", "fetched_at"),
    "air_quality_observations_global_weather": ("provider", "source_row"),
    "air_quality_observations_who": ("source", "source_row"),
    "source_registry": ("source_file",),
}
NULL_MARKERS = {"", "null", "none", "nan", "na", "n/a", "not provided", "not available"}
PERCENT_FIELDS = {"humidity_pct", "pm25_temporal_coverage", "pm10_temporal_coverage"}


def semantic_null(value: Any) -> bool:
    return value is None or str(value).strip().lower() in NULL_MARKERS


def valid_coordinate(latitude: Any, longitude: Any) -> bool:
    try:
        lat = float(latitude)
        lon = float(longitude)
    except (TypeError, ValueError):
        return False
    return math.isfinite(lat) and math.isfinite(lon) and -90 <= lat <= 90 and -180 <= lon <= 180


def valid_percentage(value: Any) -> bool:
    if semantic_null(value):
        return True
    text = str(value).strip().replace("%", "").replace(" ", "")
    if not re.fullmatch(r"(?:[<>]=?)?\d+(?:\.\d+)?(?:-(?:[<>]=?)?\d+(?:\.\d+)?)?", text):
        return False
    numbers = re.findall(r"\d+(?:\.\d+)?", text)
    return all(math.isfinite(float(number)) and 0 <= float(number) <= 100 for number in numbers)


def _read_rows(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if not reader.fieldnames:
            raise ValueError(f"Missing CSV header: {path}")
        yield from reader


def validate_data(data_root: Path = DATA_ROOT) -> dict[str, Any]:
    issues: list[dict[str, str]] = []
    dataset_counts: dict[str, int] = {}
    identifiers: dict[str, set[str]] = {name: set() for name in ("cities", "countries", "universities", "source_registry")}
    duplicate_keys: dict[str, int] = defaultdict(int)
    semantic_null_counts: dict[str, int] = defaultdict(int)
    provider_city_assignments: dict[tuple[str, str], set[str]] = defaultdict(set)

    for name, relative_path in DATASETS.items():
        path = data_root / relative_path
        if not path.is_file():
            issues.append({"severity": "error", "dataset": name, "check": "file_exists", "detail": str(path)})
            dataset_counts[name] = 0
            continue
        seen_keys: set[tuple[str, ...]] = set()
        count = 0
        for row_number, row in enumerate(_read_rows(path), start=2):
            count += 1
            key_fields = NATURAL_KEYS.get(name)
            if key_fields:
                key_values = tuple((row.get(field) or "").strip() for field in key_fields)
                if any(semantic_null(value) for value in key_values):
                    issues.append({"severity": "error", "dataset": name, "check": "missing_natural_key", "detail": f"row {row_number}: {key_fields}"})
                elif key_values in seen_keys:
                    duplicate_keys[name] += 1
                    issues.append({"severity": "error", "dataset": name, "check": "duplicate_natural_key", "detail": f"row {row_number}: {key_values}"})
                else:
                    seen_keys.add(key_values)

            for field, value in row.items():
                if semantic_null(value):
                    semantic_null_counts[f"{name}.{field}"] += 1

            required_provenance = PROVENANCE_FIELDS.get(name, ())
            missing_provenance = [field for field in required_provenance if semantic_null(row.get(field))]
            if missing_provenance:
                issues.append({"severity": "warning", "dataset": name, "check": "provenance", "detail": f"row {row_number}: {missing_provenance}"})

            if name == "cities":
                city_id = (row.get("city_id") or "").strip()
                if city_id:
                    identifiers["cities"].add(city_id)
                if not valid_coordinate(row.get("latitude"), row.get("longitude")):
                    issues.append({"severity": "error", "dataset": name, "check": "coordinates", "detail": f"row {row_number}"})
            elif name == "city_provider_identities":
                latitude = row.get("latitude")
                longitude = row.get("longitude")
                if not semantic_null(latitude) or not semantic_null(longitude):
                    if not valid_coordinate(latitude, longitude):
                        issues.append({"severity": "error", "dataset": name, "check": "coordinates", "detail": f"row {row_number}"})
            elif name == "countries" and row.get("country_id"):
                identifiers["countries"].add(row["country_id"].strip())
            elif name == "universities" and row.get("university_id"):
                identifiers["universities"].add(row["university_id"].strip())
            elif name == "source_registry" and row.get("source_id"):
                identifiers["source_registry"].add(row["source_id"].strip())

            for field in PERCENT_FIELDS.intersection(row):
                if not valid_percentage(row.get(field)):
                    issues.append({"severity": "error", "dataset": name, "check": "invalid_range", "detail": f"row {row_number}: {field}={row.get(field)}"})

            if name == "city_provider_identities":
                provider_city_assignments[(row.get("provider", ""), row.get("provider_location_id", ""))].add(row.get("city_id", ""))
        dataset_counts[name] = count

    known_ids = identifiers
    for name, relative_path in DATASETS.items():
        path = data_root / relative_path
        if not path.is_file():
            continue
        for row_number, row in enumerate(_read_rows(path), start=2):
            city_id = row.get("city_id")
            if not semantic_null(city_id) and name != "cities" and city_id not in known_ids["cities"]:
                issues.append({"severity": "error", "dataset": name, "check": "orphan_city_id", "detail": f"row {row_number}: {city_id}"})
            country_id = row.get("country_id")
            if not semantic_null(country_id) and country_id not in known_ids["countries"]:
                issues.append({"severity": "error", "dataset": name, "check": "orphan_country_id", "detail": f"row {row_number}: {country_id}"})
            university_id = row.get("university_id")
            if not semantic_null(university_id) and name != "universities" and university_id not in known_ids["universities"]:
                issues.append({"severity": "error", "dataset": name, "check": "orphan_university_id", "detail": f"row {row_number}: {university_id}"})
            source_id = row.get("source_id")
            if not semantic_null(source_id) and name != "source_registry" and source_id not in known_ids["source_registry"]:
                issues.append({"severity": "warning", "dataset": name, "check": "unregistered_source", "detail": f"row {row_number}: {source_id}"})

    for provider_key, city_ids in provider_city_assignments.items():
        if len(city_ids) > 1:
            issues.append({"severity": "error", "dataset": "city_provider_identities", "check": "provider_conflict", "detail": f"{provider_key}: {sorted(city_ids)}"})

    return {
        "data_root": str(data_root),
        "dataset_counts": dataset_counts,
        "duplicate_natural_keys": dict(duplicate_keys),
        "semantic_null_counts": dict(semantic_null_counts),
        "issue_count": len(issues),
        "issues": issues,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate UrbanLens CSV data without modifying it.")
    parser.add_argument("--data-root", type=Path, default=DATA_ROOT)
    parser.add_argument("--output", type=Path, help="Optional JSON report destination.")
    parser.add_argument("--strict", action="store_true", help="Exit nonzero when errors or warnings are found.")
    parser.add_argument("--verbose", action="store_true", help="Print every finding as JSON.")
    args = parser.parse_args(argv)
    try:
        report = validate_data(args.data_root)
    except (OSError, ValueError, csv.Error) as error:
        print(f"Validation could not complete: {error}", file=sys.stderr)
        return 2
    rendered = json.dumps(report, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    if args.verbose:
        print(rendered)
    else:
        print(f"Datasets checked: {len(report['dataset_counts'])}")
        for name, count in report["dataset_counts"].items():
            print(f"  {name}: {count} rows")
        grouped_issues: dict[tuple[str, str, str], int] = defaultdict(int)
        for issue in report["issues"]:
            key = (issue["severity"], issue["dataset"], issue["check"])
            grouped_issues[key] += 1
        print(f"Findings: {report['issue_count']}")
        for (severity, dataset, check), count in sorted(grouped_issues.items()):
            print(f"  {severity}: {dataset}.{check}: {count}")
        for issue in report["issues"][:10]:
            print(f"  sample: {issue['dataset']}.{issue['check']}: {issue['detail']}")
    has_findings = any(issue["severity"] in {"error", "warning"} for issue in report["issues"])
    return 1 if args.strict and has_findings else 0


if __name__ == "__main__":
    raise SystemExit(main())