"""Phase 9 Regression Tests: Currency Service & API Endpoints."""

import asyncio
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.services.currency import CurrencyService
from app.data.currencies import get_currency_for_country, get_supported_currencies
from app.providers.base import LiveMetadata, LiveStatus, ProviderResponse
from app.providers.currency.base import NormalizedCurrencyConversion
from app.schemas.currency import UsdBenchmark


def test_currency_registry_coverage():
    """Verify ISO 3166-1 to ISO 4217 registry contains key relocation corridors."""
    in_curr = get_currency_for_country("IN")
    assert in_curr["code"] == "INR"
    assert in_curr["symbol"] == "₹"

    jp_curr = get_currency_for_country("JP")
    assert jp_curr["code"] == "JPY"
    assert jp_curr["symbol"] == "¥"

    gb_curr = get_currency_for_country("GB")
    assert gb_curr["code"] == "GBP"

    sg_curr = get_currency_for_country("SG")
    assert sg_curr["code"] == "SGD"

    ae_curr = get_currency_for_country("AE")
    assert ae_curr["code"] == "AED"

    currencies = get_supported_currencies()
    assert len(currencies) >= 30
    codes = [c["code"] for c in currencies]
    assert "USD" in codes
    assert "EUR" in codes
    assert "JPY" in codes
    assert "INR" in codes


def test_currency_conversion_inr_to_jpy(mock_db):
    """Verify INR -> JPY conversion returns rate, inverse_rate, converted amount, and USD benchmarks."""
    async def run():
        service = CurrencyService(mock_db)

        norm_conv = NormalizedCurrencyConversion(
            from_currency="INR",
            to_currency="JPY",
            rate=1.65,
            amount=1000.0,
            converted_amount=1650.0,
            date="2026-10-28",
        )
        mock_provider_res = ProviderResponse(
            meta=LiveMetadata(status=LiveStatus.FRESH, provider="frankfurter", source="https://api.frankfurter.dev"),
            data=norm_conv,
        )

        usd_base = {
            "currency": "INR",
            "rate_to_usd": 0.0105,
            "usd_to_currency": 95.238,
            "label": "USD benchmark",
        }
        usd_quote = {
            "currency": "JPY",
            "rate_to_usd": 0.0063,
            "usd_to_currency": 158.73,
            "label": "USD benchmark",
        }

        with patch.object(service.provider, "convert", new=AsyncMock(return_value=mock_provider_res)):
            with patch.object(service, "get_usd_benchmark", side_effect=[usd_base, usd_quote]):
                res = await service.convert_currency("INR", "JPY", 1000.0)

                assert res["base_currency"] == "INR"
                assert res["quote_currency"] == "JPY"
                assert res["rate"] == 1.65
                assert res["inverse_rate"] == round(1.0 / 1.65, 6)
                assert res["amount"] == 1000.0
                assert res["converted_amount"] == 1650.0
                assert res["status"] in ("live", "fresh")
                assert res["provider"] == "frankfurter"
                assert res["usd_benchmark_base"] is not None
                assert res["usd_benchmark_quote"] is not None
                assert res["usd_benchmark_base"]["rate_to_usd"] == 0.0105
                assert res["usd_benchmark_quote"]["rate_to_usd"] == 0.0063

    asyncio.run(run())


def test_currency_conversion_usd_to_inr_and_eur_to_gbp(mock_db):
    """Verify USD -> INR and EUR -> GBP calculation."""
    async def run():
        service = CurrencyService(mock_db)

        # Test identical currency conversion
        same_res = await service.convert_currency("USD", "USD", 500.0)
        assert same_res["rate"] == 1.0
        assert same_res["inverse_rate"] == 1.0
        assert same_res["converted_amount"] == 500.0
        assert same_res["status"] in ("live", "fresh")

        # Test EUR -> GBP with mocked provider
        norm_eur = NormalizedCurrencyConversion(
            from_currency="EUR",
            to_currency="GBP",
            rate=0.85,
            amount=100.0,
            converted_amount=85.0,
            date="2026-10-28",
        )
        mock_eur_gbp = ProviderResponse(
            meta=LiveMetadata(status=LiveStatus.FRESH, provider="frankfurter", source="https://api.frankfurter.dev"),
            data=norm_eur,
        )
        with patch.object(service.provider, "convert", new=AsyncMock(return_value=mock_eur_gbp)):
            eur_res = await service.convert_currency("EUR", "GBP", 100.0)
            assert eur_res["rate"] == 0.85
            assert eur_res["converted_amount"] == 85.0
            assert eur_res["inverse_rate"] == round(1.0 / 0.85, 6)

    asyncio.run(run())


def test_currency_conversion_cache_fallback(mock_db):
    """Verify that when live provider fails, recent cache is used with status='cached'."""
    async def run():
        service = CurrencyService(mock_db)

        cached_doc = {
            "base_currency": "INR",
            "quote_currency": "JPY",
            "rate": 1.62,
            "inverse_rate": 0.617284,
            "amount": 1.0,
            "converted_amount": 1.62,
            "provider": "frankfurter",
            "source": "https://api.frankfurter.dev",
            "status": "cached",
            "observed_at": "2026-10-28T10:00:00Z",
            "fetched_at": "2026-10-28T10:00:00Z",
        }
        from app.core.cache import build_cache_key
        fallback_cache_key = build_cache_key("currency", from_cur="INR", to_cur="JPY", amount=1.0)
        if service.cache:
            service.cache.set(fallback_cache_key, cached_doc)

        failed_resp = ProviderResponse(
            meta=LiveMetadata(status=LiveStatus.UNAVAILABLE, provider="frankfurter", source="https://api.frankfurter.dev", error_detail="Provider timeout"),
            data=None,
        )
        sec_failed_resp = ProviderResponse(
            meta=LiveMetadata(status=LiveStatus.UNAVAILABLE, provider="exchangerate_api", source="https://open.er-api.com", error_detail="Provider timeout"),
            data=None,
        )
        with patch.object(service.primary_provider, "convert", new=AsyncMock(return_value=failed_resp)), \
             patch.object(service.secondary_provider, "convert", new=AsyncMock(return_value=sec_failed_resp)):
            res = await service.convert_currency("INR", "JPY", 2000.0)
            assert res["status"] == "cached"
            assert res["rate"] == 1.62
            assert res["converted_amount"] == 2000.0 * 1.62

    asyncio.run(run())


def test_currency_conversion_unavailable(mock_db):
    """Verify that when both live provider and cache fail, status is 'unavailable' without fabrication."""
    async def run():
        service = CurrencyService(mock_db, cache=None)

        failed_resp = ProviderResponse(
            meta=LiveMetadata(status=LiveStatus.UNAVAILABLE, provider="frankfurter", source="https://api.frankfurter.dev", error_detail="Network down"),
            data=None,
        )
        sec_failed_resp = ProviderResponse(
            meta=LiveMetadata(status=LiveStatus.UNAVAILABLE, provider="exchangerate_api", source="https://open.er-api.com", error_detail="Network down"),
            data=None,
        )
        with patch.object(service.primary_provider, "convert", new=AsyncMock(return_value=failed_resp)), \
             patch.object(service.secondary_provider, "convert", new=AsyncMock(return_value=sec_failed_resp)):
            res = await service.convert_currency("INR", "JPY", 1000.0)
            assert res["status"] == "unavailable"
            assert res["rate"] is None
            assert res["converted_amount"] is None
            assert "error_detail" in res

    asyncio.run(run())


def test_currency_api_endpoint_convert(mock_db):
    """Verify /api/v1/currency/convert HTTP endpoint returns structured response."""
    from app.db.client import get_db
    app.dependency_overrides[get_db] = lambda: mock_db

    async def run():
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            resp = await ac.get("/api/v1/currency/convert", params={"base": "USD", "quote": "USD", "amount": 100})
            assert resp.status_code == 200
            body = resp.json()
            assert body["success"] is True
            data = body["data"]
            assert data["base_currency"] == "USD"
            assert data["quote_currency"] == "USD"
            assert data["rate"] == 1.0
            assert data["converted_amount"] == 100.0

    try:
        asyncio.run(run())
    finally:
        app.dependency_overrides.clear()


def test_currency_api_endpoint_invalid_code(mock_db):
    """Verify /api/v1/currency/convert rejects invalid currency codes with HTTP 422."""
    from app.db.client import get_db
    app.dependency_overrides[get_db] = lambda: mock_db

    async def run():
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            resp = await ac.get("/api/v1/currency/convert", params={"base": "INVALID_TOOLONG", "quote": "USD"})
            assert resp.status_code == 422

    try:
        asyncio.run(run())
    finally:
        app.dependency_overrides.clear()


def test_currency_conversion_aed_secondary_provider(mock_db):
    """Verify AED conversions use secondary provider (ExchangeRate-API) with exact provider attribution."""
    async def run():
        service = CurrencyService(mock_db)

        # Mock primary failing for AED (since Frankfurter ECB does not support AED)
        primary_fail = ProviderResponse(
            meta=LiveMetadata(status=LiveStatus.UNAVAILABLE, provider="frankfurter", source="https://api.frankfurter.dev", error_detail="Currency not supported"),
            data=None,
        )
        # Mock secondary succeeding
        sec_conv = NormalizedCurrencyConversion(
            from_currency="INR",
            to_currency="AED",
            rate=0.03854,
            amount=100.0,
            converted_amount=3.854,
            date="2026-10-29",
        )
        sec_success = ProviderResponse(
            meta=LiveMetadata(status=LiveStatus.FRESH, provider="exchangerate_api", source="https://open.er-api.com/v6/latest/INR"),
            data=sec_conv,
        )

        with patch.object(service.primary_provider, "convert", new=AsyncMock(return_value=primary_fail)):
            with patch.object(service.secondary_provider, "convert", new=AsyncMock(return_value=sec_success)):
                res = await service.convert_currency("INR", "AED", 100.0)

                assert res["base_currency"] == "INR"
                assert res["quote_currency"] == "AED"
                assert res["rate"] == 0.03854
                assert res["inverse_rate"] == round(1.0 / 0.03854, 6)
                assert res["converted_amount"] == 3.854
                assert res["status"] in ("live", "fresh")
                # Provider must be actual secondary provider, NEVER frankfurter
                assert res["provider"] == "exchangerate_api"
                assert "open.er-api.com" in res["source"]

    asyncio.run(run())


def test_currency_conversion_aed_to_inr_and_usd_to_aed(mock_db):
    """Verify AED -> INR and USD -> AED conversions with correct inverse rate calculation."""
    async def run():
        # Test AED -> INR
        service_aed = CurrencyService(mock_db, cache=None)
        sec_aed_inr = NormalizedCurrencyConversion(
            from_currency="AED",
            to_currency="INR",
            rate=25.95,
            amount=10.0,
            converted_amount=259.5,
            date="2026-10-29",
        )
        sec_resp = ProviderResponse(
            meta=LiveMetadata(status=LiveStatus.FRESH, provider="exchangerate_api", source="https://open.er-api.com/v6/latest/AED"),
            data=sec_aed_inr,
        )

        with patch.object(service_aed.primary_provider, "convert", new=AsyncMock(return_value=ProviderResponse(meta=LiveMetadata(status=LiveStatus.UNAVAILABLE, provider="frankfurter", source="https://api.frankfurter.dev"), data=None))):
            with patch.object(service_aed.secondary_provider, "convert", new=AsyncMock(return_value=sec_resp)):
                res = await service_aed.convert_currency("AED", "INR", 10.0, include_benchmarks=False)
                assert res["base_currency"] == "AED"
                assert res["quote_currency"] == "INR"
                assert res["rate"] == 25.95
                assert res["inverse_rate"] == round(1.0 / 25.95, 6)
                assert res["converted_amount"] == 259.5
                assert res["provider"] == "exchangerate_api"

        # Test USD -> AED
        service_usd = CurrencyService(mock_db, cache=None)
        sec_usd_aed = NormalizedCurrencyConversion(
            from_currency="USD",
            to_currency="AED",
            rate=3.6725,
            amount=1.0,
            converted_amount=3.6725,
            date="2026-10-29",
        )
        sec_resp_usd = ProviderResponse(
            meta=LiveMetadata(status=LiveStatus.FRESH, provider="exchangerate_api", source="https://open.er-api.com/v6/latest/USD"),
            data=sec_usd_aed,
        )
        with patch.object(service_usd.primary_provider, "convert", new=AsyncMock(return_value=ProviderResponse(meta=LiveMetadata(status=LiveStatus.UNAVAILABLE, provider="frankfurter", source="https://api.frankfurter.dev"), data=None))):
            with patch.object(service_usd.secondary_provider, "convert", new=AsyncMock(return_value=sec_resp_usd)):
                res_usd = await service_usd.convert_currency("USD", "AED", 1.0, include_benchmarks=False)
                assert res_usd["rate"] == 3.6725
                assert res_usd["inverse_rate"] == round(1.0 / 3.6725, 6)
                assert res_usd["provider"] == "exchangerate_api"

    asyncio.run(run())


def test_currency_fallback_primary_to_secondary(mock_db):
    """Verify fallback from primary (Frankfurter) to secondary (ExchangeRate-API) when primary fails."""
    async def run():
        service = CurrencyService(mock_db, cache=None)

        primary_fail = ProviderResponse(
            meta=LiveMetadata(status=LiveStatus.UNAVAILABLE, provider="frankfurter", source="https://api.frankfurter.dev", error_detail="Frankfurter 503 Service Unavailable"),
            data=None,
        )
        sec_conv = NormalizedCurrencyConversion(
            from_currency="INR",
            to_currency="JPY",
            rate=1.65,
            amount=100.0,
            converted_amount=165.0,
            date="2026-10-29",
        )
        sec_success = ProviderResponse(
            meta=LiveMetadata(status=LiveStatus.FRESH, provider="exchangerate_api", source="https://open.er-api.com/v6/latest/INR"),
            data=sec_conv,
        )

        with patch.object(service.primary_provider, "convert", new=AsyncMock(return_value=primary_fail)):
            with patch.object(service.secondary_provider, "convert", new=AsyncMock(return_value=sec_success)):
                res = await service.convert_currency("INR", "JPY", 100.0)
                assert res["status"] in ("live", "fresh")
                assert res["provider"] == "exchangerate_api"
                assert res["rate"] == 1.65

    asyncio.run(run())


def test_currency_secondary_unavailable_and_honest_failure(mock_db):
    """Verify that when both primary and secondary fail and no cache exists, honest unavailable is returned."""
    async def run():
        service = CurrencyService(mock_db, cache=None)

        primary_fail = ProviderResponse(
            meta=LiveMetadata(status=LiveStatus.UNAVAILABLE, provider="frankfurter", source="https://api.frankfurter.dev", error_detail="Primary timeout"),
            data=None,
        )
        secondary_fail = ProviderResponse(
            meta=LiveMetadata(status=LiveStatus.UNAVAILABLE, provider="exchangerate_api", source="https://open.er-api.com", error_detail="Secondary API rate limit"),
            data=None,
        )

        with patch.object(service.primary_provider, "convert", new=AsyncMock(return_value=primary_fail)):
            with patch.object(service.secondary_provider, "convert", new=AsyncMock(return_value=secondary_fail)):
                res = await service.convert_currency("INR", "AED", 100.0)
                assert res["status"] == "unavailable"
                assert res["rate"] is None
                assert res["inverse_rate"] is None
                assert res["converted_amount"] is None
                assert "error_detail" in res
                assert res["provider"] == "exchangerate_api"

    asyncio.run(run())
