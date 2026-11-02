# URBANLENS AI — MONGODB INDEX OPTIMIZATION EXECUTION RESULT

**Date:** November 2, 2026
**Auditor:** UrbanLens Autonomous Database Reliability & Systems Agent
**Database:** `urbanlens` (MongoDB Atlas M0 Free Tier)
**Target Collection:** `healthcare_facilities`
**Operation:** **CONTROLLED DROP OF REDUNDANT INDEX `idx_city_id` (USER AUTHORIZED)**
**Git Status:** **STRICT GIT HOLD OBSERVED — NO STAGING, COMMITTING, OR PUSHING**

---

## 1. Executive Summary & Verification Verdict

Per explicit user authorization, the single-field index `idx_city_id` on MongoDB Atlas collection `healthcare_facilities` was safely and permanently dropped.

All pre-drop safety checks, immediate post-drop verifications, live multi-city healthcare API tests, geospatial queries, and the complete backend test suite passed with **100% success**:

- **Exact Index Dropped:** `healthcare_facilities.idx_city_id` (Key: `[("city_id", 1)]`).
- **Verified Storage Space Reclaimed:** **8.27 MB (8,667,136 bytes)**.
- **Atlas M0 Headroom Expansion:** Headroom increased from **2.16 MB to 10.43 MB (+383% expansion)**.
- **Document Integrity:** Exactly **314,924 healthcare documents** preserved (0 modified, 0 deleted).
- **Referential Integrity:** **0 orphan city references** confirmed via `$lookup` against `cities`.
- **API Parity:** 8 out of 8 key global cities (Mumbai, Dubai, Tokyo, Riyadh, Berlin, London, Sydney, Jakarta) returned **HTTP 200 OK** with unchanged facility counts.
- **Backend Test Suite:** **186/186 pytest tests passed** (0 failures).

---

## 2. Pre-Drop Safety Checks

Prior to issuing the drop command, the automated pipeline verified all preconditions:
1. **Target Database & Collection Confirmed:** Verified connected to `urbanlens.healthcare_facilities`.
2. **Index Key Exact Match:** Confirmed `idx_city_id` existed with key specification `[("city_id", 1)]`.
3. **Compound Index Coverage:** Confirmed `idx_city_type` existed with key specification `[("city_id", 1), ("facility_type", 1)]`.
4. **Zero Application Dependencies:** Verified zero instances of `.hint("idx_city_id")` or index name bindings across the codebase.
5. **Explain Plan Verification:** Confirmed that `idx_city_type` satisfies prefix `{city_id: "..."}` queries with identical key examinations (234 keys for 234 documents) and 0 ms latency.

---

## 3. Before and After Index Inventory

| Index Name | Key Definition | Unique | Status Before | Status After |
|---|---|:---:|:---:|:---:|
| `_id_` | `[('_id', 1)]` | True | Active (6.05 MB) | **Active (6.05 MB)** |
| `uniq_healthcare_id` | `[('healthcare_id', 1)]` | True | Active (12.94 MB) | **Active (12.94 MB)** |
| `idx_city_id` | `[('city_id', 1)]` | False | Active (8.27 MB) | **DROPPED (0 MB)** |
| `idx_country` | `[('country', 1)]` | False | Active (5.23 MB) | **Active (5.23 MB)** |
| `idx_city_type` | `[('city_id', 1), ('facility_type', 1)]` | False | Active (6.71 MB) | **Active (6.71 MB)** |
| `idx_geo_location` | `[('location', '2dsphere')]` | False | Active (8.24 MB) | **Active (8.24 MB)** |
| **Index Count** | — | — | **6 Indexes** | **5 Indexes** |

---

## 4. Atlas Storage Metrics Before and After

Live metrics retrieved via `db.command("dbStats")` and `db.command("collStats", "healthcare_facilities")`:

| Storage Metric | Pre-Drop Value | Post-Drop Value | Delta / Savings |
|---|---|---|---|
| **Collection Total Index Size** | 47.44 MB | **39.17 MB** | **-8.27 MB (-17.4%)** |
| **Database Data Size (`dataSize`)** | 423.04 MB | **423.04 MB** | **0.00 MB (Unchanged)** |
| **Database Total Index Size (`indexSize`)** | 86.79 MB | **78.53 MB** | **-8.27 MB (-9.5%)** |
| **Atlas Quota Usage (`dataSize + indexSize`)** | 509.84 MB | **501.57 MB** | **-8.27 MB** |
| **Atlas M0 Free Tier Storage Ceiling** | 512.00 MB | **512.00 MB** | — |
| **Remaining Atlas M0 Headroom** | **2.16 MB** | **10.43 MB** | **+8.27 MB (+383% Headroom)** |

---

## 5. Post-Drop Healthcare API Regression Test Results

Live HTTP requests executed against running backend on `http://localhost:8000`:

### 1. Multi-City Healthcare Endpoint Verification
- **Mumbai (`city_1356226629`):** HTTP 200 | **234 facilities** | 10 returned
- **Dubai (`city_1784736618`):** HTTP 200 | **661 facilities** | 10 returned
- **Tokyo (`city_1392685764`):** HTTP 200 | **96 facilities** | 10 returned
- **Riyadh (`city_1682999334`):** HTTP 200 | **674 facilities** | 10 returned
- **Berlin (`city_1276451290`):** HTTP 200 | **1,549 facilities** | 10 returned
- **London (`city_1826645935`):** HTTP 200 | **10 facilities** | 10 returned
- **Sydney (`city_1036074917`):** HTTP 200 | **61 facilities** | 10 returned
- **Jakarta (`city_1360771077`):** HTTP 200 | **372 facilities** | 10 returned

### 2. Category & Facility_Type Filtering (Mumbai)
- Category `hospital`: HTTP 200 | 10 returned | Sample: *Khan Bahadur Bhabha Hospital Kurla*
- Category `clinic`: HTTP 200 | 10 returned | Sample: *Agrao*
- Category `pharmacy`: HTTP 200 | 0 returned (honest zero state)

### 3. Pagination & Distance Ordering
- Page 1 IDs vs Page 2 IDs: Disjoint sets, **0 overlapping IDs**. Pagination integrity verified.

### 4. Geospatial Proximity Search (`/api/v1/healthcare/nearby`)
- Parameters: `lat=19.0760&lon=72.8777&radius=5000&page_size=5`
- Status: **HTTP 200 OK** | 5 nearby facilities returned | Sample: *Dr. Anandibai Joshi Maternity Home*
- Proves `idx_geo_location` (`2dsphere`) is 100% operational.

### 5. Facility Detail Lookup (`/api/v1/cities/{id}/healthcare/{fid}`)
- Status: **HTTP 200 OK** | Verified unique ID resolution via `uniq_healthcare_id`.

### 6. Document & Foreign Key Integrity
- **Total Documents in `healthcare_facilities`:** Exactly **314,924** (Expected: 314,924).
- **Orphan City References:** Exactly **0** (Confirmed via aggregation lookup against `cities`).

---

## 6. Pytest Backend Test Suite Results

```bash
pytest tests/ -q
================ 186 passed, 1 warning in 106.08s (0:01:46) ================
```
- **Total Tests:** 186
- **Passed:** **186 (100%)**
- **Failed:** **0**
- **Warnings:** 1 (Starlette testclient deprecation warning)

---

## 7. Known Limitations & Failures

- **Zero Functional Failures:** All queries, endpoints, and test suites passed.
- **Headroom Capacity:** The reclaimed **8.27 MB** expands headroom to **10.43 MB**. This headroom accommodates approximately 7,000 to 10,000 additional clean facilities. If further multi-country expansions exceeding 10,000 documents are planned, upgrading MongoDB Atlas from M0 (512 MB) to M2 (2 GB) or M10 (10 GB) remains the permanent long-term scaling path.

---

## 8. Strict Git Hold Confirmation

Per instructions:
- **No files staged.**
- **No git commits created.**
- **No git push executed.**
- **Working tree remains clean and untouched.**

**The approved index optimization is complete, verified, and ready for your review.**
