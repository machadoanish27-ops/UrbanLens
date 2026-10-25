# UrbanLens

**Source-Grounded City Intelligence Platform**

UrbanLens is an enterprise-grade urban intelligence platform that aggregates, normalizes, and synthesizes multi-dimensional city data across geographic, meteorological, environmental, economic, academic, and civic infrastructure domains. Designed with a strict commitment to data provenance and anti-hallucination principles, UrbanLens grounds all insights in validated datasets and official observation records.

---

## Overview

Modern municipal decision-making and cross-city research require accurate, transparent data. Many AI and analytics tools fabricate or average incompatible municipal statistics. UrbanLens solves this by maintaining a strict source-grounded foundation:

- **Canonical Identity System:** Every city is anchored to a unique, immutable `city_id`. Provider-specific IDs (e.g., weather stations, census codes) remain strictly namespaced.
- **Strict Non-Fabrication:** Missing values are explicitly flagged as unavailable. Statistical metrics from incompatible collection methodologies (e.g., satellite vs. ground station air quality) are never silently blended or averaged.
- **Seven-Agent Architecture:** Modular intelligence agents analyze specific urban dimensions before synthesizing an aggregated city intelligence assessment.
- **RAG-Ready Engine:** Built with clean interfaces ready for Large Language Model (LLM) reasoning and semantic retrieval without premature vector database bloat.

---

## Features

- **FastAPI Core Engine:** High-performance, asynchronous REST API with OpenAPI `/docs` and `/redoc` documentation.
- **MongoDB Atlas Integration:** Production-ready client layer with connection pooling, timeout resiliency, TLS certificate support (`certifi`), and safe diagnostic health checks.
- **Comprehensive City Endpoints:** Search, filter, and retrieve comprehensive city profiles, administrative boundaries, aliases, and provider mappings.
- **Meteorological & Climate Intelligence:** Ground-truth weather observations and official World Meteorological Organization (WMO) forecasts.
- **Uncompromised Air Quality:** Independent tracking for both Global Weather observational air quality and World Health Organization (WHO) annual municipal monitoring.
- **Cost of Living Benchmarks:** Grounded consumer price indices, grocery baskets, and residential rental metrics.
- **Higher Education Ecosystem:** Catalog of accredited universities paired with global ranking histories (QS, THE).
- **Multi-Agent Orchestrator:** Coordinated execution across all seven specialized intelligence agents with aggregated scoring.
- **Traceability & Provenance:** Request tracing with `X-Request-ID`, execution timing (`X-Process-Time-MS`), and per-datapoint source metadata.

---

## Architecture

UrbanLens enforces a clear separation of concerns across presentation, domain, and data layers:

```text
                  HTTP Client / Agent Frontends
                              │
                      [FastAPI Routers]
                 (Cities, Countries, Data, Agents)
                              │
                     [Service Layer]
              (Business logic, Provenance, Fallbacks)
                              │
                     [Multi-Agent Orchestrator]
       ┌──────────────────────┬──────────────────────┐
 LocationAgent         EnvironmentAgent        CostAgent ...
       └──────────────────────┴──────────────────────┘
                              │
                    [Repository Layer]
           (BaseRepository, Typed Entity Queries)
                              │
                     [MongoDB Client]
             (Connection Pooling, PyMongo, Atlas)
                              │
                    [(MongoDB Database)]
  cities, countries, weather, air_quality, cost, universities...
```

---

## Technology Stack

- **Runtime:** Python 3.11+
- **Web Framework:** FastAPI (v0.115+)
- **ASGI Server:** Uvicorn (v0.30+)
- **Database Driver:** PyMongo (v4.9+) with `certifi` TLS support
- **Schema Validation & Settings:** Pydantic (v2.0+) & Pydantic Settings
- **Testing:** Pytest (v8.0+) & FastAPI TestClient / HTTPX

---

## Backend

The backend is built around clean architectural patterns:
- **`app/core/`**: Configuration via Pydantic `BaseSettings`, structured secret-scrubbing logger, custom domain exceptions, and global HTTP exception handlers.
- **`app/db/`**: Thread-safe `MongoClientManager` singleton with safe `/health/db` health check, index synchronization (`indexes.py`), and typed repositories in `app/db/repositories/`.
- **`app/schemas/`**: Pydantic models for request bodies, data payloads, pagination metadata, provenance objects, and standardized `ApiResponse[T]` wrappers.
- **`app/services/`**: Orchestrates repository queries, validates data availability, enforces fallback hierarchies, and computes domain summaries.
- **`app/agents/`**: Modular implementations of the seven domain agents inheriting from `BaseAgent`.
- **`app/orchestrator/`**: Manages multi-agent execution context, parallel agent calls, and aggregated intelligence synthesis.
- **`app/api/`**: Modular versioned routers under `/api/v1` and core diagnostic endpoints under `/health`.

---

## MongoDB

### Collections
The UrbanLens MongoDB database contains validated canonical collections:

| Collection Name | Description | Key Indexes |
|-----------------|-------------|-------------|
| `cities` | Master city registry with demographics and coordinates | `city_id` (unique), `worldcities_id` (unique), `country_iso2` |
| `city_aliases` | Alternate names, historic names, and local spellings | `(city_id, normalized_alias)` (unique) |
| `city_provider_identities` | External provider cross-reference IDs | `(provider, provider_location_id)` (unique), `city_id` |
| `countries` | Master country registry and ISO codes | `country_id` (unique), `iso2` (unique), `iso3` (unique) |
| `country_metrics` | National socioeconomic and development indicators | `(country_id, metric, period)` (unique) |
| `gdp_country_metrics` | World Bank / macroeconomic GDP indicators | `(country_id, metric, period)` (unique) |
| `weather_observations` | Ground-truth historical and recent observations | `(city_id, provider, observed_at, source_row)` (unique) |
| `weather_forecasts_wmo` | Forward-looking meteorological forecasts | `(city_id, provider, forecast_for)` (unique) |
| `air_quality_observations_global_weather` | Multi-pollutant observational AQ index | `(city_id, provider, observed_at, source_row)` (unique) |
| `air_quality_observations_who` | WHO annual mean particulate monitoring | `(city_id, source, year, source_row)` (unique) |
| `cost_of_living` | Standardized consumer expense baskets | `(city_id, metric, observed_at, source_id)` |
| `universities` | Academic institution directory | `university_id` (unique), `(country_iso2, name)` |
| `university_rankings` | Historical QS & Times Higher Education rankings | `(university_id, ranking_metric, ranking_year)` |
| `source_registry` | Provenance registry tracking upstream files | `source_id` (unique) |

---

## Dataset Overview

The authoritative local dataset is stored under `data/`:
- **`data/canonical/`**: Cleaned, verified CSVs ready for database sync.
- **`data/mappings/`**: Alias resolution tables and provider cross-references.
- **`data/quarantine/`**: Out-of-bounds or ambiguous rows isolated to prevent polluting canonical collections.
- **`data/reports/`**: Audit manifests, index definitions, and validation logs.

---

## Data Provenance

All observations and metrics in UrbanLens maintain explicit grounding:
```json
{
  "source_id": "weather_observations",
  "provider": "global_weather",
  "observed_at": "2026-10-25T12:00:00Z",
  "source_row": 142
}
```
If an observation is older than its configured TTL, the data freshness classifier tags the record as `stale`. If no verified data exists for a city, the platform returns an explicit `DATA_UNAVAILABLE` response rather than guessing or fabricating numbers.

---

## API Endpoints

### Health & Diagnostics
- `GET /health`: Core application liveness and version info.
- `GET /health/db`: MongoDB connectivity check and latency (secrets scrubbed).

### Cities
- `GET /api/v1/cities`: Paginated city search with query, population, and country filters.
- `GET /api/v1/cities/{city_id}`: City profile with aliases and provider identities.
- `GET /api/v1/cities/{city_id}/overview`: Multidimensional snapshot across weather, air quality, economics, and academics.

### Countries
- `GET /api/v1/countries`: List countries with continent filtering.
- `GET /api/v1/countries/{country_id}`: Detailed country record.
- `GET /api/v1/countries/{country_id}/metrics`: Socioeconomic and GDP metrics.

### Meteorological & Air Quality
- `GET /api/v1/cities/{city_id}/weather`: Latest weather observation and historical records.
- `GET /api/v1/cities/{city_id}/weather/forecast`: Official WMO weather forecast entries.
- `GET /api/v1/cities/{city_id}/air-quality`: Ground-truth Global Weather AQ and WHO annual monitoring datasets (unmixed).

### Cost of Living
- `GET /api/v1/cities/{city_id}/cost-of-living`: Consumer price metrics and residential rental indices.

### Universities & Rankings
- `GET /api/v1/cities/{city_id}/universities`: Higher education institutions associated with the city's regional context.
- `GET /api/v1/universities/{university_id}`: Institution details and ranking history.
- `GET /api/v1/universities/{university_id}/rankings`: Historical ranking trends.

### Intelligence & Multi-Agent Orchestration
- `GET /api/v1/intelligence/agents`: Catalog and operational status of all 7 agents.
- `POST /api/v1/intelligence/query`: Dispatch multi-agent query for a city with targeted or full domain analysis.
- `GET /api/v1/cities/{city_id}/intelligence`: Convenience endpoint synthesizing all 7 agents for a city.

---

## Agent Architecture

UrbanLens organizes urban intelligence into seven distinct domain agents inheriting from `BaseAgent`:

1. **`LocationAgent` (City Identity):** Verified coordinates, administrative levels, aliases, and provider mapping.
2. **`EnvironmentAgent` (Climate & Air):** Weather observations, WMO forecasts, and air pollution metrics.
3. **`MobilityAgent` (Transit & Infrastructure):** Metropolitan scale classification and transit connectivity indicators.
4. **`CostAgent` (Budget & Cost of Living):** Consumer basket pricing and living expense metrics.
5. **`AccommodationAgent` (Housing & Locality):** Residential rental metrics, center vs. suburban price ratios.
6. **`EducationLifestyleAgent` (Academics & Culture):** Higher education institutions and global academic rankings.
7. **`SafetyHealthcareAgent` (Civic Essentials):** Particulate thresholds against WHO safety baselines and public health metrics.

---

## Project Structure

```text
UrbanLens/
├── app/
│   ├── main.py                     # FastAPI application setup and middleware
│   ├── core/                       # Config, secret-scrubbing logger, exceptions
│   ├── db/                         # MongoDB client singleton, index definitions
│   │   └── repositories/           # Typed repositories (city, country, weather, etc.)
│   ├── models/                     # Domain dataclasses and agent contracts
│   ├── schemas/                    # Pydantic request/response schemas
│   ├── services/                   # Business logic and domain services
│   ├── agents/                     # The 7 modular domain agents
│   ├── orchestrator/               # Multi-agent orchestrator, context, and result
│   ├── api/
│   │   └── routes/                 # FastAPI router modules
│   └── utils/                      # Provenance and data freshness utilities
├── data/
│   ├── canonical/                  # Authoritative cleaned CSV datasets
│   ├── mappings/                   # City aliases and provider identities
│   ├── quarantine/                 # Isolated non-canonical/ambiguous rows
│   └── reports/                    # Manifests, audit reports, and index specs
├── etl/                            # Resumable, idempotent MongoDB ETL
├── scripts/                        # Data and MongoDB audit scripts
├── tests/                          # Full pytest test suite
├── docs/                           # Architectural and operational documentation
├── requirements.txt                # Production dependencies
├── pyproject.toml                  # Project packaging and pytest configuration
├── .env.example                    # Environment configuration template
├── .gitignore                      # Git ignore protecting secrets and caches
├── LICENSE                         # MIT Software License
└── README.md                       # Master platform documentation
```

---

## Environment Setup

### Prerequisites
- Python 3.11 or higher
- MongoDB Atlas cluster or local MongoDB instance (optional for test execution)

### 1. Clone & Set Up Virtual Environment
```powershell
git clone <repository-url> UrbanLens
cd UrbanLens
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Install Dependencies
```powershell
pip install -r requirements.txt
pip install pytest httpx
```

### 3. Configure Environment Variables
Copy `.env.example` to `.env`:
```powershell
Copy-Item .env.example .env
```
Edit `.env` with your MongoDB credentials:
```env
MONGODB_URI=mongodb+srv://<username>:<password>@<cluster-url>/urbanlens
MONGODB_DB=urbanlens
ENVIRONMENT=development
DEBUG=false
```
> [!CAUTION]
> Never commit `.env` or paste real credentials into code. `.env` is protected by `.gitignore`.

---

## Local Development & Running the API

Start the backend API with live reload:
```powershell
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Access the interactive API documentation:
- **Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **Health Check:** [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

## Testing

Run the automated test suite with `pytest`:
```powershell
python -m pytest -v
```

The test suite covers:
- Core application lifecycle and middleware headers (`X-Request-ID`, `X-Process-Time-MS`).
- Health endpoints (`/health` and `/health/db`).
- City, Country, Weather, Air Quality, Cost, and University API routes.
- Error handling, 404 responses, and pagination parameter bounds.
- Individual unit tests for each of the 7 modular domain agents.
- Orchestrator multi-agent synthesis and grounding.
- Data validation and ETL preflight key safety checks.

---

## MongoDB Configuration & ETL

To verify your MongoDB connection and collection counts:
```powershell
python scripts/validate_mongodb.py
```

To run or resume the idempotent ETL importer:
```powershell
python import_mongodb.py
```
> [!NOTE]
> The ETL operates with strict `$setOnInsert` and upsert rules, never drops collections, and checkpoints progress.

---

## GitHub Development Workflow

1. Always branch from `main`:
   ```powershell
   git checkout -b feature/your-feature-name
   ```
2. Run tests before committing:
   ```powershell
   python -m pytest -q
   ```
3. Commit with semantic messages:
   ```powershell
   git commit -m "feat(api): add multi-agent intelligence query endpoint"
   ```

---

## Data Licensing & Attribution

> [!IMPORTANT]
> The open-source software license for the UrbanLens code does **not** automatically apply to ingested third-party datasets. Upstream data sources retain their respective licenses and attribution requirements:

- **World Cities Database:** Used under SimpleMaps open license terms.
- **World Meteorological Organization (WMO):** Official public forecasts.
- **World Health Organization (WHO):** Ambient air quality database; attribution required per WHO guidelines.
- **Cost of Living Dataset:** Aggregated crowd-sourced and municipal consumer price benchmarks; requires upstream verification.
- **University Rankings:** Academic metric publications (QS / THE); informational and educational reference use.

*Third-party dataset licenses that are not explicitly documented are marked as requiring verification.*

---

## Software License

The **UrbanLens source code, tooling, and application framework** are licensed under the **[MIT License](LICENSE)**.

---

## Future Roadmap

- [ ] **Live Provider Connectors:** Dynamic integration of real-time GTFS feeds and OpenWeather/AirNow live APIs.
- [ ] **LLM Grounding / RAG Integration:** Seamlessly feed multi-agent grounded outputs into Gemini / LLM models for natural language explanations.
- [ ] **City Comparison Matrix:** Multi-city side-by-side benchmarking endpoint (`/api/v1/compare`).
- [ ] **Geospatial GeoJSON Polygons:** Adding full administrative boundaries to city detail responses.
