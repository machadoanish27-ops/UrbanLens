#!/usr/bin/env python3
"""
UrbanLens MongoDB loader V1
Requires: Python 3.10+, pymongo
Usage:
  pip install pymongo
  export MONGODB_URI="mongodb://localhost:27017"
  python import_mongodb.py --db urbanlens
"""
import argparse, csv, json, os, re, sys, time
from datetime import datetime, timezone
from pathlib import Path
from pymongo import MongoClient, UpdateOne

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"

COLLECTIONS = {
    "cities": "cities.csv",
    "city_aliases": "city_aliases.csv",
    "city_provider_identities": "city_provider_identities.csv",
    "countries": "countries.csv",
    "country_metrics": "country_metrics.csv",
    "gdp_country_metrics": "gdp_country_metrics.csv",
    "cost_of_living": "cost_of_living.csv",
    "universities": "universities.csv",
    "university_rankings": "university_rankings.csv",
    "weather_observations": "weather_observations.csv",
    "weather_forecasts_wmo": "weather_forecasts_wmo.csv",
    "air_quality_observations_global_weather": "air_quality_observations_global_weather.csv",
    "air_quality_observations_who": "air_quality_observations_who.csv",
    "source_registry": "source_registry.csv",
}

NULLS = {"", "null", "none", "nan", "na", "n/a", "not provided", "not available"}

BOOL_FIELDS = {
    "population_unavailable", "review_required", "rank_unavailable", "score_unavailable"
}

INT_FIELDS = {
    "worldcities_id", "geonames_id", "period", "year", "ranking_year",
    "rank", "source_record_id"
}

DATE_FIELDS = {
    "observed_at", "fetched_at", "forecast_for", "forecast_fetched_at",
    "first_seen_at", "last_verified_at", "ingested_at", "retrieved_at",
    "expires_at"
}

def scalar(v, field):
    if v is None:
        return None
    s = str(v).strip()
    if s.lower() in NULLS:
        return None
    if field in BOOL_FIELDS:
        if s.lower() in {"true","1","yes"}: return True
        if s.lower() in {"false","0","no"}: return False
    if field in INT_FIELDS:
        try: return int(float(s))
        except: return s
    if field in DATE_FIELDS:
        # Leave unparseable values as strings; never fabricate a timestamp.
        try:
            x = s.replace("Z", "+00:00")
            return datetime.fromisoformat(x)
        except:
            return s
    # Numeric-looking values become numbers unless the field is clearly an ID/name/string.
    if re.fullmatch(r"-?\d+", s):
        if field.endswith("_id") and field not in INT_FIELDS:
            return s
        try: return int(s)
        except: pass
    if re.fullmatch(r"-?(?:\d+\.\d*|\.\d+)(?:[eE][+-]?\d+)?", s) or re.fullmatch(r"-?\d+(?:[eE][+-]?\d+)", s):
        try: return float(s)
        except: pass
    return s

def convert(row):
    out = {}
    for k, v in row.items():
        out[k] = scalar(v, k)
    # GeoJSON-friendly coordinates for cities only.
    if "latitude" in out and "longitude" in out and out["latitude"] is not None and out["longitude"] is not None:
        try:
            out["coordinates"] = {
                "type": "Point",
                "coordinates": [float(out["longitude"]), float(out["latitude"])]
            }
        except Exception:
            pass
    return out

def index_specs(db):
    return {
        "cities": [
            ([("city_id",1)], {"unique":True}),
            ([("worldcities_id",1)], {"unique":True}),
            ([("country_iso2",1)], {}),
            ([("coordinates","2dsphere")], {}),
        ],
        "city_aliases": [
            ([("city_id",1)], {}),
            ([("normalized_alias",1)], {}),
            ([("city_id",1),("normalized_alias",1)], {"unique":True}),
        ],
        "city_provider_identities": [
            ([("provider",1),("provider_location_id",1)], {"unique":True}),
            ([("city_id",1)], {}),
        ],
        "countries": [
            ([("country_id",1)], {"unique":True}),
            ([("iso2",1)], {"unique":True}),
            ([("iso3",1)], {"unique":True}),
        ],
        "country_metrics": [
            ([("country_id",1),("metric",1),("period",1)], {}),
        ],
        "gdp_country_metrics": [
            ([("country_id",1),("metric",1),("period",1)], {}),
        ],
        "cost_of_living": [
            ([("city_id",1)], {}),
            ([("city_id",1),("metric",1)], {}),
        ],
        "universities": [
            ([("university_id",1)], {"unique":True}),
            ([("country_iso2",1),("name",1)], {}),
        ],
        "university_rankings": [
            ([("university_id",1)], {}),
            ([("ranking_metric",1),("ranking_year",1)], {}),
        ],
        "weather_observations": [
            ([("city_id",1)], {}),
            ([("city_id",1),("observed_at",-1)], {}),
        ],
        "weather_forecasts_wmo": [
            ([("city_id",1)], {}),
            ([("city_id",1),("forecast_for",1)], {}),
        ],
        "air_quality_observations_global_weather": [
            ([("city_id",1)], {}),
            ([("city_id",1),("observed_at",-1)], {}),
        ],
        "air_quality_observations_who": [
            ([("city_id",1)], {}),
            ([("city_id",1),("year",-1)], {}),
        ],
        "source_registry": [
            ([("source_id",1)], {"unique":True}),
        ],
    }

def load_csv(db, collection, filename, batch_size=2000):
    path = DATA / filename
    if not path.exists():
        print(f"[SKIP] {filename} not found")
        return 0
    coll = db[collection]
    ops = []
    n = 0
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            doc = convert(row)
            # Deterministic natural key where possible; otherwise insert.
            # Use collection-specific natural keys so multi-row collections are not
            # accidentally collapsed to one document per city/country/university.
            if collection == "city_aliases" and doc.get("city_id") and doc.get("normalized_alias"):
                filt = {"city_id": doc["city_id"], "normalized_alias": doc["normalized_alias"]}
            elif collection == "city_provider_identities" and doc.get("provider") and doc.get("provider_location_id"):
                filt = {"provider": doc["provider"], "provider_location_id": doc["provider_location_id"]}
            elif "country_id" in doc and "metric" in doc and "period" in doc:
                filt = {"country_id":doc["country_id"],"metric":doc["metric"],"period":doc["period"]}
            elif "source_id" in doc:
                filt = {"source_id":doc["source_id"]}
            elif "university_id" in doc and doc.get("university_id"):
                filt = {"university_id":doc["university_id"]}
            elif "city_id" in doc and doc.get("city_id") and collection in {"cities"}:
                filt = {"city_id": doc["city_id"]}
            else:
                # For high-volume observations without a stable key, preserve each row.
                coll.insert_one(doc)
                n += 1
                continue
            ops.append(UpdateOne(filt, {"$set":doc}, upsert=True))
            if len(ops) >= batch_size:
                coll.bulk_write(ops, ordered=False)
                n += len(ops); ops = []
    if ops:
        coll.bulk_write(ops, ordered=False)
        n += len(ops)
    return n

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--uri", default=os.getenv("MONGODB_URI"))
    ap.add_argument("--db", default="urbanlens")
    ap.add_argument("--drop", action="store_true", help="Drop target collections before import.")
    ap.add_argument("--only", nargs="*", help="Only load named collections.")
    args = ap.parse_args()
    if not args.uri:
        raise SystemExit("Set MONGODB_URI or pass --uri.")
    client = MongoClient(args.uri)
    db = client[args.db]
    names = list(COLLECTIONS)
    if args.only:
        names = [x for x in names if x in args.only]
    if args.drop:
        for name in names:
            db[name].drop()
    for name in names:
        t0=time.time()
        count=load_csv(db,name,COLLECTIONS[name])
        print(f"[OK] {name}: {count} operations ({time.time()-t0:.1f}s)")
    for name, specs in index_specs(db).items():
        if name not in names: continue
        for keys, opts in specs:
            try:
                db[name].create_index(keys, **opts)
            except Exception as e:
                print(f"[INDEX ERROR] {name} {keys}: {e}")
    print("UrbanLens MongoDB import complete.")

if __name__ == "__main__":
    main()
