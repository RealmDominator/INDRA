# INDRA — System Architecture

> Source: PETRAS Analysis §8, §16; INDRA Master Report §11, §12

---

## Design Principles

1. **Single-database architecture** — PostgreSQL handles all structured, semi-structured (JSONB), geospatial (PostGIS), and time-series data. No multi-database complexity.
2. **Hybrid AI** — LLM for unstructured text processing; deterministic formulas for quantitative computation.
3. **Monolithic deployment** — Single FastAPI backend, single React frontend. No microservices for Phase 1.
4. **Evidence-first** — Every computation preserves its source chain.
5. **Data honesty** — Every data point carries its classification (live/recent/historical/derived/simulated).

---

## Logical Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    EXTERNAL DATA SOURCES                      │
│  GDELT (15-min) │ ACLED (weekly) │ OFAC (daily)             │
│  EIA (daily)    │ RBI (daily)    │ NewsAPI/RSS (hourly)     │
│  PPAC (monthly/static) │ ISPRL (static)                     │
└──────────────────────────┬───────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│                   INGESTION LAYER                            │
│              APScheduler + aiohttp/httpx                     │
│                                                              │
│  GDELT poller (15-min)  │  ACLED poller (daily)             │
│  EIA price poller       │  RBI FX poller (daily)            │
│  OFAC poller (daily)    │  News/RSS poller (hourly)         │
│  Static data loader (one-time seed)                          │
└──────────────────────────┬───────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│                  PROCESSING LAYER                            │
│              Pydantic + RapidFuzz + LLM                      │
│                                                              │
│  Deduplication  │  Entity normalization (rules + fuzzy)      │
│  Event classification (LLM-assisted)                         │
│  Severity scoring  │  Feature extraction                     │
│  Structured JSON validation (Pydantic)                       │
└──────────────────────────┬───────────────────────────────────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ LLM Event    │ │ Risk Engine  │ │ Supply Graph │
│ Extraction   │ │ (Weighted    │ │ (NetworkX)   │
│              │ │  Rules)      │ │              │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       │                │                │
       └────────────────┼────────────────┘
                        ▼
┌──────────────────────────────────────────────────────────────┐
│                     PostgreSQL                               │
│                                                              │
│  events │ suppliers │ refineries │ routes │ ports            │
│  risk_scores │ crude_prices │ scenarios │ scenario_results   │
│  procurement_options │ strategic_reserves │ countries        │
└──────────────────────────┬───────────────────────────────────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Scenario     │ │ Procurement  │ │ SPR          │
│ Engine       │ │ Engine       │ │ Engine       │
│ deterministic│ │ ranking / LP │ │ deterministic│
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       └────────────────┼────────────────┘
                        ▼
┌──────────────────────────────────────────────────────────────┐
│               Recommendation Builder                         │
│           structured output + LLM explanation                │
└──────────────────────────┬───────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│                    FastAPI REST API                           │
│  /events │ /risk │ /scenario │ /recommend │ /prices         │
│  /reserve │ /routes │ /suppliers │ /refineries              │
└──────────────────────────┬───────────────────────────────────┘
                           │
                    ┌──────┴──────┐
                    ▼             ▼
          ┌──────────────┐ ┌──────────────┐
          │ Redis Cache  │ │ React        │
          │ (optional)   │ │ Dashboard    │
          └──────────────┘ │ + Leaflet    │
                           │ + Recharts   │
                           └──────────────┘
```

---

## Component Responsibilities

### 1. Ingestion Layer

| Component | Technology | Responsibility |
|---|---|---|
| Schedulers | APScheduler | Periodic polling of external data sources |
| HTTP clients | aiohttp / httpx | Async API calls to GDELT, ACLED, EIA, RBI, OFAC, NewsAPI |
| Static loader | Python scripts | One-time seed of India refinery, port, route, supplier, SPR data |

The ingestion layer does NOT use Kafka, message queues, or event streaming. APScheduler with PostgreSQL persistence is sufficient for the data volumes involved (hundreds of events per day, not millions).

### 2. Processing Layer

| Component | Technology | Responsibility |
|---|---|---|
| Validation | Pydantic | Schema enforcement for all ingested and computed data |
| Entity matching | RapidFuzz | Fuzzy string matching for entity normalization ("Saudi Aramco" = "Saudi Arabian Oil Company") |
| Deduplication | Rule-based + optional sentence embeddings | Same event from multiple sources → single event record |
| LLM extraction | Abstracted LLM provider | Unstructured news → structured JSON event object |

### 3. AI/ML Layer

| Component | Technology | Responsibility |
|---|---|---|
| Event extraction | LLM (abstracted provider) | Convert news articles to structured event JSON |
| Risk scoring | Weighted formula (deterministic) | Calculate corridor/supplier/route risk from event features |
| Supply graph | NetworkX | Model India's supply network as a computational graph |
| Disruption probability | Rule-based thresholds (Phase 1) | Elevated risk if ACLED events > threshold AND sanctions change |

**Phase 2 additions:** XGBoost classification, SHAP explanations, anomaly detection.

See [AI_PIPELINE.md](../07-ai-ml/AI_PIPELINE.md) for LLM boundaries and [ML_MODEL.md](../07-ai-ml/ML_MODEL.md) for ML strategy.

### 4. Computation Engines

| Engine | Technology | Input | Output |
|---|---|---|---|
| Scenario Engine | Python (parametric) | Disruption type, severity, duration | Supply gap, affected refineries, days-to-critical, cost impact |
| Procurement Engine | scipy.optimize / PuLP | Available suppliers × routes × prices × risk × compatibility | Ranked procurement options with cost/risk tradeoff |
| SPR Engine | Python (deterministic) | Supply gap, reserve levels, drawdown rate | Recommended drawdown, remaining reserve, days bridged, uncovered gap |

See [SCENARIO_ENGINE.md](../08-engines/SCENARIO_ENGINE.md) and [OPTIMIZATION.md](../08-engines/OPTIMIZATION.md).

### 5. Backend (FastAPI)

Single FastAPI application serving:
- REST API endpoints for all frontend data needs
- Background scheduler management (APScheduler)
- AI pipeline orchestration
- Engine invocation

See [API_SPEC.md](../04-backend/API_SPEC.md).

### 6. Frontend (React)

Single-page React application with:
- Interactive Leaflet map (India supply network)
- Risk dashboard (corridor risk cards)
- Event feed (classified geopolitical events)
- Scenario simulator (preset + interactive parameters)
- Procurement recommendation panel
- SPR dashboard
- Evidence drawer (drilldown from any score to source)

See [UI_UX.md](../03-frontend/UI_UX.md).

### 7. Database (PostgreSQL)

Single PostgreSQL instance. Extensions considered:
- **PostGIS** — geospatial queries for map data (port/refinery coordinates, route geometry)
- **TimescaleDB** — time-series queries for price history (optional; standard PostgreSQL is adequate for demo volumes)

See [DATABASE_SCHEMA.md](../05-database/DATABASE_SCHEMA.md).

### 8. Cache (Redis)

Optional Redis instance for:
- Caching frequently-requested API responses (risk scores, current prices)
- Rate limiting external API calls
- Session data if needed

Redis is NOT a required dependency. The system must function correctly without it (slower but functional).

---

## Data Flow

### Event Ingestion → Recommendation (Complete Chain)

```
1. GDELT/RSS/ACLED delivers raw event data
                    ↓
2. APScheduler triggers poller at configured interval
                    ↓
3. Raw data validated against Pydantic schema
                    ↓
4. Duplicate detection (source URL + temporal window)
                    ↓
5. LLM extracts structured event:
   {event_type, severity, entities, corridors, confidence}
                    ↓
6. Validation rules applied:
   - Is event within last 30 days?
   - Confidence > 0.6?
   - Country in tracked list?
                    ↓
7. Event stored in PostgreSQL with source URL, timestamp
                    ↓
8. Risk engine recalculates affected corridor scores
   (deterministic weighted formula)
                    ↓
9. Alert generated if risk_delta > threshold
                    ↓
10. User opens scenario simulator, selects disruption
                    ↓
11. Scenario engine propagates disruption through supply graph:
    - Reduce affected route capacity
    - Calculate refinery feedstock shortfall
    - Estimate inventory burn
    - Calculate national supply gap
    - Calculate SPR bridge requirement
                    ↓
12. Procurement engine ranks alternatives:
    - Filter by refinery compatibility
    - Exclude blocked routes/suppliers
    - Score by cost + risk + transit + compliance
    - Optionally solve LP for optimal mix
                    ↓
13. LLM generates natural-language action brief
    (receives ONLY structured, validated results)
                    ↓
14. Dashboard displays results with evidence trail
```

---

## Evidence Flow

Every output preserves a traceable path:

```
SOURCE ARTICLE (URL, timestamp, source name)
        ↓
EXTRACTED EVENT (type, severity, confidence, LLM model used)
        ↓
RISK CONTRIBUTION (weight, component score, formula reference)
        ↓
SCENARIO ASSUMPTIONS (disruption %, duration, affected corridors)
        ↓
SUPPLY IMPACT (gap MMT, affected refineries, days-to-critical)
        ↓
RECOMMENDATION (supplier, grade, route, cost, risk, compatibility)
```

The evidence panel in the UI must allow drill-down at every level.

---

## Failure Boundaries

| Failure | Impact | Fallback |
|---|---|---|
| GDELT unavailable | No new events ingested | Cached event fixture; demo mode |
| LLM API unavailable | No event extraction | Pre-parsed structured events loaded from seed |
| PostgreSQL deployment fails | No data persistence | Local SQLite for demo fallback (extreme case) |
| LP optimizer unstable | No optimal procurement mix | Deterministic ranking scorer |
| Map tiles fail | No map visualization | Static map image / simplified graph view |
| External news noisy | Too many irrelevant events | Fixed energy/geopolitics keyword filters |
| Live feeds rate-limited | Stale data | Demo mode fixture with labeled timestamps |
| Redis unavailable | Slower API responses | Direct database queries (no caching) |

---

## Technology Stack Summary

| Layer | Technology | Phase 1 Status |
|---|---|---|
| Language | Python 3.11 | MUST |
| API Framework | FastAPI | MUST |
| Database | PostgreSQL 16 | MUST |
| ORM | SQLAlchemy | MUST |
| Validation | Pydantic | MUST |
| Scheduler | APScheduler | MUST |
| Graph | NetworkX | MUST |
| Entity Matching | RapidFuzz | MUST |
| Data Processing | pandas | MUST |
| HTTP Client | aiohttp / httpx | MUST |
| Optimization | scipy / PuLP | MUST (ranking fallback) |
| LLM | Abstracted provider (see AI_MODEL_STRATEGY) | MUST |
| Frontend | React | MUST |
| Map | React-Leaflet | MUST |
| Charts | Recharts | SHOULD |
| Cache | Redis | SHOULD |
| Deployment | Docker Compose | SHOULD |
| Geospatial | PostGIS | SHOULD |

### Explicitly Excluded Technologies

| Technology | Reason |
|---|---|
| Kafka / Redpanda | Zero streaming volume; APScheduler sufficient |
| Neo4j | NetworkX handles all graph needs |
| MongoDB | PostgreSQL JSONB handles semi-structured data |
| Elasticsearch | News search volume doesn't require this |
| dbt / Airflow | Python scripts sufficient |
| Kubernetes | Simple container deployment is enough |
| ClickHouse | Unnecessary at demo data volumes |

---

## Phase 2/3 Architecture Evolution

### Phase 2 — Pilot
- Add validated XGBoost disruption model with SHAP
- Real AIS subscription (Spire/ExactEarth)
- Stronger entity resolution
- Richer news feeds
- Live freight/insurance data
- User accounts and access control
- Model monitoring and evaluation

### Phase 3 — Enterprise
- Kafka event streaming
- Neo4j entity graph
- Satellite/RF intelligence
- ERP/SAP integrations
- Enterprise security and audit controls
- Model governance and retraining pipeline
- Multi-tenant deployment
