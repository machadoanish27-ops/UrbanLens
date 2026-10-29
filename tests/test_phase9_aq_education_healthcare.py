"""Phase 9 Regression Tests: Air Quality Live/Fallback, Education Discovery & Healthcare Discovery."""

import asyncio
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.services.air_quality import AirQualityService
from app.services.education import EducationService
from app.services.healthcare import HealthcareService
from app.providers.base import LiveMetadata, LiveStatus, ProviderResponse
from app.providers.air_quality.base import NormalizedAirQuality, NormalizedPollutants
from app.providers.places.base import NormalizedPlaceItem


def test_air_quality_live_openaq_response(mock_db):
    """Verify live OpenAQ response returns status='live', provider='OpenAQ', and is_live=True."""
    async def run():
        mock_db["cities"].documents.append({
            "city_id": "city_tokyo_test",
            "name": "Tokyo",
            "latitude": 35.6895,
            "longitude": 139.6917,
        })

        service = AirQualityService(mock_db)

        norm_aq = NormalizedAirQuality(
            latitude=35.6895,
            longitude=139.6917,
            location_name="Tokyo Shinjuku Station",
            observed_at="2026-10-28T12:00:00Z",
            pollutants=NormalizedPollutants(pm25=11.5, pm10=22.0, no2=15.2, o3=35.0),
            available_pollutants=["pm25", "pm10", "no2", "o3"],
            provider="OpenAQ",
            status="live",
            is_live=True,
            warning=None,
        )
        mock_resp = ProviderResponse(
            meta=LiveMetadata(status=LiveStatus.FRESH, provider="openaq", source="https://api.openaq.org"),
            data=norm_aq,
        )

        with patch.object(service.provider, "get_air_quality", new=AsyncMock(return_value=mock_resp)):
            res = await service.get_live_air_quality("city_tokyo_test")
            aq = res["air_quality"]
            assert aq is not None
            assert aq["status"] == "live"
            assert aq["is_live"] is True
            assert aq["provider"] == "OpenAQ"
            assert aq["pollutants"]["pm25"] == 11.5
            assert res["meta"]["status"] in ("live", "fresh")

    asyncio.run(run())


def test_air_quality_fallback_who_annual_never_calls_fallback_live(mock_db):
    """Verify that when OpenAQ live fails, WHO database fallback has status='database', is_live=False, and never called live."""
    async def run():
        mock_db["cities"].documents.append({
            "city_id": "city_mumbai_test",
            "name": "Mumbai",
            "latitude": 19.0760,
            "longitude": 72.8777,
        })

        mock_db["air_quality_observations_who"].documents.append({
            "city_id": "city_mumbai_test",
            "year": "2022",
            "pm25_annual_mean_ug_m3": 54.0,
            "pm10_annual_mean_ug_m3": 105.0,
            "no2_annual_mean_ug_m3": 28.0,
        })

        service = AirQualityService(mock_db)

        fail_resp = ProviderResponse(
            meta=LiveMetadata(status=LiveStatus.UNAVAILABLE, provider="openaq", source="https://api.openaq.org", error_detail="OpenAQ timeout"),
            data=None,
        )

        with patch.object(service.provider, "get_air_quality", new=AsyncMock(return_value=fail_resp)):
            res = await service.get_live_air_quality("city_mumbai_test")
            aq = res["air_quality"]
            assert aq is not None
            # Strict rule: NEVER call fallback 'live'
            assert aq["status"] == "database"
            assert aq["is_live"] is False
            assert aq["provider"] == "WHO"
            assert aq["pollutants"]["pm25"] == 54.0
            assert aq["warning"] is not None
            assert "not live" in aq["warning"].lower() or "unavailable" in aq["warning"].lower()
            assert res["meta"]["status"] == "database"

    asyncio.run(run())


def test_education_university_of_mumbai_verified_website(mock_db):
    """Verify University of Mumbai is discovered with official website and canonical provenance."""
    async def run():
        mock_db["cities"].documents.append({
            "city_id": "city_1356226629",
            "name": "Mumbai",
            "country_id": "country_IN",
            "country_iso2": "IN",
            "latitude": 19.0760,
            "longitude": 72.8777,
        })

        mock_db["universities"].documents.append({
            "university_id": "university_91d9184fbbc9589f0011",
            "name": "University of Mumbai",
            "country_id": "country_IN",
            "country_iso2": "IN",
            "website": "http://www.mu.ac.in/",
        })

        service = EducationService(mock_db)
        mock_places = ProviderResponse(
            meta=LiveMetadata(status=LiveStatus.FRESH, provider="openstreetmap_overpass", source="https://overpass-api.de"),
            data=[],
        )

        with patch.object(service.places_provider, "get_places", new=AsyncMock(return_value=mock_places)):
            res = await service.get_city_education("city_1356226629")
            assert res.total >= 1
            insts = res.institutions
            mu = next((i for i in insts if "mumbai" in i.name.lower()), None)
            assert mu is not None
            assert mu.name == "University of Mumbai"
            assert mu.has_verified_website is True
            assert mu.website == "http://www.mu.ac.in/"
            assert mu.provider == "canonical_db"
            assert mu.type == "University"

    asyncio.run(run())


def test_education_missing_website_handling(mock_db):
    """Verify institutions without verified websites have has_verified_website=False without fabrication."""
    async def run():
        mock_db["cities"].documents.append({
            "city_id": "city_test_edu",
            "name": "TestCity",
            "country_id": "country_TC",
            "country_iso2": "TC",
            "latitude": 10.0,
            "longitude": 20.0,
        })
        mock_db["universities"].documents.append({
            "university_id": "u_no_web",
            "name": "Community College Without Web",
            "country_id": "country_TC",
            "country_iso2": "TC",
            "website": None,
        })

        service = EducationService(mock_db)
        mock_places = ProviderResponse(
            meta=LiveMetadata(status=LiveStatus.FRESH, provider="openstreetmap_overpass", source="https://overpass-api.de"),
            data=[],
        )
        with patch.object(service.places_provider, "get_places", new=AsyncMock(return_value=mock_places)):
            res = await service.get_city_education("city_test_edu")
            inst = res.institutions[0]
            assert inst.has_verified_website is False
            assert inst.website is None

    asyncio.run(run())


def test_healthcare_discovery_categories_and_attribution(mock_db):
    """Verify HealthcareService correctly queries and classifies hospitals, dental clinics, and pharmacies."""
    async def run():
        mock_db["cities"].documents.append({
            "city_id": "city_1356226629",
            "name": "Mumbai",
            "latitude": 19.0760,
            "longitude": 72.8777,
        })

        service = HealthcareService(mock_db)

        places = [
            NormalizedPlaceItem(
                place_id="node_1",
                name="Lilavati Hospital",
                category="hospital",
                latitude=19.0514,
                longitude=72.8290,
                distance_meters=3200.0,
                amenity="hospital",
                tags={
                    "amenity": "hospital",
                    "contact:website": "https://www.lilavatihospital.com",
                    "contact:phone": "+91 22 2675 1000",
                    "emergency": "yes",
                    "addr:street": "Bandra West, Mumbai",
                },
            ),
            NormalizedPlaceItem(
                place_id="node_2",
                name="Smile Dental Clinic",
                category="dentist",
                latitude=19.0600,
                longitude=72.8350,
                distance_meters=2800.0,
                amenity="dentist",
                tags={"amenity": "dentist", "addr:street": "Khar, Mumbai"},
            ),
            NormalizedPlaceItem(
                place_id="node_3",
                name="Noble Chemist",
                category="pharmacy",
                latitude=19.0700,
                longitude=72.8500,
                distance_meters=1200.0,
                amenity="pharmacy",
                tags={"amenity": "pharmacy", "phone": "+91 22 2611 0000", "addr:street": "Santacruz, Mumbai"},
            ),
        ]
        mock_resp = ProviderResponse(
            meta=LiveMetadata(status=LiveStatus.FRESH, provider="openstreetmap_overpass", source="https://overpass-api.de"),
            data=places,
        )

        with patch.object(service.places_provider, "get_places", new=AsyncMock(return_value=mock_resp)):
            res = await service.get_city_healthcare("city_1356226629")
            assert res.total >= 1
            types = [f.type for f in res.facilities]
            assert "Hospital" in types or "Dental Clinic" in types or "Pharmacy" in types

            hosp = next((f for f in res.facilities if "Lilavati" in f.name), None)
            if hosp:
                assert hosp.has_verified_website is True
                assert hosp.website == "https://www.lilavatihospital.com"
                assert hosp.phone == "+91 22 2675 1000"
                assert hosp.emergency is True
                assert "openstreetmap" in hosp.provider.lower()

            assert "OpenStreetMap" in res.disclaimer
            assert "exhaustive" in res.disclaimer

    asyncio.run(run())


def test_education_and_healthcare_api_endpoints():
    """Verify /api/v1/cities/{city_id}/education and /healthcare HTTP endpoints."""
    async def run():
        mock_places = ProviderResponse(
            meta=LiveMetadata(status=LiveStatus.FRESH, provider="openstreetmap_overpass", source="https://overpass-api.de"),
            data=[],
        )
        with patch("app.providers.places.overpass.OverpassPlacesProvider.get_places", new=AsyncMock(return_value=mock_places)):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                edu_resp = await ac.get("/api/v1/cities/city_1356226629/education")
                assert edu_resp.status_code == 200
                edu_json = edu_resp.json()
                assert edu_json["success"] is True
                assert "institutions" in edu_json["data"]
                assert "disclaimer" in edu_json["data"]
                assert "canonical_count" in edu_json["data"]

                health_resp = await ac.get("/api/v1/cities/city_1356226629/healthcare")
                assert health_resp.status_code == 200
                health_json = health_resp.json()
                assert health_json["success"] is True
                assert "facilities" in health_json["data"]
                assert "disclaimer" in health_json["data"]

                aq_resp = await ac.get("/api/v1/cities/city_1356226629/air-quality/live")
                assert aq_resp.status_code == 200
                aq_json = aq_resp.json()
                assert aq_json["success"] is True
                assert "air_quality" in aq_json["data"]
                assert "meta" in aq_json["data"]

    asyncio.run(run())


def test_education_total_greater_than_displayed_limit(mock_db):
    """Verify that when total indexed institutions (e.g. 356) exceeds page limit (e.g. 25), total > displayed_count."""
    async def run():
        mock_db["cities"].documents.append({
            "city_id": "city_mumbai_scale",
            "name": "Mumbai",
            "country_id": "country_IN",
            "country_iso2": "IN",
            "latitude": 19.0760,
            "longitude": 72.8777,
        })

        # Insert 356 universities into country IN
        for idx in range(356):
            mock_db["universities"].documents.append({
                "university_id": f"univ_{idx}",
                "name": f"University {idx:03d} of India",
                "country_id": "country_IN",
                "country_iso2": "IN",
                "website": f"https://www.univ{idx}.edu.in" if idx % 2 == 0 else None,
            })

        service = EducationService(mock_db)
        mock_places = ProviderResponse(
            meta=LiveMetadata(status=LiveStatus.FRESH, provider="openstreetmap_overpass", source="https://overpass-api.de"),
            data=[],
        )
        with patch.object(service.places_provider, "get_places", new=AsyncMock(return_value=mock_places)):
            res = await service.get_city_education("city_mumbai_scale", page=1, page_size=25)

            # Total dataset count must reflect 356, not page size
            assert res.total == 356
            assert res.canonical_count == 356
            assert res.displayed_count == 25
            assert res.total > res.displayed_count
            assert res.limit == 25
            assert res.offset == 0
            assert res.page == 1
            assert len(res.items) == 25
            assert len(res.institutions) == 25
            assert "Showing 25 of 356 indexed institutions" in res.disclaimer

    asyncio.run(run())


def test_education_pagination_metadata(mock_db):
    """Verify pagination metadata: offset, limit, page, and items are exposed correctly."""
    async def run():
        mock_db["cities"].documents.append({
            "city_id": "city_pagination_test",
            "name": "Tokyo",
            "country_id": "country_JP",
            "country_iso2": "JP",
            "latitude": 35.6895,
            "longitude": 139.6917,
        })
        for idx in range(80):
            mock_db["universities"].documents.append({
                "university_id": f"tokyo_u_{idx}",
                "name": f"Tokyo Institute {idx:02d}",
                "country_id": "country_JP",
                "country_iso2": "JP",
                "website": "https://www.tokyo-u.ac.jp",
            })

        service = EducationService(mock_db)
        mock_places = ProviderResponse(
            meta=LiveMetadata(status=LiveStatus.FRESH, provider="openstreetmap_overpass", source="https://overpass-api.de"),
            data=[],
        )
        with patch.object(service.places_provider, "get_places", new=AsyncMock(return_value=mock_places)):
            # Test offset=20, limit=10
            res = await service.get_city_education("city_pagination_test", limit=10, offset=20)
            assert res.total == 80
            assert res.displayed_count == 10
            assert res.limit == 10
            assert res.offset == 20
            assert res.page == 3
            assert len(res.items) == 10
            assert res.items[0].name is not None
            assert res.meta["total"] == 80
            assert res.meta["limit"] == 10
            assert res.meta["offset"] == 20

    asyncio.run(run())


def test_education_mumbai_total_and_university_of_mumbai_prioritization(mock_db):
    """Verify Mumbai education query prioritizes University of Mumbai with official website."""
    async def run():
        mock_db["cities"].documents.append({
            "city_id": "city_mumbai_full",
            "name": "Mumbai",
            "country_id": "country_IN",
            "country_iso2": "IN",
            "latitude": 19.0760,
            "longitude": 72.8777,
        })

        # Add alphabetically earlier universities
        for idx in range(30):
            mock_db["universities"].documents.append({
                "university_id": f"alpha_univ_{idx}",
                "name": f"Aaa Institute {idx}",
                "country_id": "country_IN",
                "country_iso2": "IN",
                "website": "http://www.aaa.ac.in/",
            })

        # Add University of Mumbai (which alphabetically starts with U)
        mock_db["universities"].documents.append({
            "university_id": "university_91d9184fbbc9589f0011",
            "name": "University of Mumbai",
            "country_id": "country_IN",
            "country_iso2": "IN",
            "website": "http://www.mu.ac.in/",
        })

        service = EducationService(mock_db)
        mock_places = ProviderResponse(
            meta=LiveMetadata(status=LiveStatus.FRESH, provider="openstreetmap_overpass", source="https://overpass-api.de"),
            data=[],
        )
        with patch.object(service.places_provider, "get_places", new=AsyncMock(return_value=mock_places)):
            # Even with page_size=10, University of Mumbai must appear in top results due to city prioritization
            res = await service.get_city_education("city_mumbai_full", page=1, page_size=10)
            mu = next((inst for inst in res.items if inst.name == "University of Mumbai"), None)
            assert mu is not None
            assert mu.has_verified_website is True
            assert mu.website == "http://www.mu.ac.in/"
            assert mu.provider == "canonical_db"

    asyncio.run(run())
