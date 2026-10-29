"""Backend REST API validator and data consistency inspector."""

import time
import httpx
from typing import Any
from scripts.qa.config import BACKEND_URL
from scripts.qa.models import PerformanceMetric, QAIssue

class ApiValidator:
    def __init__(self, base_url: str = BACKEND_URL) -> None:
        self.base_url = base_url.rstrip("/")
        self.client = httpx.Client(base_url=self.base_url, timeout=45.0)
        self.issues: list[QAIssue] = []
        self.metrics: list[PerformanceMetric] = []

    def close(self) -> None:
        self.client.close()

    def get_city_details(self, city_id: str) -> dict[str, Any] | None:
        t0 = time.perf_counter()
        res = self.client.get(f"/api/v1/cities/{city_id}")
        latency = (time.perf_counter() - t0) * 1000
        self.metrics.append(PerformanceMetric("get_city_details", f"/api/v1/cities/{city_id}", latency, res.status_code))
        if res.status_code == 200:
            return res.json().get("data")
        return None

    def get_city_weather(self, city_id: str) -> dict[str, Any] | None:
        t0 = time.perf_counter()
        res = self.client.get(f"/api/v1/cities/{city_id}/weather/live")
        latency = (time.perf_counter() - t0) * 1000
        self.metrics.append(PerformanceMetric("get_city_weather", f"/api/v1/cities/{city_id}/weather/live", latency, res.status_code))
        if res.status_code == 200:
            return res.json().get("data")
        return None

    def get_city_air_quality(self, city_id: str) -> dict[str, Any] | None:
        t0 = time.perf_counter()
        res = self.client.get(f"/api/v1/cities/{city_id}/air-quality")
        latency = (time.perf_counter() - t0) * 1000
        self.metrics.append(PerformanceMetric("get_city_air_quality", f"/api/v1/cities/{city_id}/air-quality", latency, res.status_code))
        if res.status_code == 200:
            return res.json().get("data")
        return None

    def get_city_cost_of_living(self, city_id: str) -> dict[str, Any] | None:
        t0 = time.perf_counter()
        res = self.client.get(f"/api/v1/cities/{city_id}/cost-of-living")
        latency = (time.perf_counter() - t0) * 1000
        self.metrics.append(PerformanceMetric("get_city_cost", f"/api/v1/cities/{city_id}/cost-of-living", latency, res.status_code))
        if res.status_code == 200:
            return res.json().get("data")
        return None

    def get_city_universities(self, city_id: str) -> dict[str, Any] | None:
        t0 = time.perf_counter()
        res = self.client.get(f"/api/v1/cities/{city_id}/universities")
        latency = (time.perf_counter() - t0) * 1000
        self.metrics.append(PerformanceMetric("get_city_universities", f"/api/v1/cities/{city_id}/universities", latency, res.status_code))
        if res.status_code == 200:
            return res.json()
        return None

    def get_city_transit(self, city_id: str) -> dict[str, Any] | None:
        t0 = time.perf_counter()
        res = self.client.get(f"/api/v1/transit/{city_id}")
        latency = (time.perf_counter() - t0) * 1000
        self.metrics.append(PerformanceMetric("get_city_transit", f"/api/v1/transit/{city_id}", latency, res.status_code))
        if res.status_code == 200:
            return res.json().get("data")
        return None

    def get_places(self, lat: float, lon: float, category: str = "hospital") -> list[dict[str, Any]]:
        t0 = time.perf_counter()
        res = self.client.get("/api/v1/places/search", params={"lat": lat, "lon": lon, "category": category, "radius": 4000, "limit": 10})
        latency = (time.perf_counter() - t0) * 1000
        self.metrics.append(PerformanceMetric("get_places", "/api/v1/places/search", latency, res.status_code))
        if res.status_code == 200:
            return res.json().get("data", {}).get("places", [])
        return []

    def get_city_intelligence(self, city_id: str) -> dict[str, Any] | None:
        t0 = time.perf_counter()
        res = self.client.get(f"/api/v1/cities/{city_id}/intelligence")
        latency = (time.perf_counter() - t0) * 1000
        self.metrics.append(PerformanceMetric("get_city_intelligence", f"/api/v1/cities/{city_id}/intelligence", latency, res.status_code))
        if res.status_code == 200:
            return res.json().get("data")
        return None

    def ask_ai(self, query: str, city_id: str | None = None) -> dict[str, Any] | None:
        t0 = time.perf_counter()
        payload: dict[str, Any] = {"query": query}
        if city_id:
            payload["city_id"] = city_id
        try:
            res = self.client.post("/api/v1/intelligence/ask", json=payload, timeout=90.0)
            latency = (time.perf_counter() - t0) * 1000
            self.metrics.append(PerformanceMetric("ask_ai", "/api/v1/intelligence/ask", latency, res.status_code, notes=query[:40]))
            if res.status_code == 200:
                return res.json().get("data")
        except (httpx.TimeoutException, httpx.RequestError) as exc:
            latency = (time.perf_counter() - t0) * 1000
            self.metrics.append(PerformanceMetric("ask_ai", "/api/v1/intelligence/ask", latency, 504, notes=f"Timeout: {exc}"))
            return None
        return None

    def check_live_freshness_and_cache(self, city_id: str) -> dict[str, Any]:
        """Perform controlled repeat calls to determine if live timestamps update or cache is used."""
        first = self.get_city_weather(city_id)
        time.sleep(1.0)
        second = self.get_city_weather(city_id)

        meta1 = first.get("meta", {}) if first else {}
        meta2 = second.get("meta", {}) if second else {}

        provider1 = meta1.get("provider")
        status1 = meta1.get("status")
        cached1 = meta1.get("cached", False)
        cached2 = meta2.get("cached", False)

        return {
            "city_id": city_id,
            "provider": provider1,
            "status": status1,
            "cached_first": cached1,
            "cached_second": cached2,
            "meta_first": meta1,
            "meta_second": meta2,
        }
