# Data and MongoDB Operations

## Authoritative Data

The operator-designated corrected V2_FIXED data layer is stored in this project. Canonical CSV values were not altered during consolidation. Both previous data trees were checksum-compared; their same-named data artifacts were byte-identical. The supplied `FINAL_MANIFEST.json` records the source build as V1; that historical metadata is retained without being rewritten.

`data/canonical/` contains cities, countries, country metrics, GDP, cost of living, universities/rankings, weather, air quality, and the source registry. `data/mappings/` contains aliases and provider identities. Quarantines and reports remain separate.

Canonical identity is `city_id`. Provider identities use `(provider, provider_location_id)` and never substitute a provider ID for `city_id`.

## Import Scope and Keys

The maintained loader is `etl/mongodb_import.py`, exposed by the root `import_mongodb.py`. Its default allow-list contains only:

- `city_aliases`
- `city_provider_identities`
- `weather_observations`
- `weather_forecasts_wmo`
- `air_quality_observations_global_weather`
- `air_quality_observations_who`
- `source_registry`

Previously verified city/country/metrics/cost/university collections are excluded. The alias key is `(city_id, normalized_alias)`; provider identity is `(provider, provider_location_id)`; weather observation key is `(city_id, provider, observed_at, source_row)`. Missing natural-key fields are skipped and counted, never synthesized. Weather writes use `$setOnInsert`; a matching existing observation is not overwritten. Other pending collections use batched upserts on their configured keys.

The loader validates duplicate keys before connecting, reports CSV and database counts, reports progress, and saves atomic per-collection checkpoints under ignored `logs/`. Re-running or resuming is idempotent. No collection-drop option exists.

The current CSV audit found 13,104 alias rows with a blank `normalized_alias`; these remain in the source and are not importable by that key. The loader reports and skips them. Cost-of-living has no confirmed natural key in the supplied evidence, so validation does not invent one. WHO temporal-coverage values include percentage strings such as `75%`; these are validated as percentages. Missing provenance, out-of-range values, and orphan references are reported, not silently rewritten.

## MongoDB Code

`mongo_init.js` prepares unique and supporting indexes and does not drop collections or alter documents. `scripts/validate_mongodb.py` performs count and duplicate-key reads only. Both require a manually selected target database. Neither was run during this task.

The loader and MongoDB audit require `MONGODB_URI` and `MONGODB_DB`. No URI is hardcoded. Keep real values in ignored `.env`; `.env.example` contains placeholders only. No Atlas connection, import, collection write, or collection drop was performed.

## Existing State Supplied by the Operator

The known verified counts and partial weather-import baseline are captured in [project status](PROJECT_STATUS.md). They are documented as operator-provided and were not checked against a live database here.
