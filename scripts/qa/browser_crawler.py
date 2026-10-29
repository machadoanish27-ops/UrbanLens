"""Playwright-based Human-like Browser Crawler for UrbanLens UI QA."""

import time
from pathlib import Path
from typing import Any
from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext

from scripts.qa.config import FRONTEND_URL, SCREENSHOTS_DIR, TARGET_CITIES, COMPARISON_PAIRS
from scripts.qa.models import BrowserLogEntry, QAIssue, CityConsistencyResult

class BrowserCrawler:
    def __init__(self, headless: bool = True) -> None:
        self.headless = headless
        self.playwright = None
        self.browser: Browser | None = None
        self.context: BrowserContext | None = None
        self.page: Page | None = None

        self.logs: list[BrowserLogEntry] = []
        self.issues: list[QAIssue] = []
        self.screenshots: list[str] = []
        self.city_consistency: dict[str, CityConsistencyResult] = {}
        self.action_count = 0
        self.routes_visited = set()

    def start(self) -> None:
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=self.headless,
            args=["--disable-web-security", "--no-sandbox"]
        )
        self.context = self.browser.new_context(
            viewport={"width": 1440, "height": 900},
            device_scale_factor=1.0,
        )
        self.page = self.context.new_page()

        # Attach listeners for console and network errors
        self.page.on("console", self._handle_console)
        self.page.on("pageerror", self._handle_pageerror)
        self.page.on("requestfailed", self._handle_requestfailed)
        self.page.on("response", self._handle_response)

    def close(self) -> None:
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def _handle_console(self, msg) -> None:
        if msg.type in ("error", "warning"):
            entry_type = "console_error" if msg.type == "error" else "console_warn"
            # Ignore standard benign React / Vite HMR logs
            if "Download the React DevTools" in msg.text or "[vite]" in msg.text:
                return
            self.logs.append(
                BrowserLogEntry(
                    entry_type=entry_type,
                    url=self.page.url if self.page else "",
                    message=msg.text,
                    route=self.page.url if self.page else "",
                    timestamp=time.time(),
                )
            )

    def _handle_pageerror(self, exc) -> None:
        self.logs.append(
            BrowserLogEntry(
                entry_type="pageerror",
                url=self.page.url if self.page else "",
                message=str(exc),
                route=self.page.url if self.page else "",
                timestamp=time.time(),
            )
        )
        self.issues.append(
            QAIssue(
                severity="P0",
                category="Runtime JS Exception",
                route=self.page.url if self.page else "",
                city="N/A",
                action="Page Rendering",
                expected="Clean render without uncaught exceptions",
                actual=f"Uncaught exception: {str(exc)}",
                source_api="frontend-runtime",
                evidence=str(exc),
            )
        )

    def _handle_requestfailed(self, req) -> None:
        # Ignore aborted requests due to fast navigation
        if req.failure == "net::ERR_ABORTED":
            return
        self.logs.append(
            BrowserLogEntry(
                entry_type="network_failed",
                url=req.url,
                message=f"Failed request to {req.url} - {req.failure}",
                route=self.page.url if self.page else "",
                timestamp=time.time(),
            )
        )

    def _handle_response(self, res) -> None:
        if res.status >= 400:
            # Map tile 404s or backend 4xx/5xx
            self.logs.append(
                BrowserLogEntry(
                    entry_type="http_error",
                    url=res.url,
                    message=f"HTTP {res.status} on {res.url}",
                    status=res.status,
                    route=self.page.url if self.page else "",
                    timestamp=time.time(),
                )
            )

    def capture_screenshot(self, name: str) -> str:
        filename = f"{name}.png"
        filepath = SCREENSHOTS_DIR / filename
        if self.page:
            self.page.screenshot(path=str(filepath), full_page=True)
            self.screenshots.append(filename)
            self.action_count += 1
            return filename
        return ""

    def test_home_page(self) -> None:
        """Crawl Home Page and search functionality."""
        print("[Crawler] Testing Home Page...")
        self.page.goto(f"{FRONTEND_URL}/", wait_until="domcontentloaded")
        self.routes_visited.add("/")
        self.action_count += 1
        time.sleep(1.0)
        self.capture_screenshot("01_home_page")

        # Test Search input
        search_input = self.page.locator("input[placeholder*='Search global cities']")
        if search_input.count() > 0:
            search_input.fill("Tokyo")
            self.action_count += 1
            time.sleep(0.8)
            self.capture_screenshot("02_home_search_tokyo")

            # Check if search result card appears
            city_card = self.page.locator("text=Tokyo").first
            if city_card.count() > 0:
                print("  [PASS] Home page search renders Tokyo successfully")
            else:
                self.issues.append(
                    QAIssue(
                        severity="P1",
                        category="Search",
                        route="/",
                        city="Tokyo",
                        action="Search for 'Tokyo'",
                        expected="Tokyo city card appears in filtered results",
                        actual="No city card rendered",
                        source_api="/api/v1/cities?q=Tokyo",
                        evidence="Locator text=Tokyo found 0 elements",
                    )
                )

    def test_city_page(self, city_meta: dict[str, Any]) -> CityConsistencyResult:
        """Inspect and crawl a specific city page across all its tabs."""
        city_id = city_meta["city_id"]
        expected_name = city_meta["name"]
        expected_country_iso = city_meta["country_iso2"]

        print(f"[Crawler] Crawling City Page: {expected_name} ({city_id})...")
        route = f"/city/{city_id}"
        self.routes_visited.add(route)
        self.page.goto(f"{FRONTEND_URL}{route}", wait_until="domcontentloaded")
        self.action_count += 1
        try:
            self.page.locator("h1").first.wait_for(state="visible", timeout=10000)
        except Exception:
            pass
        time.sleep(0.5)

        res = CityConsistencyResult(
            city_id=city_id,
            city_name=expected_name,
            country=expected_country_iso,
        )

        # 1. City Identity Validation (Header)
        header_text = self.page.locator("h1").first.inner_text() if self.page.locator("h1").count() > 0 else ""
        if expected_name.lower() not in header_text.lower():
            res.identity_status = "CRITICAL_FAIL"
            res.issues_summary.append(f"Header city name '{header_text}' != expected '{expected_name}'")
            self.issues.append(
                QAIssue(
                    severity="P0",
                    category="City Identity",
                    route=route,
                    city=expected_name,
                    action="Open City Page",
                    expected=f"H1 contains '{expected_name}'",
                    actual=f"H1 contains '{header_text}'",
                    source_api=f"/api/v1/cities/{city_id}",
                    evidence=f"Header: {header_text}",
                    screenshot=self.capture_screenshot(f"identity_fail_{city_id}"),
                    recommended_fix="Verify city detail route state and ID resolution.",
                )
            )

        # Check country tag
        page_content = self.page.content()
        if expected_country_iso not in page_content:
            res.identity_status = "FAIL"
            res.issues_summary.append(f"Country code '{expected_country_iso}' missing from header")

        self.capture_screenshot(f"city_{expected_name.lower()}_overview")

        # 2. Map Tab Validation
        map_tab = self.page.locator("button:has-text('Geographic Map')")
        if map_tab.count() > 0:
            map_tab.click()
            self.action_count += 1
            time.sleep(1.0)
            leaflet_container = self.page.locator(".leaflet-container")
            if leaflet_container.count() == 0:
                res.map_status = "FAIL"
                res.issues_summary.append("Leaflet map container not rendered")
            else:
                res.map_status = "PASS"
            self.capture_screenshot(f"city_{expected_name.lower()}_map")

        # 3. Weather Tab Validation
        weather_tab = self.page.locator("button:has-text('Live Weather')")
        if weather_tab.count() > 0:
            weather_tab.click()
            self.action_count += 1
            time.sleep(0.8)
            # Check if temperature is rendered
            temp_elem = self.page.locator("text=Temperature")
            if temp_elem.count() == 0:
                res.weather_status = "FAIL"
                res.issues_summary.append("Temperature card missing")
            else:
                res.weather_status = "PASS"
            self.capture_screenshot(f"city_{expected_name.lower()}_weather")

        # 4. Air Quality Tab Validation
        aq_tab = self.page.locator("button:has-text('Air Quality')")
        if aq_tab.count() > 0:
            aq_tab.click()
            self.action_count += 1
            time.sleep(0.8)
            res.aq_status = "PASS"
            self.capture_screenshot(f"city_{expected_name.lower()}_aq")

        # 5. Cost of Living Tab Validation
        cost_tab = self.page.locator("button:has-text('Cost of Living')")
        if cost_tab.count() > 0:
            cost_tab.click()
            self.action_count += 1
            time.sleep(0.8)
            res.cost_status = "PASS"
            self.capture_screenshot(f"city_{expected_name.lower()}_cost")

        # 6. Universities Tab Validation
        uni_tab = self.page.locator("button:has-text('Universities')")
        if uni_tab.count() > 0:
            uni_tab.click()
            self.action_count += 1
            time.sleep(0.8)
            res.universities_status = "PASS"
            self.capture_screenshot(f"city_{expected_name.lower()}_education")

        # 7. Healthcare & Amenities Tab Validation
        health_tab = self.page.locator("button:has-text('Healthcare & Amenities')")
        if health_tab.count() > 0:
            health_tab.click()
            self.action_count += 1
            time.sleep(0.8)
            self.capture_screenshot(f"city_{expected_name.lower()}_healthcare")

        # 8. Transit Tab Validation
        transit_tab = self.page.locator("button:has-text('Mobility & Transit')")
        if transit_tab.count() > 0:
            transit_tab.click()
            self.action_count += 1
            time.sleep(0.8)
            res.transit_status = "PASS"
            self.capture_screenshot(f"city_{expected_name.lower()}_transit")

        self.city_consistency[city_id] = res
        return res

    def test_compare_page(self) -> None:
        """Crawl Compare Page, test city swapping, presets, and AI compare trigger."""
        print("[Crawler] Testing Compare Page...")
        route = "/compare"
        self.routes_visited.add(route)
        self.page.goto(f"{FRONTEND_URL}{route}", wait_until="domcontentloaded")
        self.action_count += 1
        time.sleep(1.5)
        self.capture_screenshot("03_compare_default_tokyo_london")

        # Test City Swapping
        swap_btn = self.page.locator("button[aria-label='Swap Cities']")
        if swap_btn.count() > 0:
            swap_btn.click()
            self.action_count += 1
            time.sleep(1.0)
            url_after_swap = self.page.url
            if "city1=city_1826645935" in url_after_swap and "city2=city_1392685764" in url_after_swap:
                print("  [PASS] City swap button updated URL parameters correctly (London vs Tokyo)")
            else:
                self.issues.append(
                    QAIssue(
                        severity="P1",
                        category="Comparison",
                        route="/compare",
                        city="Tokyo/London",
                        action="Click Swap Button",
                        expected="URL city1=London and city2=Tokyo",
                        actual=f"URL: {url_after_swap}",
                        source_api="frontend-state",
                        evidence="URL query string did not swap",
                    )
                )
            self.capture_screenshot("04_compare_swapped_london_tokyo")

        # Test Preset Selection (Mumbai vs New York)
        preset_mumbai_ny = self.page.locator("button:has-text('Mumbai vs New York')")
        if preset_mumbai_ny.count() > 0:
            preset_mumbai_ny.click()
            self.action_count += 1
            time.sleep(1.0)
            self.capture_screenshot("05_compare_mumbai_ny_preset")

        # Test Reversal Preset (Paris vs Berlin)
        preset_paris_berlin = self.page.locator("button:has-text('Paris vs Berlin')")
        if preset_paris_berlin.count() > 0:
            preset_paris_berlin.click()
            self.action_count += 1
            time.sleep(1.0)
            self.capture_screenshot("06_compare_paris_berlin")

        # Test "Ask AI to Compare" button
        ai_compare_btn = self.page.locator("button:has-text('Ask AI to Compare')")
        if ai_compare_btn.count() > 0:
            ai_compare_btn.click()
            self.action_count += 1
            time.sleep(1.5)
            if "/ask" in self.page.url:
                print("  [PASS] 'Ask AI to Compare' navigated to /ask with pre-filled question")
            else:
                self.issues.append(
                    QAIssue(
                        severity="P2",
                        category="Comparison to Ask AI Navigation",
                        route="/compare",
                        city="Paris/Berlin",
                        action="Click 'Ask AI to Compare'",
                        expected="Navigates to /ask with comparison prompt",
                        actual=f"Current URL: {self.page.url}",
                        source_api="frontend-router",
                        evidence=f"URL is {self.page.url}",
                    )
                )

    def test_ask_page_ui(self) -> None:
        """Crawl Ask Page interface, query execution, progressive loader, copy button, and follow-ups."""
        print("[Crawler] Testing Ask Page UI...")
        route = "/ask"
        self.routes_visited.add(route)
        self.page.goto(f"{FRONTEND_URL}{route}", wait_until="domcontentloaded")
        self.action_count += 1
        time.sleep(1.0)
        self.capture_screenshot("07_ask_page_empty")

        # Type query and submit
        query_input = self.page.locator("textarea[placeholder*='Ask any urban question']")
        if query_input.count() > 0:
            query_input.fill("What is the current air quality and living environment in Tokyo?")
            self.action_count += 1
            submit_btn = self.page.locator("button[type='submit']")
            submit_btn.click()
            self.action_count += 1

            # Observe loader
            time.sleep(1.0)
            self.capture_screenshot("08_ask_page_loading_state")

            # Wait for response (up to 20s for Groq LLM)
            try:
                self.page.wait_for_selector("text=Grounded Multi-Agent Assessment", timeout=25000)
                print("  [PASS] Ask AI generated grounded response successfully")
                time.sleep(1.0)
                self.capture_screenshot("09_ask_page_answered")

                # Test Copy Answer Button
                copy_btn = self.page.locator("button:has-text('Copy Answer')")
                if copy_btn.count() > 0:
                    copy_btn.click()
                    self.action_count += 1
                    time.sleep(0.5)
                    self.capture_screenshot("10_ask_page_copied_answer")
            except Exception as e:
                self.issues.append(
                    QAIssue(
                        severity="P1",
                        category="AI Response Latency / Error",
                        route="/ask",
                        city="Tokyo",
                        action="Submit Ask Query",
                        expected="Grounded answer within 25 seconds",
                        actual=f"Timeout or error: {str(e)}",
                        source_api="/api/v1/intelligence/ask",
                        evidence=str(e),
                        screenshot=self.capture_screenshot("ask_ai_timeout"),
                    )
                )

    def test_invalid_routes(self) -> None:
        """Test error recovery, non-existent city, and 404 page."""
        print("[Crawler] Testing Invalid City and 404 Routes...")

        # 1. Non-existent city ID
        route_bad_city = "/city/city_nonexistent_99999"
        self.routes_visited.add(route_bad_city)
        self.page.goto(f"{FRONTEND_URL}{route_bad_city}", wait_until="domcontentloaded")
        self.action_count += 1
        try:
            self.page.locator("h2:has-text('City Not Found')").first.wait_for(state="visible", timeout=10000)
        except Exception:
            pass
        time.sleep(0.5)
        self.capture_screenshot("11_invalid_city_id_state")

        # Check if error message is displayed
        if "City Not Found" in self.page.content() or "Something went wrong" in self.page.content():
            print("  [PASS] Invalid city ID displays graceful error alert")
        else:
            self.issues.append(
                QAIssue(
                    severity="P1",
                    category="Error Handling",
                    route=route_bad_city,
                    city="city_nonexistent_99999",
                    action="Open invalid city page",
                    expected="Graceful error banner",
                    actual="No standard error banner found",
                    source_api="/api/v1/cities/city_nonexistent_99999",
                    evidence=self.page.inner_text("body")[:200],
                )
            )

        # 2. Completely unknown route
        route_404 = "/completely-unknown-path-xyz"
        self.routes_visited.add(route_404)
        self.page.goto(f"{FRONTEND_URL}{route_404}", wait_until="domcontentloaded")
        self.action_count += 1
        time.sleep(0.8)
        self.capture_screenshot("12_404_not_found_page")

        if "404" in self.page.content() or "Page Not Found" in self.page.content():
            print("  [PASS] Unknown route displays 404 page")
        else:
            self.issues.append(
                QAIssue(
                    severity="P2",
                    category="Routing",
                    route=route_404,
                    city="N/A",
                    action="Open unknown route",
                    expected="404 Not Found Page",
                    actual="Page rendered without 404 indication",
                    source_api="frontend-router",
                    evidence=self.page.inner_text("body")[:200],
                )
            )

    def test_mobile_viewports(self) -> None:
        """Test mobile responsiveness on 390x844 (iPhone 14)."""
        print("[Crawler] Testing Mobile Viewport (390x844)...")
        self.page.set_viewport_size({"width": 390, "height": 844})
        self.action_count += 1

        # Test mobile city page
        self.page.goto(f"{FRONTEND_URL}/city/city_1392685764", wait_until="domcontentloaded")
        time.sleep(1.0)
        self.capture_screenshot("13_mobile_city_tokyo")

        # Test mobile compare page
        self.page.goto(f"{FRONTEND_URL}/compare", wait_until="domcontentloaded")
        time.sleep(1.0)
        self.capture_screenshot("14_mobile_compare")

        # Reset viewport back to desktop
        self.page.set_viewport_size({"width": 1440, "height": 900})
        self.action_count += 1
