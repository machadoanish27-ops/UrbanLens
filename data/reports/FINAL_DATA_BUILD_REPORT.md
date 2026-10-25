# UrbanLens Final Data Package V1

One-shot consolidated static ETL build using frozen CITY_ID_MAPPING_V3.

- Source datasets were not modified.
- Canonical city_id remains `city_<worldcities.id>`.
- External API/provider IDs are separate.
- Semantic unavailable values are null; legitimate negatives are preserved.
- Unmatched records are quarantined rather than fabricated.

See `FINAL_MANIFEST.json`, `FINAL_VALIDATION_REPORT.csv`, and `MONGODB_INDEXES_V1.json`.
