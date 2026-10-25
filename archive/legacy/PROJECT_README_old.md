# UrbanLens — Final Project Workspace

This is the single canonical VS Code workspace for UrbanLens.

## Canonical data layer
- `data/` contains the corrected V2-fixed UrbanLens data package.
- `import_mongodb.py` is the corrected MongoDB loader.
- `mongo_init.js` contains MongoDB initialization/index definitions.
- V1 MongoDB loader is not the canonical loader.

## Project structure
- `app/agents/` — seven UrbanLens agent implementations
- `app/api/` — API routes and schemas
- `app/models/` — domain models
- `app/services/` — provider/API and business services
- `app/utils/` — shared utilities
- `etl/` — ETL and normalization pipelines
- `scripts/` — operational/import/validation scripts
- `config/` — non-secret configuration templates
- `tests/` — automated tests
- `docs/` — architecture and data documentation

## Important data rules
- `city_id` is the canonical UrbanLens city identity.
- Provider IDs never replace `city_id`.
- Do not fabricate missing values.
- Preserve legitimate negative values.
- Keep provenance, timestamps, confidence, and source/version metadata.
- Quarantined records stay outside canonical collections until reviewed.

## MongoDB
Use `.env.example` to create a local `.env` containing `MONGODB_URI` and `MONGODB_DB=urbanlens`.
Never commit a real password or connection string.

## Current import state
MongoDB import is still being completed. Do not treat the database as fully loaded until the remaining weather/AQ/source collections and the corrected alias/provider-identity collections have been verified.
