"""Regression tests for university repository country_id case sensitivity."""

import pytest
from app.db.repositories.university import UniversityRepository
from app.services.university import UniversityService
from app.core.exceptions import ResourceNotFoundException

def test_university_repository_country_id_canonical_case(mock_db):
    """Verify repository correctly handles canonical uppercase country_id."""
    repo = UniversityRepository(mock_db)
    
    # Overwrite with clean test fixtures
    mock_db["universities"].documents = [
        {"university_id": "u1", "name": "Tokyo Tech", "country_id": "country_JP", "country_iso2": "JP"},
        {"university_id": "u2", "name": "Kyoto Univ", "country_id": "country_JP", "country_iso2": "JP"},
        {"university_id": "u3", "name": "Oxford Univ", "country_id": "country_GB", "country_iso2": "GB"},
    ]

    # Query with exact canonical uppercase
    items, total = repo.get_universities_by_country(country_id="country_JP")
    assert total == 2
    assert [i["name"] for i in items] == ["Kyoto Univ", "Tokyo Tech"]

    # Query with lowercase input (should canonicalize to country_JP)
    items_lower, total_lower = repo.get_universities_by_country(country_id="country_jp")
    assert total_lower == 2
    assert [i["name"] for i in items_lower] == ["Kyoto Univ", "Tokyo Tech"]

    # Query with country_iso2
    items_iso, total_iso = repo.get_universities_by_country(country_iso2="JP")
    assert total_iso == 2

    # Query for GB
    items_gb, total_gb = repo.get_universities_by_country(country_id="country_GB")
    assert total_gb == 1
    assert items_gb[0]["name"] == "Oxford Univ"

def test_university_service_get_by_city(mock_db):
    """Verify UniversityService resolves city country_id and returns matching institutions."""
    mock_db["cities"].documents.append({
        "city_id": "city_tokyo_test",
        "name": "Tokyo",
        "country_id": "country_JP",
        "country_iso2": "JP",
    })
    mock_db["universities"].documents.append({
        "university_id": "u_tokyo_1",
        "name": "Tokyo University of Agriculture",
        "country_id": "country_JP",
        "country_iso2": "JP",
    })

    service = UniversityService(mock_db)
    items, total = service.get_universities_by_city("city_tokyo_test")
    assert total >= 1
    assert any("Tokyo" in u["name"] for u in items)

    # Non-existent city raises ResourceNotFoundException
    with pytest.raises(ResourceNotFoundException):
        service.get_universities_by_city("city_does_not_exist")
