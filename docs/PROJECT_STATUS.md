# Project Status

## Implemented foundation

- One project root at the workspace root, with canonical data, mappings, quarantine, reports, docs, tests, application, ETL, and scripts separated.
- Seven-agent capability catalog, shared result/provenance models, injectable orchestration, stale/missing-data status, and basic `/health` and `/agents` API routes.
- Local CSV validation plus prepared resumable MongoDB import, read-only MongoDB validation, and index setup scripts.

## Not implemented/configured

Agent decision logic, external provider integrations, production city/query routes, and Atlas connection remain TODO/configurable. This project does not contain fabricated integrations or API responses.

## MongoDB baseline supplied by the operator

These are the known verified values supplied for planning, not live counts rechecked by this workspace audit:

| Collection | Known count |
| --- | ---: |
| cities | 50,250 |
| countries | 215 |
| country_metrics | 16,000 |
| gdp_country_metrics | 2,925 |
| cost_of_living | 2,172 |
| universities | 9,350 |
| university_rankings | 342 |
| weather_observations | 99,139 verified of 135,406 CSV rows |

Weather observations must be resumed by `(city_id, provider, observed_at, source_row)` with insert-only semantics. Forecast, air-quality, and source-registry collections, plus corrected alias and provider-identity rows, remain pending per the supplied state. No database connection or import was made.

## Data findings from the local CSV audit

- `city_aliases.csv` contains 13,104 rows without `normalized_alias`; the importer counts and skips these rather than fabricating keys.
- Some forecasts have no `fetched_at`; source values remain unchanged and the validator reports provenance gaps.
- WHO coverage values may be formatted with `%`; those are parsed as percentage values for range checks.
- The validator reports unresolved country/university references and other quality findings without modifying canonical files.
- The retained source manifest says V1 even though the supplied corrected data layer is designated authoritative for this project. Its provenance metadata was preserved.