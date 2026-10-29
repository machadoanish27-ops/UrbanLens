"""MongoDB data consistency and integrity audit script for UrbanLens."""

from app.db.client import MongoClientManager

def run_audit():
    db = MongoClientManager.get_database()
    print("=== URBANLENS MONGODB DATA CONSISTENCY AUDIT ===")

    # 1. Total counts across core collections
    collections = [
        "cities", "countries", "country_metrics", "gdp_country_metrics",
        "universities", "university_rankings", "cost_of_living",
        "weather_observations", "weather_forecasts_wmo",
        "air_quality_observations_global_weather", "air_quality_observations_who",
        "city_aliases", "city_provider_identities", "knowledge_chunks"
    ]
    counts = {}
    print("\n--- Collection Document Counts ---")
    for coll_name in collections:
        c = db[coll_name].count_documents({})
        counts[coll_name] = c
        print(f"  {coll_name}: {c:,} documents")

    # 2. Universities Country ID Casing Check
    print("\n--- Universities Country Identity Audit ---")
    lowercase_univ_countries = db.universities.count_documents({"country_id": {"$regex": "^country_[a-z]{2}$"}})
    uppercase_univ_countries = db.universities.count_documents({"country_id": {"$regex": "^country_[A-Z]{2}$"}})
    total_univ = counts.get("universities", 0)
    print(f"  Total universities: {total_univ:,}")
    print(f"  Uppercase canonical country_id (e.g. country_JP): {uppercase_univ_countries:,}")
    print(f"  Lowercase country_id (e.g. country_jp): {lowercase_univ_countries:,}")
    assert lowercase_univ_countries == 0, "Discrepancy: lowercase country_id values found in universities"

    # Distinct countries in universities
    distinct_univ_countries = db.universities.distinct("country_id")
    print(f"  Distinct countries represented in universities collection: {len(distinct_univ_countries)}")

    # 3. Cost of Living City Identity Mapping Check
    print("\n--- Cost of Living City ID Audit ---")
    cost_city_ids = set(db.cost_of_living.distinct("city_id"))
    canonical_city_ids = set(db.cities.distinct("city_id"))
    orphan_cost_cities = cost_city_ids - canonical_city_ids
    print(f"  Distinct cost of living cities: {len(cost_city_ids)}")
    print(f"  Cost of living cities mapped to canonical cities: {len(cost_city_ids - orphan_cost_cities)} / {len(cost_city_ids)}")
    print(f"  Orphan cost cities: {len(orphan_cost_cities)}")

    # Check for negative cost values
    neg_costs = db.cost_of_living.count_documents({"value": {"$lt": 0}})
    print(f"  Negative/invalid cost sentinel values: {neg_costs}")
    assert neg_costs == 0, "Invalid negative cost metrics found"

    # 4. Countries ID Casing and Duplicate Check
    print("\n--- Countries Collection Audit ---")
    country_ids = db.countries.distinct("country_id")
    print(f"  Distinct country_id count: {len(country_ids)}")
    print(f"  Total country documents: {counts['countries']}")
    assert len(country_ids) == counts["countries"], "Duplicate country_id values detected in countries"

    # 5. Cities Collection Integrity
    print("\n--- Cities Collection Audit ---")
    total_cities = counts["cities"]
    cities_with_id = db.cities.count_documents({"city_id": {"$regex": "^city_"}})
    print(f"  Total canonical cities: {total_cities:,}")
    print(f"  Cities with valid 'city_' prefix: {cities_with_id:,}")
    assert total_cities == cities_with_id, "Inconsistent city_id values found in cities"

    # 6. Provider Metadata and Freshness
    print("\n--- Observations Provenance Audit ---")
    gw_weather_providers = db.weather_observations.distinct("provider")
    print(f"  Weather observations providers: {gw_weather_providers}")
    gw_aq_providers = db.air_quality_observations_global_weather.distinct("provider")
    print(f"  Air Quality GW providers: {gw_aq_providers}")

    print("\n=== DATA INTEGRITY AUDIT COMPLETE: ALL CHECKS VERIFIED ===")

if __name__ == "__main__":
    run_audit()
