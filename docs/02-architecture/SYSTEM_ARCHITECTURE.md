# INDRA — System Architecture

> **STATUS: FROZEN FOR PHASE 1 IMPLEMENTATION**
>
> Source: PETRAS Analysis §8, §16; INDRA Master Report §11, §12
>
> **Revision:** Step 2 Architecture Freeze (20 August 2026). Authoritative decisions: [ARCHITECTURE_DECISIONS.md](ARCHITECTURE_DECISIONS.md)

---

## Design Principles

1. **Single-database architecture** — PostgreSQL handles all structured, semi-structured (JSONB), and coordinate data. No multi-database complexity.
2. **Hybrid AI** — LLM for unstructured text processing; deterministic formulas for quantitative computation.
3. **Monolithic deployment** — Single FastAPI backend, single React frontend. No microservices for Phase 1.
4. **Evidence-first** — Every computation preserves its source chain via the provenance model.
5. **Data honesty** — Every data point carries its semantic classification (OBSERVED / DERIVED / HISTORICAL_CALIBRATED / ASSUMED / SIMULATED).
6. **Corridor-first modeling** — Corridors (Hormuz, Red Sea, Russia, Suez, etc.) are first-class domain entities, not free-form strings.

---

## Canonical Domain Model (Phase 1 — Frozen)

Authoritative entity list and relationships for implementation:

| Entity | Purpose |
|---|---|
| `countries` | Supplier/transit countries, base risk |
| `corridors` | Strategic pathways/chokepoints (stable codes) |
| `suppliers` | Crude suppliers linked to country + grades |
| `crude_grades` | Controlled vocabulary for crude types |
| `ports` | Origin and Indian receiving ports |
| `routes` | Supplier paths: origin port → corridors → destination port |
| `refineries` | Indian refineries linked to receiving port |
| `refinery_supply_mix` | Refinery–grade compatibility and share constraints |
| `geopolitical_events` | Ingested events with country/corridor/route associations |
| `risk_scores` | Computed risk for corridor/route/supplier/country |
| `scenarios` | Disruption parameter sets |
| `scenario_results` | Deterministic scenario outputs |
| `procurement_options` | Ranked alternatives per scenario + refinery |
| `strategic_reserves` | SPR locations and levels |
| `commodity_prices` | USD price observations (EIA) |
| `fx_rates` | FX observations (RBI) — separate stream |
| `evidence_records` | Provenance nodes |
| `evidence_links` | Evidence chain edges |
| `entity_aliases` | Entity resolution mappings |
| `data_sources` | External feed registry |

**Frozen relationships:**

```
Geopolitical Event → affected countries, corridors, routes (when known)
Supplier → country, crude grades
Route → origin port, destination port, corridor_ids[]
Refinery → receiving port, refinery_supply_mix
Refinery Supply Mix → refinery, crude grade, compatibility, share constraints
Scenario → disruption parameters → scenario_results
Procurement Option → scenario, supplier, route, crude grade
```

The LLM outputs human-readable names only — never internal database IDs. See [DATABASE_SCHEMA.md](../05-database/DATABASE_SCHEMA.md) and [ARCHITECTURE_DECISIONS.md](ARCHITECTURE_DECISIONS.md).

---

## Risk Scale Convention

> **FROZEN for all documents:**
>
> - **Internal representation:** 0.0–1.0 (stored in database, used in computations)
> - **Display representation:** 0–100 (shown in UI, returned in API display fields)
> - **Conversion:** `display_score = internal_score × 100`
>
> This applies to: risk scores, severity, confidence, compatibility scores.

---

## Logical Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    EXTERNAL DATA SOURCES                      │
│  GDELT (15-min) │ ACLED (weekly) │ OFAC (daily)             │
│  EIA (daily)    │ RBI (daily)    │ NewsAPI/RSS (hourly)     │
│  PPAC (static)  │ ISPRL (static)                            │
└──────────────────────────┬───────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│                   INGESTION LAYER                            │
│              APScheduler + httpx                             │
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
│                                                              │
│  ┌─────────────────┐  ┌─────────────────┐                   │
│  │ LLM Extraction  │  │ Pydantic        │                   │
│  │ (news → JSON)   │  │ Validation      │                   │
│  └────────┬────────┘  └────────┬────────┘                   │
│           │                    │                             │
│           ▼                    ▼                             │
│  ┌─────────────────────────────────────────┐                │
│  │       ENTITY RESOLUTION LAYER           │                │
│  │                                         │                │
│  │  LLM output (names/strings)             │                │
│  │       ↓                                 │                │
│  │  entity_aliases table lookup            │                │
│  │       ↓                                 │                │
│  │  RapidFuzz fuzzy match (if no exact)    │                │
│  │       ↓                                 │                │
│  │  Internal database IDs                  │                │
│  │  (country_ids, corridor_ids, etc.)      │                │
│  └────────┬────────────────────────────────┘                │
│           │                                                  │
│  ┌────────▼────────┐                                        │
│  │  Deduplication   │                                       │
│  │  (source URL +   │                                       │
│  │   temporal window)│                                      │
│  └────────┬─────────┘                                       │
└───────────┼─────────────────────────────────────────────────┘
            │
            ▼
┌──────────────────────────────────────────────────────────────┐
│                     PostgreSQL                               │
│                                                              │
│  REFERENCE: countries │ corridors │ crude_grades │ suppliers │
│             ports │ refineries │ refinery_supply_mix │ routes│
│                                                              │
│  EVENTS:   geopolitical_events │ risk_scores                │
│                                                              │
│  MARKET:   commodity_prices │ fx_rates                      │
│                                                              │
│  OUTPUTS:  scenarios │ scenario_results │ procurement_options│
│            strategic_reserves                                │
│                                                              │
│  PROVENANCE: evidence_records │ evidence_links              │
│              entity_aliases │ data_sources                  │
└──────────────────────────┬───────────────────────────────────┘
            │
            ▼
┌──────────────────────────────────────────────────────────────┐
│               COMPUTATION ENGINES                            │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Risk Engine   │  │ Scenario     │  │ Supply Graph │      │
│  │ (Weighted     │  │ Engine       │  │ (NetworkX)   │      │
│  │  Rules)       │  │ (parametric) │  │              │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                 │                  │              │
│         ▼                 ▼                  ▼              │
│  ┌──────────────┐  ┌──────────────┐                        │
│  │ Procurement  │  │ SPR          │                        │
│  │ Engine       │  │ Engine       │                        │
│  │ (ranking/LP) │  │ (arithmetic) │                        │
│  └──────┬───────┘  └──────┬───────┘                        │
│         └─────────────────┘                                │
│                    │                                        │
│                    ▼                                        │
│  ┌──────────────────────────────────┐                      │
│  │  Recommendation Builder          │                      │
│  │  (structured output              │                      │
│  │   + optional LLM explanation)    │                      │
│  └──────────────────────────────────┘                      │
└──────────────────────────┬───────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│                    FastAPI REST API                           │
│  ~12 MVP endpoint groups                                    │
│  /events │ /risk │ /corridors │ /scenarios │ /recommend     │
│  /reserves │ /routes │ /prices │ /evidence │ /health       │
└──────────────────────────┬───────────────────────────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ React        │
                    │ Dashboard    │
                    │ + Leaflet    │
                    │ + Recharts   │
                    └──────────────┘
```

---

## Component Responsibilities

### 1. Ingestion Layer

| Component | Technology | Responsibility |
|---|---|---|
| Schedulers | APScheduler | Periodic polling of external data sources |
| HTTP clients | httpx (async) | API calls to GDELT, ACLED, EIA, RBI, OFAC, NewsAPI |
| Static loader | Python scripts | One-time seed of India refinery, port, route, corridor, supplier, crude grade, SPR data |

The ingestion layer does NOT use Kafka, message queues, or event streaming. APScheduler with PostgreSQL persistence is sufficient for the data volumes involved (hundreds of events per day, not millions).

### 2. Processing Layer

| Component | Technology | Responsibility |
|---|---|---|
| Validation | Pydantic | Schema enforcement for all ingested and computed data |
| Entity resolution | entity_aliases table + RapidFuzz | Map LLM-output names/strings to internal database IDs |
| Deduplication | Rule-based (source URL + temporal window) | Same event from multiple sources → single event record |
| LLM extraction | Abstracted LLM provider | Unstructured news → structured JSON event object |

### 3. Entity Resolution Layer

The entity resolution layer sits between LLM extraction and database insertion. It is responsible for mapping human-readable names to internal database IDs.

**Data flow:**
```
LLM output (human-readable)          Entity resolution          Database (internal IDs)
─────────────────────────          ─────────────────          ──────────────────────

"country_names": ["Iran"]    →    entity_aliases lookup    →    affected_country_ids: [7]
"corridor_names": ["HORMUZ"] →    entity_aliases lookup    →    affected_corridor_ids: [1]
"entity_name": "Aramco"      →    RapidFuzz fuzzy match    →    supplier_id: 3
```

**The LLM must NOT produce database IDs.** It outputs normalized human-readable values. The entity resolution layer performs the mapping using:

1. Exact match against `entity_aliases` table
2. Fuzzy match via RapidFuzz (threshold ≥ 85% similarity) if no exact match
3. Fallback: log unresolved entity for manual review; do not insert unresolved references

**Phase 1 scope:** Pre-populate ~50–100 aliases covering key countries, corridors, suppliers, crude grades, and chokepoints.

See [AI_PIPELINE.md](../07-ai-ml/AI_PIPELINE.md) for LLM output schema and extraction details.

### 4. AI/ML Layer

| Component | Technology | Responsibility |
|---|---|---|
| Event extraction | LLM (abstracted provider) | Convert news articles to structured event JSON |
| Risk scoring | Weighted formula (deterministic) | Calculate corridor/supplier/route risk from event features |
| Supply graph | NetworkX | Graph traversal: reachability, path analysis, disruption propagation (see §5a below) |

**Phase 1:** Rule-based weighted scoring. Architecture supports drop-in ML models (Phase 2).

See [AI_PIPELINE.md](../07-ai-ml/AI_PIPELINE.md) for LLM boundaries and [ML_MODEL.md](../07-ai-ml/ML_MODEL.md) for ML strategy.

### 5. Computation Engines

| Engine | Technology | Input | Output |
|---|---|---|---|
| Scenario Engine | Python (parametric) | Disruption type, severity, duration, corridor + NetworkX-derived affected entities | Supply gap, affected refineries, days-to-critical, cost impact |
| Procurement Engine | scipy.optimize / PuLP | Suppliers × routes × prices × risk × crude grade compatibility | Ranked procurement options with cost/risk tradeoff |
| SPR Engine | Python (deterministic) | Supply gap, reserve levels, drawdown rate | Recommended drawdown, remaining reserve, days bridged, uncovered gap |

See [SCENARIO_ENGINE.md](../08-engines/SCENARIO_ENGINE.md) and [OPTIMIZATION.md](../08-engines/OPTIMIZATION.md).

### 5a. Supply Graph Layer (NetworkX)

NetworkX models India's crude oil supply network as an in-memory directed graph. It is used for **graph traversal and connectivity queries only** — not for numerical calculation, risk scoring, or optimization.

#### Graph Structure

```
Nodes:  Supplier | Port (origin) | Corridor | Port (destination) | Refinery
Edges:  Supplier → OriginPort → Corridor → DestinationPort → Refinery
        (weighted by: route capacity, corridor risk score, transit days)
```

The graph is **built at runtime from PostgreSQL** (the persistent source of truth) and rebuilt when the entity dataset changes. It is not stored separately.

#### What NetworkX IS responsible for in Phase 1

| Operation | Description |
|---|---|
| **Affected refinery identification** | Given a disrupted corridor/route, traverse the graph to find all refineries downstream of that corridor |
| **Alternative route discovery** | Find feasible paths from supplier → refinery that do NOT pass through the disrupted corridor(s) |
| **Reachability check** | Determine whether a supplier can reach a specific refinery via any non-disrupted path |
| **Supplier–route–port–refinery traversal** | Traverse the full supply chain to determine which supplier–route combinations serve a given refinery |
| **Disruption propagation input** | Provide the list of affected entities (refineries, routes, suppliers) that the Scenario Engine then uses for arithmetic calculation |

#### What NetworkX is NOT responsible for

| Task | Correct component |
|---|---|
| Calculating risk scores | Risk Engine (weighted formula) |
| Computing supply gaps or volume loss | Scenario Engine (parametric arithmetic) |
| Optimizing procurement allocation | Procurement Engine (scipy LP / ranking) |
| Storing entity relationships | PostgreSQL (source of truth) |
| Calculating SPR bridge requirements | SPR Engine (deterministic arithmetic) |

#### PostgreSQL / NetworkX Boundary

```
PostgreSQL (source of truth)
    stores: corridors, routes, ports, suppliers, refineries, supply_mix
          ↓ loaded at startup / corridor-state-change
NetworkX in-memory graph
    answers: "which refineries are reachable from corridor X?"
             "which alternative routes exist if corridor Y is disrupted?"
          ↓ returns affected entity lists
Scenario Engine (Python arithmetic)
    computes: supply_gap = affected_volume × disruption_pct × duration
              days_until_critical, cost_impact, SPR bridge requirement
```

The Scenario Engine **does not traverse the graph itself** — it receives the graph query results as structured lists and applies the documented arithmetic formulas.

### 6. Backend (FastAPI)

Single FastAPI application serving:
- ~12 MVP REST API endpoint groups (see [API_SPEC.md](../04-backend/API_SPEC.md))
- Background scheduler management (APScheduler)
- AI pipeline orchestration
- Engine invocation

### 7. Frontend (React)

Single-page React application with:
- Risk overview dashboard (corridor risk cards)
- Interactive Leaflet map (India supply network)
- Scenario simulator + Procurement recommendations (combined view)
- Evidence drawer (accessible from any page via "Why?" links)

See [UI_UX.md](../03-frontend/UI_UX.md).

### 8. Database (PostgreSQL)

Single PostgreSQL instance. 20 tables organized into:
- **Reference entities:** countries, corridors, crude_grades, suppliers, ports, refineries, refinery_supply_mix, routes
- **Events/risk:** geopolitical_events, risk_scores
- **Market data:** commodity_prices, fx_rates
- **Outputs:** scenarios, scenario_results, procurement_options, strategic_reserves
- **Provenance:** evidence_records, evidence_links, entity_aliases, data_sources

See [DATABASE_SCHEMA.md](../05-database/DATABASE_SCHEMA.md).

---

## Provenance / Evidence Architecture

Every important output in INDRA is traceable through a provenance chain:

```
SOURCE ARTICLE (URL, timestamp, source name)
    ↓  [evidence_type: SOURCE]
LLM EXTRACTION (model, input/output, confidence)
    ↓  [evidence_type: LLM_EXTRACTION]
ENTITY RESOLUTION (alias → canonical ID mapping)
    ↓  [evidence_type: ENTITY_RESOLUTION]
RISK CALCULATION (formula, component weights, contributing events)
    ↓  [evidence_type: RISK_CALCULATION]
SCENARIO COMPUTATION (parameters, assumptions, formula results)
    ↓  [evidence_type: SCENARIO_COMPUTATION]
OPTIMIZATION (objective, constraints, ranking scores)
    ↓  [evidence_type: OPTIMIZATION]
RECOMMENDATION (final ranked output with scoring breakdown)
    ↓  [evidence_type: RECOMMENDATION]
```

Each step creates an `evidence_records` entry. The `evidence_links` table connects them into chains. The UI evidence drawer traverses these chains.

---

## Data Semantic Classification

| Category | Definition | Example |
|---|---|---|
| **OBSERVED** | Directly fetched from external source | EIA Brent price, GDELT event |
| **DERIVED** | Calculated from observed values via documented formula | Risk score, supply gap |
| **HISTORICAL_CALIBRATED** | Parameter derived from historical event analysis | $15/bbl Hormuz price impact |
| **ASSUMED** | Configuration/user assumption | Freight multiplier, risk weight |
| **SIMULATED** | Synthetic state for scenario/demo | Demo fixture events, scenario disruption |

This classification replaces the previous LIVE/RECENT/HISTORICAL/DERIVED/SIMULATED system with finer granularity. The UI data badges should reflect these categories.

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
   {event_type, severity, country_names, corridor_names, entities, confidence}
   (all values are human-readable names, NOT database IDs)
                    ↓
6. Post-LLM validation:
   - Is event within last 30 days?
   - Confidence > 0.6?
   - event_type in allowed enum?
   - Severity within valid range?
                    ↓
7. Entity resolution maps names → internal IDs:
   country_names → affected_country_ids
   corridor_names → affected_corridor_ids
   entity_name → supplier_id / port_id (if applicable)
                    ↓
8. Event stored in PostgreSQL with source URL, timestamp, IDs
   Evidence record created (type: LLM_EXTRACTION + ENTITY_RESOLUTION)
                    ↓
9. Risk engine recalculates affected corridor scores
   (deterministic weighted formula, all 0.0–1.0 internal)
   Evidence record created (type: RISK_CALCULATION)
                    ↓
10. Alert generated if risk_delta > threshold
                    ↓
11. User opens scenario simulator, selects disruption
                    ↓
12. Scenario engine propagates disruption through supply graph:
    - Reduce affected corridor/route capacity
    - Calculate refinery feedstock shortfall (via refinery_supply_mix)
    - Estimate inventory burn
    - Calculate national supply gap
    - Calculate SPR bridge requirement
    Evidence record created (type: SCENARIO_COMPUTATION)
                    ↓
13. Procurement engine ranks alternatives:
    - Filter by crude grade compatibility (via refinery_supply_mix)
    - Exclude sanctioned suppliers
    - Exclude disrupted routes
    - Score by cost + risk + transit + compliance
    - Optionally solve LP for optimal mix
    Evidence record created (type: OPTIMIZATION)
                    ↓
14. Optional: LLM generates natural-language action brief
    (receives ONLY structured, validated results)
                    ↓
15. Dashboard displays results with evidence trail
    Every score links to evidence drawer
```

---

## Price / FX Architecture

Commodity prices (EIA) and FX rates (RBI) are ingested independently into separate tables:

```
EIA API → commodity_prices (USD per barrel, source_timestamp)
RBI API → fx_rates (USD_INR rate, source_timestamp)

Query-time derivation:
  price_inr = commodity_price.price_usd × fx_rate.rate
  where fx_rate.source_timestamp = nearest prior to commodity_price.source_timestamp

Evidence record captures:
  - commodity price source + timestamp
  - FX rate source + timestamp
  - derivation method: "nearest_valid_prior_fx"
```

This replaces the previous design that used a GENERATED column requiring synchronized insertion.

---

## Evidence Flow

Every output preserves a traceable path:

```
SOURCE ARTICLE (URL, timestamp, source name, data_semantic: OBSERVED)
        ↓
EXTRACTED EVENT (type, severity, confidence, LLM model, data_semantic: DERIVED)
        ↓
ENTITY RESOLUTION (corridor/country mapping, data_semantic: DERIVED)
        ↓
RISK CONTRIBUTION (weight, component score, formula, data_semantic: DERIVED)
        ↓
SCENARIO ASSUMPTIONS (disruption %, duration, data_semantic: ASSUMED or HISTORICAL_CALIBRATED)
        ↓
SUPPLY IMPACT (gap MMT, affected refineries, days-to-critical, data_semantic: DERIVED)
        ↓
RECOMMENDATION (supplier, grade, route, cost, risk, compatibility, data_semantic: DERIVED)
```

The evidence panel in the UI must allow drill-down at every level.

---

## Failure Boundaries

| Failure | Impact | Fallback |
|---|---|---|
| GDELT unavailable | No new events ingested | Cached event fixture; demo mode |
| LLM API unavailable | No event extraction | Pre-parsed structured events loaded from seed |
| LLM returns malformed JSON | Event not extracted | Retry once; if still malformed, skip and log |
| LLM hallucinates entity | Wrong corridor/country | Post-extraction validation against entity_aliases whitelist |
| PostgreSQL deployment fails | No data persistence | Fatal — ensure DB is tested before demo |
| LP optimizer infeasible | No optimal procurement mix | Deterministic ranking scorer fallback |
| Map tiles fail | No map visualization | Static map image / simplified view |
| External news noisy | Too many irrelevant events | Fixed energy/geopolitics keyword filters |
| Live feeds rate-limited | Stale data | Demo mode fixture with labeled timestamps |
| RBI API unavailable | No FX rate | Hardcoded recent USD/INR rate labeled HISTORICAL |

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
| HTTP Client | httpx (async) | MUST |
| Optimization | scipy.optimize.linprog | MUST (ranking fallback) |
| LLM | Abstracted provider (see AI_MODEL_STRATEGY) | MUST |
| Frontend | React | MUST |
| Map | React-Leaflet | MUST |
| Charts | Recharts | SHOULD |
| Deployment | Docker Compose | SHOULD |

### Explicitly Excluded Technologies

| Technology | Reason |
|---|---|
| Kafka / Redpanda | Zero streaming volume; APScheduler sufficient |
| Neo4j | NetworkX handles all graph needs |
| MongoDB | PostgreSQL JSONB handles semi-structured data |
| Elasticsearch | News search volume doesn't require this |
| Redis | Not needed at demo data volumes; direct DB queries are fast enough |
| dbt / Airflow | Python scripts sufficient |
| Kubernetes | Simple container deployment is enough |
| PostGIS | Plain lat/lon columns sufficient for Phase 1 |
| aiohttp | Standardized on httpx |

---

## Phase 2/3 Architecture Evolution

### Phase 2 — Pilot
- Add validated XGBoost disruption model with SHAP
- Real AIS subscription (Spire/ExactEarth)
- Stronger entity resolution (embeddings)
- Richer news feeds
- Live freight/insurance data
- User accounts and access control
- Model monitoring and evaluation
- Redis caching layer
- PostGIS for spatial queries

### Phase 3 — Enterprise
- Kafka event streaming
- Neo4j entity graph
- Satellite/RF intelligence
- ERP/SAP integrations
- Enterprise security and audit controls
- Model governance and retraining pipeline
- Multi-tenant deployment
