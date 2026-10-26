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

# Live Intelligence Providers
OPENAQ_API_KEY=your_openaq_api_key_here
```
> [!CAUTION]
> Never commit `.env` or paste real credentials into code. `.env` is protected by `.gitignore`.

---

## Live Intelligence Provider Layer

UrbanLens integrates live, external data feeds through a strict, decoupled service architecture:

```text
       Agent (Domain Intelligence)
                   │
                   ▼
          UrbanLens Service
       (Fallback, Data Mediation)
                   │
                   ▼
            Provider Adapter
        (Typed External Adapter)
                   │
                   ▼
              External API
    (Open-Meteo, OpenAQ, Nominatim...)
                   │
                   ▼
        Normalized UrbanLens Schema
                   │
                   ▼
     Provenance + Timestamps + Status
                   │
                   ▼
          Agent / Orchestrator
```

### Provider Architectural Invariants

1. **Agents never call external providers directly:** All live interactions are mediated through UrbanLens services (`WeatherService`, `AirQualityService`, `CurrencyService`, `GeocodingService`, `RoutingService`, `PlacesService`, `TransitService`).
2. **Providers are replaceable:** Each provider implements a typed abstract base class inheriting from `BaseProvider`.
3. **No fabricated confidence scores:** Confidence values are reported only when natively supplied by the upstream provider.
4. **Never disguise stale data as live:** If an external provider fails and the service falls back to MongoDB ground-truth observations, the status is explicitly set to `database`, and the original observation timestamp is preserved.

### Fallback Hierarchy

When a service requests live intelligence for an urban domain:
1. **Fresh live provider:** Query active external provider adapter.
2. **Fresh cache:** (Clean architectural extension point for upcoming caching layers).
3. **Canonical database observation:** If the live provider is unreachable, times out, or reports errors, fallback to verified MongoDB historical ground-truth observations (`status="database"`).
4. **Secondary provider:** (If configured).
5. **Explicit `DATA_UNAVAILABLE`:** Explicitly communicate that data is unavailable without returning fabricated or zeroed mock numbers.

### Provider Matrix

| Domain | Provider | Endpoint / Protocol | Requires API Key? | Environment Variable | Attribution & License Note |
|--------|----------|---------------------|-------------------|----------------------|----------------------------|
| **Weather** | Open-Meteo | `https://api.open-meteo.com/v1/forecast` | No | None | Free for non-commercial use with attribution to Open-Meteo. |
| **Air Quality** | OpenAQ | `https://api.openaq.org/v3/locations` | **Yes** | `OPENAQ_API_KEY` | OpenAQ Open Data Platform; requires valid `X-API-Key`. |
| **Currency** | Frankfurter | `https://api.frankfurter.dev/v1/latest` | No | None | Open exchange rate data published by the European Central Bank (ECB). |
| **Geocoding** | Nominatim | `https://nominatim.openstreetmap.org` | No | None | © OpenStreetMap contributors (ODbL). Must send valid descriptive `User-Agent`. Limit: max 1 req/sec. |
| **Routing** | Project OSRM | `http://router.project-osrm.org` | No | None | © Project OSRM and OSM contributors. Basic demo routing; not for heavy navigation. |
| **Places (POI)** | OSM Overpass | `https://overpass-api.de/api/interpreter` | No | None | © OpenStreetMap contributors. Controlled bounded queries only (max 5000m radius). |
| **Public Transit** | GTFS / GTFS-RT | Federated local agency feeds | No (Federated) | `GTFS_FEEDS` | Public transit feeds are decentralized by agency. UrbanLens rejects claiming universal global real-time coverage. |

> [!WARNING]
> **Provider Rate Limits and Licensing Notice:**
> Provider usage tiers, terms of service, rate limits, and licensing terms are set by upstream providers and can change over time. Do not assume unlimited free usage, and do not assume commercial rights without directly verifying individual provider licenses. When running high-throughput production workloads, configure dedicated or self-hosted provider instances.


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

## Phase 4: Real Agent Intelligence & Orchestration

UrbanLens Phase 4 operationalizes the seven domain intelligence agents into fully functioning, service-backed evaluators coordinated by a deterministic orchestrator.

### Seven Modular Intelligence Agents

1. **`LocationAgent`:** Anchors canonical city demographics, coordinates, country records, and location geocoding/POI metadata via `CityService`, `GeocodingService`, and `PlacesService`.
2. **`EnvironmentAgent`:** Retrieves real-time meteorological observations and AQI metrics via `WeatherService` and `AirQualityService`, with historical database fallbacks and explicit observation timestamps.
3. **`MobilityAgent`:** Evaluates intra-city commute routes and public transport metrics via `RoutingService` and `TransitService`, explicitly reporting unconfigured GTFS providers without fabrication.
4. **`CostAgent`:** Evaluates canonical cost-of-living indices and itemized expense baskets against live currency exchange rates via `CostOfLivingService` and `CurrencyService`, strictly preserving baseline price grounding.
5. **`AccommodationAgent`:** Gathers locality amenities and rental baseline indicators using `CostOfLivingService` and `PlacesService`, explicitly flagging unavailable vacancy listings.
6. **`EducationLifestyleAgent`:** Analyzes accredited institutions, QS/THE academic ranking histories, and cultural POIs using `UniversityService` and `PlacesService`.
7. **`SafetyHealthcareAgent`:** Assesses medical facilities (hospitals, clinics) via `PlacesService`, air health criteria (WHO PM2.5 baselines), and national health metrics, strictly refusing to fabricate arbitrary crime or safety ratings.

### Service-Mediated Architecture & Fallback Contract

Agents **never** communicate with external third-party APIs or databases directly. All data access is mediated by the application service layer:

```text
User Query ──> Orchestrator ──> Relevant Agents ──> Application Services ──> [Live Provider | Cache | DB Fallback]
```

Every live-capable service strictly enforces a deterministic fallback hierarchy:
1. **Fresh live provider:** Real-time data from configured external APIs (e.g., Open-Meteo, Franker/FX).
2. **Cached live response:** High-efficiency, thread-safe in-memory TTL cache (`app/core/cache.py`) prevents redundant public API requests and honors provider namespaces.
3. **Canonical database observation:** Validated MongoDB historical baseline records.
4. **Explicit unavailable status:** Missing metrics are clearly recorded as `unavailable` or `error` with explanatory warnings.

### Deterministic Orchestration & Explainable Synthesis

The orchestrator (`app/orchestrator/orchestrator.py`):
- **Resolves City Context:** Identifies target cities from natural language queries (filtering conversational stop words against the alias index and canonical registry) or accepts explicit `city_id` parameters.
- **Keyword Domain Routing:** Maps query intent to relevant agents (e.g., weather keywords to `EnvironmentAgent`, commute terms to `MobilityAgent`, relocation queries to the complete 7-agent suite).
- **Concurrent Execution:** Dispatches agent requests asynchronously via `asyncio`.
- **Explainable Synthesis:** Assembles structured signals, warnings, grounded source citations, and deterministic summaries without relying on an unverified LLM or vector database.

### Intelligence Endpoint

- **`POST /api/v1/intelligence/query`**: Queries the deterministic orchestrator. Accepts natural language questions (`"query"`) and optional `"city_id"`:
  ```json
  {
    "query": "Should I move to Mumbai?",
    "city_id": "city_1356226629"
  }
  ```
  Returns `selected_agents`, normalized `results`, extracted `signals`, grounded `sources`, `warnings`, and deterministic `summary`.

### Phase 4 Limitations Handed Over
- In Phase 4, synthesis was strictly restricted to canonical database observations and live provider signals.

---

## Phase 5: Grounded RAG Knowledge Layer

UrbanLens Phase 5 introduces a production-oriented, retrieval-augmented generation (RAG) knowledge layer. It grounds the platform in semi-structured documentation, official municipal policies, tenancy frameworks, and transport guidelines alongside canonical structured data and live API feeds.

### Target Architecture

```text
User Query
    ↓
Orchestrator
    ↓
Relevant Agents
    ├── MongoDB Structured Data (Canonical Baselines)
    ├── Live APIs (Open-Meteo, Frankfurter FX, OSRM)
    └── RAG Knowledge Retrieval (KnowledgeService)
              ↓
       Grounded Evidence (Traceable Chunks)
              ↓
       Provenance & Citations (Source URLs, Titles, Checksums)
              ↓
       Deterministic Synthesis (Explainable Multi-Source Summary)
```

### 1. Knowledge Document Model & Supported Categories

Knowledge documents are represented by `KnowledgeDocument` in `app/models/knowledge.py` and stored in the `knowledge_documents` collection:
- `document_id`: Deterministic prefix (`doc_<checksum[:12]>`).
- `title`, `source`, `source_url`, `publisher`: Explicit publication metadata.
- `country_id`, `city_id`: Canonical spatial mapping.
- `category`: Bounded domain taxonomy.
- `language`, `published_at`, `updated_at`, `fetched_at`: Temporal and linguistic tracking.
- `content`, `checksum`: Normalized raw text and SHA-256 content checksum.
- `metadata`, `status`: Structured annotations and ingestion status.

Supported knowledge categories:
`relocation`, `government`, `transport`, `healthcare`, `education`, `safety`, `culture`, `lifestyle`, `housing`, `immigration`, `environment`, `city_information`.

### 2. Document Ingestion Pipeline

The ingestion service (`KnowledgeIngestionService` in `app/services/knowledge_ingestion.py`):
- **Normalization:** Cleans redundant whitespace, standardizes punctuation, and strips boilerplate safely.
- **Deterministic Checksum:** Computes SHA-256 over normalized content to guarantee idempotency.
- **Idempotency Guarantee:** If a document with identical checksum exists, re-ingestion returns the existing record without duplicate storage.
- **No Uncontrolled Web Crawling:** Ingestion is controlled and explicit; bulk or uncontrolled crawling is strictly rejected.

### 3. Boundary-Aware Deterministic Chunking

The chunking engine (`app/services/chunking.py`):
- Splits documents respecting natural boundary hierarchy: double line breaks (paragraphs), sentence delimiters (`. `, `! `, `? `), and token words.
- Preserves context across chunks using configurable overlap (`chunk_size=600`, `chunk_overlap=100`).
- Each chunk preserves `chunk_id`, `document_id`, `chunk_index`, `char_start`, `char_end`, `word_count`, `city_id`, `country_id`, and `category`.

### 4. Pluggable Embedding Provider Abstraction

Located in `app/providers/embedding/`:
- **`BaseEmbeddingProvider`**: Interface defining `embed_text` and `embed_batch`.
- **`DeterministicHashEmbeddingProvider`**: Local, reproducible signed SHA-256 n-gram feature hasher with unit L2 normalization. Operates offline without external vendor dependencies or paid APIs.
- **Factory & Extensibility:** Switchable via `EMBEDDING_PROVIDER` configuration (`hash`, `mock`, or future hosted providers like OpenAI/Vertex). Unconfigured hosted providers fail fast and clearly.
- **Anti-Fabrication:** Never invents fake embedding vectors or mock numbers.

### 5. Grounded Semantic Retrieval & Vector Storage

The knowledge repository (`KnowledgeRepository` in `app/db/repositories/knowledge.py`) and retrieval service (`KnowledgeService` in `app/services/knowledge.py`):
- Stores chunk vectors and document metadata in MongoDB Atlas.
- Executes cosine similarity matching over L2-normalized embeddings.
- Supports strict metadata filtering by `city_id`, `country_id`, and `categories`.
- Computes genuine mathematical similarity scores—no fabricated relevance numbers.

### 6. RAG Provenance Model & Source Classification

Retrieved chunks are formatted as `KnowledgeEvidence`:
- `evidence_id`, `document_id`, `chunk_id`
- `title`, `source`, `source_url`, `publisher`
- `text`, `category`, `city_id`, `country_id`
- `retrieved_at`, `retrieval_score`

UrbanLens enforces a clear distinction between three source classes:
1. **`LIVE`**: Dynamic real-time APIs (Open-Meteo, Frankfurter FX, OSRM).
2. **`DATABASE`**: Validated MongoDB canonical structured benchmarks.
3. **`KNOWLEDGE`**: Grounded RAG document chunks with explicit source citations.

### 7. Agent & Orchestrator Integration

- **Domain Agents:** Selected agents query `KnowledgeService` for their specific domain scopes (e.g. `LocationAgent` -> `city_information`, `EnvironmentAgent` -> `environment`, `MobilityAgent` -> `transport`).
- **Orchestrator Synthesis:** Assembles structured signals, live signals, and knowledge citations into an explainable, deterministic report without LLM hallucination.

### 8. Knowledge Endpoints

- `GET /api/v1/knowledge/search`: Query grounded knowledge chunks with filters:
  - Query parameters: `query`, `city_id`, `country_id`, `category`, `top_k`, `min_score`.
- `POST /api/v1/knowledge/documents`: Ingest a verified knowledge document.
- `GET /api/v1/knowledge/documents/{document_id}`: Retrieve a stored knowledge document by ID.
- `POST /api/v1/intelligence/query`: Includes grounded `knowledge_evidence` array alongside structured `signals` and live `sources`.

### Phase 5 Limitations
- **No LLM Synthesis Yet:** Synthesis remains fully deterministic and rule-based; Gemini/LLM reasoning is scheduled for future phases.
- **No Uncontrolled Web Crawling:** Ingestion is controlled via explicit document feeds or API ingestion.
- **No Fabricated Knowledge:** Missing knowledge yields empty results rather than speculative answers.

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

- [x] **RAG Knowledge Layer:** Grounded document ingestion, deterministic boundary-aware chunking, pluggable embedding abstraction, and multi-source provenance (Phase 5).
- [ ] **Live Provider Connectors:** Dynamic integration of real-time GTFS feeds and OpenWeather/AirNow live APIs.
- [ ] **LLM Grounding & Natural Language Synthesis:** Feed multi-agent grounded outputs and citations into Gemini / LLM models for conversational explanations.
- [ ] **City Comparison Matrix:** Multi-city side-by-side benchmarking endpoint (`/api/v1/compare`).
- [ ] **Geospatial GeoJSON Polygons:** Adding full administrative boundaries to city detail responses.
