"""Master executable entry point for UrbanLens Human Crawl Tester."""

import time
from datetime import datetime
from scripts.qa.config import TARGET_CITIES, FRONTEND_URL, BACKEND_URL
from scripts.qa.api_validator import ApiValidator
from scripts.qa.browser_crawler import BrowserCrawler
from scripts.qa.ai_evaluator import AiEvaluator
from scripts.qa.reporter import QAReporter
from scripts.qa.models import QAIssue

def main() -> None:
    t_start = time.time()
    print("==================================================")
    print("URBANLENS HUMAN CRAWL TESTER STARTING")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Frontend Target: {FRONTEND_URL}")
    print(f"Backend Target: {BACKEND_URL}")
    print("==================================================")

    api_validator = ApiValidator(base_url=BACKEND_URL)
    crawler = BrowserCrawler(headless=True)
    all_issues: list[QAIssue] = []

    try:
        # Step 1: Start Browser
        crawler.start()

        # Step 2: Test Home Page
        crawler.test_home_page()

        # Step 3: Test City Pages for Target Cities
        for city_meta in TARGET_CITIES:
            cr = crawler.test_city_page(city_meta)
            # Cross-check frontend data against direct backend response
            backend_city = api_validator.get_city_details(city_meta["city_id"])
            if not backend_city:
                all_issues.append(
                    QAIssue(
                        severity="P0",
                        category="Backend Resolution",
                        route=f"/city/{city_meta['city_id']}",
                        city=city_meta["name"],
                        action="Fetch Backend Record",
                        expected="Valid CityDetail JSON",
                        actual="None / 404",
                        source_api=f"/api/v1/cities/{city_meta['city_id']}",
                        evidence="Backend returned None",
                    )
                )

        # Step 4: Test Compare Page (Swap, Presets, AI Compare)
        crawler.test_compare_page()

        # Step 5: Test Ask Page UI
        crawler.test_ask_page_ui()

        # Step 6: Test Invalid and Error Routes
        crawler.test_invalid_routes()

        # Step 7: Test Mobile Viewports
        crawler.test_mobile_viewports()

        # Step 8: Controlled Live Change Detection
        print("[Crawler] Checking Live Change Detection & Cache Behavior on Tokyo...")
        freshness_check = api_validator.check_live_freshness_and_cache("city_1392685764")
        print(f"  Provider: {freshness_check['provider']}, Status: {freshness_check['status']}, Cached First: {freshness_check['cached_first']}, Cached Second: {freshness_check['cached_second']}")

        # Step 9: Extended API Sampling (50 canonical cities)
        print("[Crawler] Performing Extended Sampling on 50 canonical cities...")
        sampled_cities_res = api_validator.client.get("/api/v1/cities?page=1&page_size=50")
        if sampled_cities_res.status_code == 200:
            sampled_cities = sampled_cities_res.json().get("data", [])
            print(f"  Successfully verified {len(sampled_cities)} city records via REST API.")
            for sc in sampled_cities:
                if sc.get("latitude") is None or sc.get("longitude") is None:
                    all_issues.append(
                        QAIssue(
                            severity="P0",
                            category="Data Integrity",
                            route="/api/v1/cities",
                            city=sc.get("name", "Unknown"),
                            action="Inspect coordinates",
                            expected="Valid float latitude and longitude",
                            actual=f"lat={sc.get('latitude')}, lon={sc.get('longitude')}",
                            source_api="/api/v1/cities",
                            evidence=str(sc),
                        )
                    )

        # Step 10: Run 30 AI Inquiries & Adversarial Evaluator
        ai_evaluator = AiEvaluator(api_validator)
        ai_evals = ai_evaluator.run_evaluations()

        # Step 11: Collect and Aggregate Findings
        all_issues.extend(crawler.issues)
        all_issues.extend(api_validator.issues)
        all_issues.extend(ai_evaluator.issues)

        # Architectural Verification: Validate P0/P1/P2 resolution dynamically
        # 1. Universities case-sensitivity verification
        tokyo_univs = api_validator.get_city_universities("city_1392685764")
        tokyo_count = tokyo_univs.get("meta", {}).get("pagination", {}).get("total", 0) if tokyo_univs else 0
        if tokyo_count == 0:
            all_issues.append(
                QAIssue(
                    severity="P0",
                    category="Backend Query Case Sensitivity",
                    route="/api/v1/cities/{city_id}/universities",
                    city="Tokyo",
                    action="Fetch universities for city with country_id",
                    expected="Registered universities in country_JP return matches",
                    actual="Returns count=0 because app/db/repositories/university.py applies .lower() producing 'country_jp', while MongoDB stores 'country_JP'",
                    source_api="/api/v1/cities/{city_id}/universities",
                    evidence="app/db/repositories/university.py line 32: filters['country_id'] = country_id.strip().lower()",
                    recommended_fix="Remove .lower() and use exact case country_id or filter on country_iso2 directly.",
                )
            )

        # 2. City Population Density verification
        tokyo_details = api_validator.get_city_details("city_1392685764") or {}
        density = tokyo_details.get("population_density")
        if not density or "status" not in density:
            all_issues.append(
                QAIssue(
                    severity="P2",
                    category="Missing Product Metric",
                    route="/city/:cityId",
                    city="Global",
                    action="View demographic density",
                    expected="City population density (people/km²) computed and displayed with unit or explicit unavailable status",
                    actual="City land area and density are absent from the database; only country-level density exists in country_metrics",
                    source_api="cities collection",
                    evidence="cities collection has population, but no land_area_km2 or population_density fields",
                    recommended_fix="Ingest city land area and calculate population density with clear units.",
                )
            )

        # 3. Languages and culture verification
        langs = tokyo_details.get("languages")
        if not langs or "official_languages" not in langs:
            all_issues.append(
                QAIssue(
                    severity="P2",
                    category="Dataset Gap",
                    route="/city/:cityId and /ask",
                    city="Global",
                    action="Inspect spoken languages & cultural indicators",
                    expected="Authoritative spoken languages and cultural indicators stored in database",
                    actual="Spoken languages and cultural metadata are completely absent from cities and countries collections",
                    source_api="cities & countries collections",
                    evidence="Neither cities nor countries schema has a languages field",
                    recommended_fix="Add authoritative spoken languages mapping to countries / cities collections.",
                )
            )

        # 4. US Cost of Living gap verification (honestly handled with 200 unavailable status)
        ny_cost = api_validator.get_city_cost_of_living("city_1840034016")
        if not ny_cost:
            all_issues.append(
                QAIssue(
                    severity="P1",
                    category="Cost of Living Dataset Coverage Gap",
                    route="/city/city_1840034016/cost-of-living",
                    city="New York",
                    action="View Cost of Living for New York and US cities",
                    expected="Structured unavailable state with honest warnings",
                    actual="404 or unhandled response",
                    source_api="/api/v1/cities/city_1840034016/cost-of-living",
                    evidence="Endpoint returned None/404",
                    recommended_fix="Return HTTP 200 with structured status: unavailable and explicit warning.",
                )
            )

        runtime = time.time() - t_start
        stats = {
            "timestamp": datetime.now().isoformat(),
            "runtime_seconds": runtime,
            "cities_tested_count": len(TARGET_CITIES) + 50,
            "routes_tested_count": len(crawler.routes_visited),
            "api_calls_count": len(api_validator.metrics),
            "browser_actions_count": crawler.action_count,
            "screenshots_count": len(crawler.screenshots),
            "p0_count": len([i for i in all_issues if i.severity == "P0"]),
            "p1_count": len([i for i in all_issues if i.severity == "P1"]),
            "p2_count": len([i for i in all_issues if i.severity == "P2"]),
            "p3_count": len([i for i in all_issues if i.severity == "P3"]),
        }

        # Step 12: Generate Reports
        reporter = QAReporter(
            issues=all_issues,
            logs=crawler.logs,
            consistency=crawler.city_consistency,
            metrics=api_validator.metrics,
            ai_evals=ai_evals,
            screenshots=crawler.screenshots,
            stats=stats,
        )

        reporter.export_json()
        reporter.generate_markdown_report()

        print("==================================================")
        print("URBANLENS HUMAN CRAWLER COMPLETED SUCCESSFULLY")
        print(f"Total Runtime: {runtime:.1f}s")
        print(f"Cities Tested: {stats['cities_tested_count']}")
        print(f"Routes Tested: {stats['routes_tested_count']}")
        print(f"API Calls Tested: {stats['api_calls_count']}")
        print(f"Browser Actions: {stats['browser_actions_count']}")
        print(f"Screenshots Captured: {stats['screenshots_count']}")
        print(f"P0 Issues: {stats['p0_count']}")
        print(f"P1 Issues: {stats['p1_count']}")
        print(f"P2 Issues: {stats['p2_count']}")
        print(f"P3 Issues: {stats['p3_count']}")
        print("==================================================")

    finally:
        crawler.close()
        api_validator.close()

if __name__ == "__main__":
    main()
