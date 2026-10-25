# UrbanLens MongoDB Ready Package V1

This is the executable import package for the consolidated UrbanLens final data build.

## What is included

`data/` contains the consolidated final data package:
- cities
- city aliases
- provider identities
- countries
- country metrics / GDP
- cost of living
- universities / rankings
- weather
- air quality
- source registry
- validation/quarantine artifacts

## Import

Requirements:
- MongoDB 6/7/8 compatible deployment
- Python 3.10+
- `pip install pymongo`

Set:
```bash
export MONGODB_URI="mongodb://localhost:27017"
```

Then:
```bash
python import_mongodb.py --db urbanlens
```

For a clean rebuild:
```bash
python import_mongodb.py --db urbanlens --drop
```

The loader converts obvious numeric/boolean/null values, preserves legitimate negative values, adds GeoJSON `coordinates` to city documents, and creates the required indexes.

## Important

- `city_id` is the UrbanLens canonical identity.
- External provider IDs never replace `city_id`.
- Historical observations are not overwritten by current API data.
- Unresolved/quarantined records remain outside canonical collections.
- Review `data/FINAL_VALIDATION_REPORT.csv` before production deployment.

## API next layer

Use `city_provider_identities` to map:
`city_id -> provider -> provider_location_id`.

API adapters should write normalized records into the same domain collections and keep provider provenance and fetch timestamps.

## IMPORTANT V2 FIX

The V1 loader incorrectly used `city_id` alone as the upsert key for
`city_aliases` and `city_provider_identities`, which collapsed multiple rows
belonging to the same city. This V2 package fixes the natural keys:
- city_aliases: `(city_id, normalized_alias)`
- city_provider_identities: `(provider, provider_location_id)`

Do not use the V1 loader to rebuild those two collections.
