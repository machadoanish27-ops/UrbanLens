"""Regression tests for city population density resolution and honest unavailable state."""

import pytest
from app.services.city import CityService

def test_population_density_known_area(mock_db):
    """Test city with known area_km2 correctly calculates population density."""
    mock_db["cities"].documents.append({
        "city_id": "city_with_area",
        "name": "DenseCity",
        "population": 1000000,
        "area_km2": 100.0,
        "country_id": "country_JP",
        "country_iso2": "JP",
    })

    service = CityService(mock_db)
    city = service.get_city_details("city_with_area")
    
    density = city.get("population_density")
    assert density is not None
    assert density["status"] == "available"
    assert density["value"] == 10000.0
    assert density["unit"] == "people/km²"
    assert density["area_km2"] == 100.0
    assert density["level"] == "city"

def test_population_density_unavailable_area(mock_db):
    """Test city without area_km2 returns honest unavailable status without fabricated numbers."""
    mock_db["cities"].documents.append({
        "city_id": "city_without_area",
        "name": "NoAreaCity",
        "population": 500000,
        "area_km2": None,
        "country_id": "country_JP",
        "country_iso2": "JP",
    })

    service = CityService(mock_db)
    city = service.get_city_details("city_without_area")
    
    density = city.get("population_density")
    assert density is not None
    assert density["status"] == "unavailable"
    assert density["value"] is None
    assert density["area_km2"] is None
