# UrbanLens Phase 9 Implementation & Verification Report

**Status:** Complete  
**Date:** 2026-10-29  
**Branch:** `main` (Verified locally, uncommitted as instructed)

---

## 1. Executive Summary

UrbanLens Phase 9 introduces comprehensive relocation intelligence capabilities without compromising data honesty, fabricating values, modifying raw MongoDB data, or altering existing Phase 1–8 architectures:

1. **User Origin + Destination Model:**
   - Origin (relocating FROM) and Destination (considering TO) are first-class concepts throughout UrbanLens.
   - Grounded in an authoritative ISO 3166-1 to ISO 4217 currency registry (`67` national currencies).
   - Backed by an `OriginDestinationContext` in React persisted in `localStorage` (`urbanlens_origin_profile_v1`, default: Mumbai, India `INR` `₹`), ready for seamless swap with future authenticated user profiles without backend refactoring.
   - User-selectable Origin modal with explicit provenance attribution: `"User-selected profile (persisted locally)"`.

2. **Global Two-Tier FX Architecture (ECB Primary + ExchangeRate-API Secondary):**
   - **PRIMARY:** Frankfurter API (European Central Bank reference rates for 31 major currencies).
   - **SECONDARY:** ExchangeRate-API Open Tier (`https://open.er-api.com/v6/latest/{BASE}`) supporting 160+ world currencies including `AED`, `INR`, `JPY`, `GBP`, `SGD`, `USD`, `EUR`, etc.
   - **Fallback Hierarchy:** Primary FX → Secondary FX → Recent cached rate (10 min TTL) → Explicit unavailable.
   - **Provider Provenance:** Every response exposes the exact provider (`frankfurter` vs `exchangerate_api`), status (`fresh`, `cached`, `unavailable`), `base_currency`, `quote_currency`, `rate`, `inverse_rate`, `observed_at`, `fetched_at`, and `source`. Secondary provider is explicitly reported as `exchangerate_api` and never labeled as Frankfurter.
   - **Zero Fabrication:** If both live providers fail and no cache is present, returns honest `status: unavailable`, `rate: null`.

3. **Live AED Validation & Delhi → Dubai Relocation Corridor:**
   - Real live conversions between `INR` and `AED` are fully verified via the live secondary provider:
     - `INR → AED`: Rate `0.03854`, Inverse `25.947068`, Provider `exchangerate_api`, Status `fresh`.
     - `AED → INR`: Rate `25.94721`, Inverse `0.03854`, Provider `exchangerate_api`, Status `fresh`.
     - `USD → AED`: Rate `3.6725`, Inverse `0.272294`, Provider `exchangerate_api`, Status `fresh`.
     - `AED → USD`: Rate `0.272294`, Inverse `3.6725`, Provider `exchangerate_api`, Status `fresh`.
   - Supported Frankfurter currencies continue using the primary provider: e.g. `INR → JPY` (Rate `1.6589`, Provider `frankfurter`), `INR → GBP`, `INR → SGD`.
   - UI for Delhi → Dubai renders a live conversion widget displaying `FROM (Delhi, India - INR)`, `TO (Dubai, UAE - AED)`, `1 INR = 0.0385 AED`, `1 AED = 25.9471 INR`, Provider `exchangerate_api`, Status `LIVE`, and updated timestamp.
   - USD is strictly labeled as `"USD benchmark"`, never as "highest currency".

4. **Education Count Honesty (Total Indexed vs Currently Displayed):**
   - Rigorous distinction between canonical MongoDB dataset size and paginated frontend display:
     - If total in dataset is 356 and display page size is 25 (or 100), the UI displays: **`356 INDEXED INSTITUTIONS` • `Showing 25`** (NOT "25 indexed institutions" or "100 indexed institutions").
   - API response explicitly exposes: `total`, `items`, `displayed_count`, `limit`, `offset`, `page`, `page_size`, `canonical_count`, `community_mapped_count`.
   - Verified across all target cities:
     - **Mumbai:** `356` indexed institutions (Showing 25, Canonical: 356)
     - **Tokyo:** `567` indexed institutions (Showing 25, Canonical: 567)
     - **London:** `169` indexed institutions (Showing 25, Canonical: 169)
     - **Paris:** `263` indexed institutions (Showing 25, Canonical: 263)
     - **New York:** `2,070` indexed institutions (Showing 25, Canonical: 2,070)
     - **Singapore:** `6` indexed institutions (Showing 6, Canonical: 6)
     - **Dubai:** `36` indexed institutions (Showing 25, Canonical: 36)
   - City-specific universities prioritized at the top of results: for Mumbai, `University of Mumbai` (`university_91d9184fbbc9589f0011`) and `Indian Institute of Technology, Bombay` appear in page 1.
   - Verified official website `http://www.mu.ac.in/` is preserved and renders an **"Official Website"** external link chip (`target="_blank"`). Unverified institutions display **"Website unavailable"**. Zero fabricated URLs.

5. **Healthcare Discovery Layer:**
   - Multi-category discovery: Hospitals, Medical Clinics, Dental Clinics, Pharmacies via OpenStreetMap Overpass with structured tag extraction (`phone`, `contact:website`, `emergency`, `opening_hours`, clean street address).
   - Honest attribution disclaimer: `"Showing X community-mapped healthcare locations for [City] from OpenStreetMap. UrbanLens does not claim exhaustive coverage of all medical providers in the municipality."`

6. **Separation of Nominal Currency Translation from Purchasing-Power Cost-of-Living:**
   - Nominal budget translation (e.g. ₹100,000 INR ≈ 3,854 AED) is strictly distinguished from relative cost-of-living purchasing power.

---

## 2. Providers & Data Provenance Hierarchy

| Domain | Primary Live Provider | Secondary Live Provider | Offline / Cache Fallback | Final Fallback | Freshness Indicator |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Currency** | Frankfurter API (ECB reference rates for 31 currencies) | ExchangeRate-API Open Tier (`https://open.er-api.com/v6/latest/{BASE}`) | In-memory TTL Cache (10 min) | Explicit `status: unavailable`, `rate: null` | `fresh` / `cached` / `unavailable` with provider attribution |
| **Air Quality** | OpenAQ API v3 | — | — | WHO Urban Ambient Air Quality Database (MongoDB) | `LIVE` (green) vs `DATABASE` (amber/gray with warning) |
| **Weather** | Open-Meteo API | — | In-memory TTL Cache | Global Weather Observations (MongoDB) | `fresh` / `cached` / `database` |
| **Education** | Canonical World Universities Dataset (MongoDB: 9,350 records) | OpenStreetMap Overpass POIs | — | — | `Canonical Database` vs `Community-mapped (OpenStreetMap)` |
| **Healthcare** | OpenStreetMap Overpass API | — | In-memory POI cache | Explicit disclaimer | `Community-mapped (OpenStreetMap)` |

---

## 3. Relocation Corridors Audited

Live backend checks executed against real providers:

1. **Delhi (`INR`) → Dubai (`AED`):**
   - **Direct Rate:** 1 INR = 0.03854 AED
   - **Inverse Rate:** 1 AED = 25.94721 INR
   - **100,000 INR Budget Translation:** 3,854 AED
   - **Provider:** `exchangerate_api` (Secondary Provider invoked because Frankfurter/ECB does not publish AED)
   - **Status:** `fresh` | **Observed:** 2026-10-29
   - **USD Benchmarks:** 1 INR = $0.010502 USD, 1 AED = $0.272294 USD (3.6725 AED/USD)

2. **Mumbai (`INR`) → Tokyo (`JPY`):**
   - **Direct Rate:** 1 INR = 1.6589 JPY
   - **Inverse Rate:** 1 JPY = 0.602805 INR
   - **100,000 INR Budget Translation:** ¥165,891 JPY
   - **Provider:** `frankfurter` (Primary Provider used for ECB supported pair)
   - **Status:** `fresh`
   - **Education:** 356 Total Indexed, 25 Currently Displayed (University of Mumbai present with official link `http://www.mu.ac.in/`)

3. **Mumbai (`INR`) → London (`GBP`):**
   - **Direct Rate:** 1 INR = 0.007904 GBP
   - **Inverse Rate:** 1 GBP = 126.518 INR
   - **Provider:** `frankfurter` (Primary Provider)
   - **Status:** `fresh`

4. **Mumbai (`INR`) → Singapore (`SGD`):**
   - **Direct Rate:** 1 INR = 0.013465 SGD
   - **Inverse Rate:** 1 SGD = 74.267 INR
   - **Provider:** `frankfurter` (Primary Provider)
   - **Status:** `fresh`

5. **AED → INR (Inverse Corridor):**
   - **Direct Rate:** 1 AED = 25.94721 INR
   - **Provider:** `exchangerate_api`
   - **Status:** `fresh`

---

## 4. Education Dataset Audit: Total Indexed vs Displayed Count

Canonical database totals audited and verified against `/api/v1/cities/{city_id}/education`:

| City | Country | Total Indexed Institutions | Currently Displayed (Page 1) | Canonical Universities | City-Specific Priority Matches |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Mumbai** | India (`IN`) | **356** | 25 | 356 | `University of Mumbai`, `IIT Bombay` |
| **Tokyo** | Japan (`JP`) | **567** | 25 | 567 | `Science University of Tokyo`, `Tokyo College of Music` |
| **London** | United Kingdom (`GB`) | **169** | 25 | 169 | `American InterContinental University - London`, `Birkbeck College` |
| **Paris** | France (`FR`) | **263** | 25 | 263 | `Université Panthéon-Sorbonne (Paris I)`, `American Graduate School in Paris` |
| **New York** | United States (`US`) | **2,070** | 25 | 2,070 | `SUNY Farmingdale`, `SUNY Buffalo`, `CUNY Hunter College` |
| **Singapore** | Singapore (`SG`) | **6** | 6 | 6 | `National University of Singapore`, `SMU`, `Taoist College` |
| **Dubai** | United Arab Emirates (`AE`) | **36** | 25 | 36 | `RIT Dubai`, `Synergy University Dubai`, `American College Of Dubai` |

---

## 5. Verification & Test Suite Summary

### A. Full Pytest Regression Suite
```
Command: python -m pytest -q
Result: 161 passed, 1 warning in 198.21s (100% pass rate)
```
- **Total Tests:** 161 (0 failed, 161 passed)
- **Currency Service Regression Tests (`tests/test_phase9_currency.py` - 11 passed):**
  - `test_currency_registry_coverage` (ISO 3166-1 to ISO 4217 registry)
  - `test_currency_conversion_inr_to_jpy` (Frankfurter primary provider)
  - `test_currency_conversion_usd_to_inr_and_eur_to_gbp` (Major corridors)
  - `test_currency_conversion_cache_fallback` (Two-tier provider failure falling back to cache)
  - `test_currency_conversion_unavailable` (Honest unavailable without fabrication)
  - `test_currency_api_endpoint_convert` (HTTP endpoint contract)
  - `test_currency_api_endpoint_invalid_code` (422 HTTP rejection)
  - `test_currency_conversion_aed_secondary_provider` (INR -> AED using `exchangerate_api`)
  - `test_currency_conversion_aed_to_inr_and_usd_to_aed` (AED -> INR and USD -> AED)
  - `test_currency_fallback_primary_to_secondary` (Fallback from Frankfurter to ExchangeRate-API)
  - `test_currency_secondary_unavailable_and_honest_failure` (Both providers unavailable)
- **Education, AQ & Healthcare Regression Tests (`tests/test_phase9_aq_education_healthcare.py` - 9 passed):**
  - `test_air_quality_live_openaq_response` (Live OpenAQ)
  - `test_air_quality_fallback_who_annual_never_calls_fallback_live` (WHO annual baseline)
  - `test_education_university_of_mumbai_verified_website` (University of Mumbai provenance)
  - `test_education_missing_website_handling` (Missing website handling)
  - `test_healthcare_discovery_categories_and_attribution` (Hospitals, clinics, pharmacies)
  - `test_education_and_healthcare_api_endpoints` (HTTP endpoint routes)
  - `test_education_total_greater_than_displayed_limit` (Total 356 > Displayed 25 honesty)
  - `test_education_pagination_metadata` (Exposing `offset`, `limit`, `page`, `items`)
  - `test_education_mumbai_total_and_university_of_mumbai_prioritization` (City matching)

### B. Frontend Production Build
```
Command: cd frontend && npm run build
Result: ✓ built in 33.76s
TypeScript Compilation: 0 errors, 0 warnings
Vite Bundling: All chunks compiled cleanly
```

### C. Backend API Contract Verification
```
Command: python -m scripts.verify_phase7_api
Result: ALL FRONTEND-BACKEND CONTRACT CHECKS PASSED SUCCESSFULLY!
```

### D. MongoDB Data Consistency Audit
```
Command: python -m scripts.data_consistency_audit
Result: ALL CHECKS VERIFIED (50,250 cities, 9,350 universities, 0 lowercase IDs, 0 orphaned cost mappings)
```

### E. Security Scan
```
Command: git diff -i -G"password|secret|api_key|token|mongodb\+srv|groq_"
Result: Clean. 0 secrets, credentials, API keys, or .env values tracked or exposed in diff.
```

---

## 6. Known Limitations & Recommendations

1. **ExchangeRate-API Open Tier Rate Limits:**
   - The secondary FX provider (`open.er-api.com`) updates once per 24 hours on its open tier. UrbanLens caches responses for 10 minutes to respect rate limits and maximize responsiveness. For enterprise real-time tick-level requirements, a paid API key for Open Exchange Rates or XE can be configured.
2. **Public Overpass Rate Limits:**
   - Community-mapped POIs query the public OpenStreetMap Overpass API within an 8 km radius of city coordinates. Overpass public instances enforce intermittent concurrency rate limits. In-memory caching (TTL 15 min) mitigates this, but an authoritative self-hosted Nominatim/Overpass instance is recommended for massive traffic.
3. **OpenAQ API Key:**
   - When an OpenAQ API key is not configured, the system cleanly and automatically falls back to WHO annual historical database observations with transparent labeling.

---

## 7. Final Assessment

All corrections requested by the user:
1. Two-tier live FX provider hierarchy (`Frankfurter` primary + `ExchangeRate-API` secondary),
2. Live AED validation (`INR ↔ AED`, `USD ↔ AED`) with honest provider provenance,
3. Currency UI with FROM/TO structure, live rates, provider badge, and status,
4. Education count honesty distinguishing total dataset size from displayed page size across all 7 cities,
5. Verified University of Mumbai official website (`http://www.mu.ac.in/`),
6. Comprehensive regression tests (161 passed),
7. Security scan clean with zero uncommitted commits/pushes,

have been completely implemented, verified, tested, and audited.

READY FOR REVIEW
