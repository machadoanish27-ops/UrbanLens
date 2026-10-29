"""Deep-dive validation of 8 target cities on live running backend."""

import httpx

client = httpx.Client(base_url="http://127.0.0.1:8000")

targets = [
    ("Tokyo", "city_1392685764"),
    ("Mumbai", "city_1356226629"),
    ("London", "city_1826645935"),
    ("New York", "city_1840034016"),
    ("Paris", "city_1250015082"),
    ("Singapore", "city_1702341327"),
    ("Delhi", "city_1356872604"),
    ("Dubai", "city_1784736618"),
]

print(f"=== DEEP-DIVE CITY AUDIT ({len(targets)} CITIES) ===")
for name, cid in targets:
    # 1. City Details
    c_res = client.get(f"/api/v1/cities/{cid}").json()["data"]
    pop = c_res.get("population")
    density = c_res.get("population_density") or {}
    langs = c_res.get("languages") or {}

    # 2. Universities
    u_res = client.get(f"/api/v1/cities/{cid}/universities").json()
    u_total = u_res["meta"]["pagination"]["total"]

    # 3. Cost of Living
    cost_res = client.get(f"/api/v1/cities/{cid}/cost-of-living").json()["data"]
    cost_status = cost_res.get("status")
    cost_metrics_count = len(cost_res.get("metrics", []))

    # 4. Weather
    w_res = client.get(f"/api/v1/cities/{cid}/weather/live").json()["data"]
    w_current = w_res.get("current") or {}
    w_temp = w_current.get("temperature_c")
    w_meta = w_res.get("meta") or {}
    w_provider = w_meta.get("provider")

    print(f"\n{name} ({cid}):")
    print(f"  - Population: {pop:,} | Density: {density.get('status')} (Val: {density.get('value')}, NatBenchmark: {density.get('national_density_value')} {density.get('unit')})")
    print(f"  - Official Langs: {langs.get('official_languages')} | Spoken: {langs.get('spoken_languages')[:3]} (Status: {langs.get('status')})")
    print(f"  - Universities: {u_total} recorded")
    print(f"  - Cost: {cost_status} (Metrics count: {cost_metrics_count}, Warning: {cost_res.get('warning')})")
    print(f"  - Weather: {w_temp}°C via {w_provider}")
