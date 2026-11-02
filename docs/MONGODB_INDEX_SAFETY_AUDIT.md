# URBANLENS AI — MONGODB INDEX SAFETY INSPECTION & AUDIT REPORT

**Date:** November 2, 2026
**Auditor:** UrbanLens Autonomous Database Reliability & Systems Agent
**Database:** `urbanlens` (MongoDB Atlas M0 Free Tier)
**Target Collection:** `healthcare_facilities` (314,924 documents)
**Inspection Mode:** **STRICTLY READ-ONLY** (No indexes dropped, no documents altered, no schema modified)
**Storage Quota Context:** Atlas M0 Ceiling: **512.00 MB** | Current Usage: **509.84 MB** | Headroom: **2.16 MB**

---

## 1. Executive Summary

This report delivers the results of an empirical, read-only investigation into the index architecture of the `healthcare_facilities` collection in MongoDB Atlas.

The objective was to evaluate whether the single-field index `idx_city_id` is truly redundant to the compound index `idx_city_type`, determine why `$indexStats` recorded 237 accesses for `idx_city_id` versus 0 for `idx_city_type`, measure the exact execution statistics (`executionStats`) across all application query patterns, and calculate the verified storage savings if `idx_city_id` is dropped.

### Key Inspection Findings:
1. **Compound Index Prefix Equivalence Confirmed:** The compound index `idx_city_type` (`{"city_id": 1, "facility_type": 1}`) fully satisfies single-field queries on `{"city_id": "..."}` with **zero execution degradation**. Execution stats demonstrate that querying `{city_id: "..."}` via `idx_city_type` examines **exactly 234 keys for 234 documents (0 ms)**—identical to `idx_city_id`.
2. **Superior Query Coverage of `idx_city_type`:** When filtering by both city and category (e.g., `{"city_id": "...", "facility_type": "hospital"}`), `idx_city_type` examines only **20 keys for 20 documents (0 ms)**, whereas `idx_city_id` is forced to scan **234 keys and 234 documents** to filter `facility_type` in memory.
3. **Index-Covered Sorting:** When sorting by facility type, `idx_city_type` avoids an in-memory `SORT` stage (`['FETCH', 'IXSCAN']`), whereas `idx_city_id` requires a blocking `SORT` stage (`['SORT', 'FETCH', 'IXSCAN']`).
4. **Why `$indexStats` showed 237 vs 0:** When both indexes co-exist, MongoDB's query optimizer evaluates candidate indexes and selects `idx_city_id` for `{city_id: ...}` queries because its key pattern is narrower (1 field vs 2 fields). Without `idx_city_id`, the optimizer automatically routes all `{city_id: ...}` queries to `idx_city_type` with 0 ms latency.
5. **Zero Application Hard-Dependencies:** A complete code audit confirms that **zero application queries use `.hint("idx_city_id")`** or explicitly reference index names.
6. **Verified Storage Savings:** Dropping `idx_city_id` will reclaim **8.27 MB (8,667,136 bytes)**, immediately expanding available Atlas headroom from **2.16 MB to 10.43 MB (+383% headroom increase)** without any performance regression.

---

## 2. Complete Inventory of Current Indexes on `healthcare_facilities`

Data retrieved directly from `col.index_information()`, `db.command("collStats", "healthcare_facilities")`, and `$indexStats`:

| Index Name | Keys & Order | Unique | Size (Bytes) | Size (MB) | Access Count ($indexStats) | Since (Timestamp) |
|---|---|---|---|---|---|---|
| `_id_` | `{"_id": 1}` | True | 6,340,608 | **6.05 MB** | 16 | 2026-11-01 21:58:06.917 UTC |
| `uniq_healthcare_id` | `{"healthcare_id": 1}` | True | 13,570,048 | **12.94 MB** | 13,717 | 2026-11-01 21:58:06.923 UTC |
| `idx_city_id` | `{"city_id": 1}` | False | 8,667,136 | **8.27 MB** | 237 | 2026-11-01 21:58:06.962 UTC |
| `idx_city_type` | `{"city_id": 1, "facility_type": 1}` | False | 7,036,928 | **6.71 MB** | 0 | 2026-11-01 21:58:07.085 UTC |
| `idx_geo_location` | `{"location": "2dsphere"}` | False | 8,642,560 | **8.24 MB** | 122 | 2026-11-01 21:58:07.159 UTC |
| `idx_country` | `{"country": 1}` | False | 5,484,544 | **5.23 MB** | 97 | 2026-11-01 21:58:07.000 UTC |
| **TOTALS** | **6 Indexes** | — | **49,741,824** | **47.44 MB** | **14,189** | — |

---

## 3. Empirical Explain ExecutionStats Comparison

To test real database behavior, identical queries were executed against Mumbai (`city_1356226629`, 234 indexed facilities) comparing the execution profiles under default optimization, forced `idx_city_id`, and forced `idx_city_type`:

### Test Matrix & Results

```
====================================================================================================
Scenario 1: City-Only Query -> col.find({"city_id": "city_1356226629"})
----------------------------------------------------------------------------------------------------
  Mode / Hint              Index Selected   nReturned   keysExamined   docsExamined   execTime  Plan Stages
  Default (Optimizer)      idx_city_id      234         234            234            1 ms      FETCH -> IXSCAN
  Hint("idx_city_id")      idx_city_id      234         234            234            0 ms      FETCH -> IXSCAN
  Hint("idx_city_type")    idx_city_type    234         234            234            0 ms      FETCH -> IXSCAN
  Verdict: EXACT PARITY. idx_city_type examines zero additional keys and incurs 0 ms latency.
====================================================================================================
Scenario 2: City + Category -> col.find({"city_id": "city_1356226629", "facility_type": "hospital"})
----------------------------------------------------------------------------------------------------
  Mode / Hint              Index Selected   nReturned   keysExamined   docsExamined   execTime  Plan Stages
  Default (Optimizer)      idx_city_type    20          20             20             0 ms      FETCH -> IXSCAN
  Hint("idx_city_type")    idx_city_type    20          20             20             0 ms      FETCH -> IXSCAN
  Hint("idx_city_id")      idx_city_id      20          234            234            0 ms      FETCH -> IXSCAN
  Verdict: idx_city_type is 11.7x more efficient (20 vs 234 documents fetched and examined).
====================================================================================================
Scenario 3: Pagination -> col.find({"city_id": ...}).skip(10).limit(25)
----------------------------------------------------------------------------------------------------
  Mode / Hint              Index Selected   nReturned   keysExamined   docsExamined   execTime  Plan Stages
  Hint("idx_city_id")      idx_city_id      25          35             25             0 ms      LIMIT -> FETCH
  Hint("idx_city_type")    idx_city_type    25          35             25             0 ms      LIMIT -> FETCH
  Verdict: EXACT PARITY. Both indexes examine exactly 35 keys to return 25 documents.
====================================================================================================
Scenario 4: Sorting by facility_type -> col.find({"city_id": ...}).sort({"facility_type": 1})
----------------------------------------------------------------------------------------------------
  Mode / Hint              Index Selected   Execution Stages
  Hint("idx_city_id")      idx_city_id      ['SORT', 'FETCH', 'IXSCAN']  (In-memory blocking sort)
  Hint("idx_city_type")    idx_city_type    ['FETCH', 'IXSCAN']          (Covered sort, NO SORT stage)
  Verdict: idx_city_type eliminates in-memory sorting completely.
====================================================================================================
Scenario 5: Geospatial Query -> col.find({"location": {"$nearSphere": ...}}).limit(10)
----------------------------------------------------------------------------------------------------
  Index Selected: idx_geo_location | nReturned: 10 | keysExamined: 30 | docsExamined: 14 | 0 ms
  Verdict: Mandatory for all $nearSphere and geo-distance queries.
====================================================================================================
Scenario 6: Detail Lookup -> col.find({"healthcare_id": "healthcare_43ebaccf73608c82"})
----------------------------------------------------------------------------------------------------
  Index Selected: uniq_healthcare_id | nReturned: 1 | keysExamined: 1 | docsExamined: 1 | 1 ms
  Verdict: Optimal express single-key point lookup.
====================================================================================================
```

---

## 4. Application Query Code Audit

An exhaustive audit of the codebase (`app/services/healthcare.py`, `app/services/places.py`, `app/api/routes/healthcare.py`, and repo models) reveals all query patterns issued against `healthcare_facilities`:

1. **`get_city_healthcare(city_id, category=None)`** (`app/services/healthcare.py:183-193`):
   - Query: `{"city_id": canonical_city_id}`
   - Supported Index: Supported by `idx_city_type` (via prefix scan) and `idx_city_id`.
2. **`get_city_healthcare(city_id, category="hospital")`** (`app/services/healthcare.py:164-183`):
   - Query: `{"city_id": canonical_city_id, "facility_type": clean_cat}`
   - Supported Index: Supported **exclusively** by `idx_city_type`.
3. **`get_city_healthcare(..., search="...")`** (`app/services/healthcare.py:179-183`):
   - Query: `{"city_id": canonical_city_id, "name": {"$regex": ...}}`
   - Supported Index: Supported by `idx_city_type` (via prefix scan) + regex filter.
4. **London / Low-Density City Proximity Fallback** (`app/services/healthcare.py:202-218`):
   - Query: `{"location": {"$nearSphere": ...}}` with optional `"facility_type"` filter.
   - Supported Index: Supported by `idx_geo_location`.
5. **`get_facility_by_id(city_id, healthcare_id)`** (`app/services/healthcare.py:356`):
   - Query: `{"healthcare_id": healthcare_id}`
   - Supported Index: Supported by `uniq_healthcare_id`.
6. **`get_nearby_facilities(lat, lon, radius)`** (`app/services/healthcare.py:386-403`):
   - Query: `{"location": {"$nearSphere": ...}}` with optional `"facility_type"` filter.
   - Supported Index: Supported by `idx_geo_location`.
7. **`PlacesService` Healthcare Fallback** (`app/services/places.py:69-82`, `141-155`):
   - Query: `{"location": {"$nearSphere": ...}, "facility_type": ...}`
   - Supported Index: Supported by `idx_geo_location`.

### Explicit Index Dependency Check:
- **`hint()` references:** **0** across the entire application codebase.
- **Direct index name references:** **0** across all services and repositories.

---

## 5. Comprehensive Index Assessment Table

| Index Name | Size | Accesses | Queries Supported | Safely Removable? | Evidence & Reasoning |
|---|---|---|---|:---:|---|
| **`_id_`** | 6.05 MB | 16 | Primary key lookup, replication, oplog | **NO** | Mandatory engine requirement in MongoDB. Cannot be removed. |
| **`uniq_healthcare_id`** | 12.94 MB | 13,717 | `get_facility_by_id`, ingestion upserts | **NO** | Critical for uniqueness constraint and direct facility endpoint. High production usage. |
| **`idx_geo_location`** | 8.24 MB | 122 | `$nearSphere`, proximity searches | **NO** | Critical for geospatial functionality. Dropping causes `$geoNear` query failure. |
| **`idx_country`** | 5.23 MB | 97 | Country-level grouping & reporting | **NO / KEEP** | Active for country aggregations. Size is modest (5.2 MB). |
| **`idx_city_type`** | 6.71 MB | 0 | `{city_id, facility_type}`, covered sorting, prefix `{city_id}` | **NO — RETAIN AS PRIMARY** | Strictly superior compound index. Satisfies both 2-field filters and 1-field prefix queries. |
| **`idx_city_id`** | 8.27 MB | 237 | `{city_id}` | **YES — SAFELY REMOVABLE** | 100% redundant to compound index `idx_city_type`. Execution stats prove identical keysExamined (234), docsExamined (234), and latency (0 ms). No application query depends on it. |

---

## 6. Storage Savings & Impact Analysis

### Current MongoDB Atlas M0 Status:
- Total Data Size: **423.04 MB**
- Total Index Size: **86.79 MB**
- **Current Total Storage:** **509.84 MB / 512.00 MB**
- **Current Available Headroom:** **2.16 MB (0.42%)**

### If `idx_city_id` is Dropped:
- Space Reclaimed: **8.27 MB**
- New Index Size: **78.52 MB**
- **New Total Storage:** **501.56 MB / 512.00 MB**
- **New Available Headroom:** **10.44 MB (2.04%)**
- **Headroom Gain:** **+383% expansion**

---

## 7. Recommendation & Strict Pre-Execution Hold

### Professional Recommendation:
Dropping `idx_city_id` is **technically safe, zero-risk, and functionally non-breaking**:
1. It does not degrade query performance (0 ms execution time maintained).
2. It does not require any code modifications (MongoDB automatically routes queries to `idx_city_type`).
3. It immediately frees **8.27 MB**, expanding Atlas headroom from **2.16 MB to 10.44 MB**, which is sufficient to ingest approximately 7,000 to 10,000 additional clean facilities without hitting the 512 MB hard ceiling.

### Status:
**Per instructions, NO DATABASE MODIFICATIONS HAVE BEEN PERFORMED. This report is submitted for your explicit review and approval.**
