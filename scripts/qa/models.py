"""Data models for UrbanLens QA Crawler results, issues, and consistency tracking."""

from dataclasses import dataclass, field, asdict
from typing import Any, Literal

Severity = Literal["P0", "P1", "P2", "P3"]

@dataclass
class QAIssue:
    severity: Severity
    category: str
    route: str
    city: str
    action: str
    expected: str
    actual: str
    source_api: str
    evidence: str
    screenshot: str | None = None
    recommended_fix: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

@dataclass
class BrowserLogEntry:
    entry_type: Literal["console_error", "console_warn", "pageerror", "network_failed", "http_error"]
    url: str
    message: str
    status: int | None = None
    route: str = ""
    timestamp: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

@dataclass
class CityConsistencyResult:
    city_id: str
    city_name: str
    country: str
    identity_status: str = "PASS"
    weather_status: str = "PASS"
    aq_status: str = "PASS"
    cost_status: str = "PASS"
    universities_status: str = "PASS"
    transit_status: str = "PASS"
    map_status: str = "PASS"
    ask_ai_status: str = "PASS"
    issues_summary: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

@dataclass
class PerformanceMetric:
    operation: str
    route: str
    latency_ms: float
    status_code: int
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
