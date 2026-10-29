"""Regression test suite for Phase 4: Authoritative Languages and Cultural Metadata."""

import pytest
from starlette.testclient import TestClient

from app.data.languages import COUNTRY_LANGUAGE_REGISTRY, get_country_languages
from app.schemas.country import CountryLanguageInfo


def test_country_language_registry_standards():
    """Verify registry entries adhere to ISO-639 / UN standards with provenance."""
    assert "JP" in COUNTRY_LANGUAGE_REGISTRY
    assert "GB" in COUNTRY_LANGUAGE_REGISTRY
    assert "IN" in COUNTRY_LANGUAGE_REGISTRY
    assert "US" in COUNTRY_LANGUAGE_REGISTRY
    assert "FR" in COUNTRY_LANGUAGE_REGISTRY
    assert "SG" in COUNTRY_LANGUAGE_REGISTRY
    assert "AE" in COUNTRY_LANGUAGE_REGISTRY

    # Check Japan
    jp = get_country_languages("country_JP")
    assert jp["status"] == "available"
    assert "Japanese" in jp["official_languages"]
    assert "ja" in jp["language_codes"]
    assert jp["level"] == "country"
    assert jp["source"] is not None

    # Check India
    india = get_country_languages("IN")
    assert india["status"] == "available"
    assert "Hindi" in india["official_languages"]
    assert "English" in india["official_languages"]
    assert len(india["spoken_languages"]) >= 5

    # Check Singapore
    sg = get_country_languages("SG")
    assert sg["status"] == "available"
    assert len(sg["official_languages"]) == 4  # English, Malay, Mandarin Chinese, Tamil


def test_unavailable_territory_language_handling():
    """Verify unindexed territory returns explicit status: 'unavailable' without fabricating data."""
    unavail = get_country_languages("country_NONEXISTENT_XYZ")
    assert unavail["status"] == "unavailable"
    assert unavail["official_languages"] == []
    assert unavail["spoken_languages"] == []
    assert unavail["source"] is None
    assert "not currently indexed" in unavail["cultural_notes"].lower()


def test_country_languages_api_endpoint(client: TestClient):
    """Verify GET /api/v1/countries/{country_id}/languages returns structured response."""
    resp = client.get("/api/v1/countries/japan/languages")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["status"] == "available"
    assert "Japanese" in data["official_languages"]
    assert data["level"] == "country"


def test_city_details_includes_country_languages(client: TestClient):
    """Verify GET /api/v1/cities/{city_id} includes authoritative country-level language data."""
    resp = client.get("/api/v1/cities/tokyo_jp")
    assert resp.status_code == 200
    data = resp.json()["data"]
    langs = data.get("languages")
    assert langs is not None
    assert langs["status"] == "available"
    assert "Japanese" in langs["official_languages"]
    assert langs["level"] == "country"
