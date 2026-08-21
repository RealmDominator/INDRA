# INDRA — Project Context & Handoff Document

> **Purpose:** Durable context file for AI development agents taking over the INDRA project.
>
> **Date:** 21 August 2026
>
> **Development State:** Step 0 COMPLETE · Step 1 COMPLETE · Step 2 COMPLETE · Step 3 COMPLETE · Step 4 COMPLETE · Step 5 COMPLETE · Step 6A COMPLETE · Step 6B COMPLETE · Step 6C COMPLETE · Step 7 NOT STARTED

---

## Project

**INDRA — India Disruption Response Architecture**

**STEP 6 COMPLETE — MVP FEATURE IMPLEMENTATION COMPLETE.** Steps 6A (core backend domain layer), 6B (event intelligence and risk), and 6C (frontend dashboard) are verified complete. Backend tests pass (6 total). Frontend builds successfully. The EVENT → RISK → SCENARIO → PROCUREMENT → EVIDENCE flow works end-to-end against real backend APIs. Step 7 (Polish and Demo Preparation) is NOT STARTED.

INDRA is an India-specific energy supply-chain decision-support system that connects geopolitical events to supply-chain risk, disruption scenarios, procurement alternatives, and evidence-backed recommendations.

### Core Intended Workflow

```
Geopolitical Event
→ Data Ingestion
→ LLM Event Extraction
→ Entity Resolution
→ Risk Calculation
→ Supply-Chain Impact
→ Scenario Simulation
→ Procurement Optimization
→ Evidence Trail
→ Dashboard
```

### Target Users

- IOC / BPCL / HPCL procurement and supply-chain teams
- MoPNG policy/crisis-monitoring teams
- ISPRL strategic-reserve planning teams
- DGH / related energy-policy stakeholders

This is a **hackathon MVP**, not an enterprise production platform.

---

## Current Development Status

| Step | Description | Status |
|---|---|---|
| **Step 0** | Project Foundation | ✅ COMPLETE |
| **Step 1** | Architecture Adversarial Review + Corrections | ✅ COMPLETE |
| **Step 2** | Architecture Freeze | ✅ COMPLETE |
| **Step 3** | Local Development Foundation | ✅ COMPLETE |
| **Step 4** | Data Foundation | ✅ COMPLETE |
| **Step 5** | PostgreSQL Implementation + Verified Data Loading | ✅ COMPLETE |
| **Step 6A** | Core Backend Domain Layer | ✅ COMPLETE |
| **Step 6B** | Event Intelligence and Risk | ✅ COMPLETE |
| **Step 6C** | Frontend Dashboard | ✅ COMPLETE |
| **Step 7** | Polish and Demo Preparation | ❌ NOT STARTED |

> **Architecture is frozen for Phase-1 implementation.** Step 6 is COMPLETE. Step 7 must not start without explicit user direction.

---

## Repository Structure

```
INDRA/
├── CONTEXT.md                          ← this file
├── README.md
├── .gitignore
├── .env.example
├── docker-compose.yml
│
├── research/
│   ├── research_report_1.md            ← primary research source (DO NOT rewrite)
│   └── research_report_2.md            ← primary research source (DO NOT rewrite)
│
├── docs/
│   ├── DEVELOPMENT_RULES.md
│   ├── 01-product/
│   │   ├── SOLUTION_OVERVIEW.md
│   │   └── MVP_SCOPE.md
│   ├── 02-architecture/
│   │   ├── SYSTEM_ARCHITECTURE.md      ← FROZEN
│   │   ├── ARCHITECTURE_DECISIONS.md   ← authoritative ADRs (Step 2)
│   │   ├── ARCHITECTURE_REVIEW.md
│   │   └── PRE_STEP2_DECISIONS.md
│   ├── 03-frontend/
│   │   └── UI_UX.md
│   ├── 04-backend/
│   │   └── API_SPEC.md
│   ├── 05-database/
│   │   └── DATABASE_SCHEMA.md
│   ├── 06-data/
│   │   └── DATA_SOURCES.md
│   ├── 07-ai-ml/
│   │   ├── AI_PIPELINE.md
│   │   ├── ML_MODEL.md
│   │   └── AI_MODEL_STRATEGY.md
│   ├── 08-engines/
│   │   ├── SCENARIO_ENGINE.md
│   │   └── OPTIMIZATION.md
│   ├── 09-testing/
│   │   └── TESTING.md
│   └── 10-demo/
│       └── DEMO_SCRIPT.md
│
├── backend/                            ← FastAPI with domain models, repositories, services, entity resolution, intelligence APIs, and tests (Step 6 COMPLETE)
├── frontend/                           ← React/Vite dashboard with EVENT→RISK→SCENARIO→PROCUREMENT→EVIDENCE flow, semantic states, evidence presentation (Step 6 COMPLETE)
├── data/
│   ├── seed/                           ← 11 curated seed CSV files (167 rows total)
│   ├── raw/ofac/                       ← OFAC SDN list (raw download, .gitignored)
│   ├── processed/ofac/                 ← Energy-relevant OFAC extract (.gitignored)
│   ├── processed/rbi/                  ← RBI FX sample format (.gitignored)
│   └── metadata/                       ← data_manifest.json (provenance)
├── ml/                                 ← empty, no models trained
├── prompts/                            ← empty
├── db/                                 ← schema.sql (reconciled with frozen schema), seed.sql (generated from CSVs)
├── scripts/data/                       ← validation, acquisition, and loader scripts
└── deployment/                         ← empty
```

Research files are reference material and must not be silently rewritten.

---

## Step 0 Summary — Project Foundation

Step 0 established:

- Repository structure
- Documentation framework
- Design principles
- MVP scope classification (MUST / SHOULD / NICE TO HAVE / DO NOT BUILD)
- Technology choices
- Development rules

### Step 0 Design Principles

1. Keep the Phase-1 system simple enough for a single student developer.
2. PostgreSQL is the primary persistent database.
3. FastAPI is the backend.
4. React is the frontend.
5. NetworkX is used for supply-chain graph operations.
6. LLM usage is bounded.
7. Numerical calculations must remain deterministic and reproducible.
8. Evidence/provenance is a core product requirement.
9. Data must never be fabricated.
10. Simulated data must never be represented as live data.
11. Unnecessary enterprise infrastructure is out of scope.

### Explicitly OUT OF SCOPE for Phase 1

- Real-time AIS vessel tracking
- Kafka
- Neo4j
- MongoDB
- Elasticsearch
- ClickHouse
- Kubernetes
- Blockchain
- Microservices
- Mobile app
- Enterprise authentication
- LSTM / GNN / reinforcement learning
- GPU-heavy custom transformer training
- Paid commercial data feeds
- Multi-database architecture

---

## Step 1 Summary — Adversarial Architecture Review + Corrections

Step 1 was an adversarial architecture review that intentionally attacked the architecture from the perspectives of: software architecture, backend engineering, data engineering, ML engineering, AI/LLM engineering, database engineering, frontend engineering, optimization/operations research, security, reliability, energy-domain credibility, and hackathon judging.

**Conclusion:** PROCEED WITH TARGETED FIXES — DO NOT REDESIGN.

The review identified several important architectural issues. Targeted corrections were applied. These corrections are documented in `docs/02-architecture/PRE_STEP2_DECISIONS.md`.

---

## Accepted Step-1 Architectural Corrections

### 1. Corridors as First-Class Domain Entities

Corridors are first-class domain entities, not free-form strings.

Examples: HORMUZ, RED_SEA, SUEZ, RUSSIA, and other explicitly supported corridors.

The system must calculate and expose corridor-level risk.

### 2. Event → Country → Corridor → Route Relationship

Geopolitical events may affect:
- Multiple countries (`affected_country_ids INT[]`)
- One or more corridors (`affected_corridor_ids INT[]`)
- Zero or more directly identified routes (`affected_route_ids INT[]`)

The LLM does NOT produce database IDs. Instead:

```
LLM → human-readable names/codes → validation → entity resolution → internal database IDs
```

Not every event must map directly to a route.

### 3. Entity Resolution Layer

Sits between the LLM and the database.

Phase-1 approach:
1. Exact alias lookup (via `entity_aliases` table)
2. Fuzzy matching using RapidFuzz (≥85% threshold) as fallback
3. Unresolved entity logging (do not insert bad FK references)

Phase-1 scope: ~50–100 pre-populated aliases.

No vector database or embedding system in Phase 1.

### 4. Crude Grades

Controlled reference structure (`crude_grades` table) instead of uncontrolled free-form strings.

Phase-1 scope: ~10–15 grades relevant to India's import basket.

### 5. Refinery Supply Mix

`refinery_supply_mix` table represents refinery-level crude-grade compatibility and supply allocation.

Unknown values must remain unknown or be explicitly marked as estimated (`source_type = 'UNKNOWN'` or `'ESTIMATED'`). Do NOT invent supply percentages.

### 6. Price + FX Separation

`commodity_prices` and `fx_rates` are separate observation streams.

Do NOT synchronize EIA and RBI observations in one generated database column.

INR valuation is derived at query time using a "nearest-valid-prior FX rate" timestamp-alignment rule.

### 7. Risk Scale Standardization

| Context | Scale |
|---|---|
| Internal storage/computation | 0.0–1.0 |
| Display / API responses | 0–100 |
| Conversion | `display_score = internal_score × 100` |

Risk classification thresholds (internal):
```
0.00–0.29   LOW
0.30–0.49   MODERATE
0.50–0.69   HIGH
0.70–0.84   CRITICAL
0.85–1.00   EXTREME
```

### 8. Provenance / Evidence Architecture

Evidence chain: Source → LLM extraction → entity resolution → risk calculation → scenario computation → optimization → recommendation.

Structures: `evidence_records`, `evidence_links`, `data_sources`.

Important outputs must be traceable to their source or calculation path.

### 9. Data Semantic Classification

The active semantic classification system:

| Category | Definition |
|---|---|
| **OBSERVED** | Directly fetched from an external source |
| **DERIVED** | Calculated from observed values via documented formula |
| **HISTORICAL_CALIBRATED** | Parameter derived from analysis of historical events |
| **ASSUMED** | Configuration or user assumption not derived from data |
| **SIMULATED** | Synthetic state generated for scenario/demo purposes |

Do NOT represent SIMULATED data as live data.

### 10. NetworkX Role

NetworkX remains in Phase 1 for defined graph operations:
- Supplier → route → port → refinery traversal
- Reachability analysis
- Affected-refinery discovery given disrupted corridors/routes
- Alternate-route discovery
- Graph-based disruption propagation where traversal is needed

NetworkX is NOT:
- The database (PostgreSQL is the persistent source of truth)
- The risk engine (weighted deterministic formula)
- The optimization engine (PuLP/scipy)
- The scenario arithmetic engine (Python parametric)

### 11. GDP Impact Removal

`gdp_impact_estimate_usd_bn` was removed from scenario results. GDP impact estimation requires macroeconomic modeling beyond this system's scope.

### 12. Generated `days_coverage` Removal

`strategic_reserves.days_coverage` GENERATED column was removed. Computed at application/query layer instead: `current_level_mmt / india_daily_consumption_mmt`.

---

## Phase-1 Risk Model Status

| | Status |
|---|---|
| **Phase 1** | Weighted deterministic risk engine — **implemented (Step 6B)** |
| **Phase 2 candidate** | XGBoost disruption-probability model — **NOT implemented** |

> **IMPORTANT:** Phase 1 risk scoring is a **weighted deterministic risk engine**, NOT XGBoost. Do not claim that INDRA currently uses trained XGBoost risk scoring. XGBoost is a Phase 2 candidate / ML-ready extension that is NOT implemented.

Default risk formula weights (from INDRA Master Report §5.2, configuration-driven):
```
risk = 0.25×event_severity + 0.20×event_recency + 0.20×chokepoint_exposure
     + 0.15×conflict_sanctions + 0.10×historical_rate + 0.10×india_dependency
```

All weights must be changeable without code changes.

---

## Application LLM Status

The application LLM has **NOT been selected** yet.

The **provider abstraction is implemented (Step 6B)**: `LLMProvider` protocol with `UnconfiguredLLMProvider` (safe default) and `CallableLLMProvider`. No external LLM provider is connected.

Development-agent models and application LLMs are **separate decisions**.

### Approved Development-Model Pool

| Model | Recommended Role |
|---|---|
| GPT-5.6 Terra | Architecture review, complex reasoning, system design |
| GPT-5.6 Luna | Fast implementation, debugging, iterative code changes |
| Kimi K2.6 | Large-context repository analysis, documentation review |
| GLM 5.2 | Rapid implementation, UI/frontend coding |
| MiniMax M3 | Agentic coding workflows, multi-step task execution |
| Nemotron 3 Super | Open/free frontier reasoning, agentic reasoning |
| Nemotron 3 Nano / Lightning | Low-latency application inference candidates |
| Claude | Optional quality/reference benchmark |

These are task-specific role assignments, NOT a universal model ranking.

The final runtime application LLM will be chosen later through an INDRA-specific benchmark. Do NOT select the application LLM now.

---

## LLM Boundaries

The application LLM is intended for:
1. Structured event extraction (news articles → structured JSON)
2. Natural-language explanation from already validated results

The LLM must NOT:
- Calculate numerical risk scores
- Perform scenario arithmetic
- Perform procurement optimization
- Generate real-world prices
- Generate database IDs
- Invent data
- Replace deterministic calculations

---

## Scenario Engine Status

Scenario computation is **deterministic and parametric** — **implemented (Step 6B)** via `scenario_supply_gap`.

It may calculate: disrupted capacity, affected supply, refinery impact, inventory pressure, national supply gap, SPR support requirement, procurement gap, modeled cost effects.

Every important scenario value must be classified using the five semantic categories.

The LLM is NOT responsible for scenario mathematics.

---

## Procurement Engine Status

| Approach | Description | Status |
|---|---|---|
| **Preferred (Phase 1)** | PuLP/scipy linear programming | NOT implemented |
| **Fallback** | Deterministic weighted ranking | **Implemented (Step 6B)** via `rank_procurement` |

Potential constraints: supplier availability, route capacity, sanctions, crude compatibility, transit time, disrupted routes, required supply volume.

LLM may explain the result but must NOT generate the numerical optimization result.

---

## API Status

The MVP API is **implemented (Steps 6A–6B)** within the frozen ~12 endpoint-group boundary. See `docs/04-backend/API_SPEC.md` for the authoritative contract.

### Implemented Endpoints

| Group | Routes | Status |
|---|---|---|
| Health | `GET /health` | ✅ Implemented |
| Domain reference | `GET /countries`, `/corridors`, `/crude-grades`, `/suppliers`, `/routes`, `/refineries`, `/reserves` | ✅ Implemented (Step 6A) |
| Events | `POST /events`, `GET /events` | ✅ Implemented (Step 6B) |
| Risk | `GET /corridors/risk`, `POST /risk`, `GET /risk` | ✅ Implemented (Step 6B) |
| Scenarios | `POST /scenarios` | ✅ Implemented (Step 6B) |
| Recommendations | `POST /recommendations` | ✅ Implemented (Step 6B) |

### Not Yet Implemented

- `GET /prices` — EIA commodity prices (deferred; no API key)
- Dedicated evidence endpoints — evidence chain returned inline with intelligence responses; standalone evidence routes not yet exposed

Do NOT expand the API into a large CRUD surface.

---

## UI Status

The primary UI workflow is **implemented (Step 6C)**: EVENT → RISK → SCENARIO → PROCUREMENT → EVIDENCE.

### Implemented UI (Step 6C)

- Dashboard shell with responsive layout (`App.jsx`)
- Event feed panel with semantic markers
- Corridor risk cards with display scores and risk levels
- Scenario simulator panel (30-day Hormuz disruption demo)
- Procurement recommendations panel
- Evidence drawer (Source → Extraction → Entity Resolution → Risk → Scenario → Optimization)
- Strategic reserves (SPR) panel
- Supply network summary (suppliers → routes → ports → refineries)
- `StatusBadge` for DERIVED, OBSERVED, UNAVAILABLE, LOADING states
- Loading, error, and retry handling
- Frontend calls real backend APIs — no fake demo data

### Not Yet Implemented

- Interactive India supply-network map
- Price/FX display panels (EIA/RBI integration deferred)
- Advanced visualizations and polish (Step 7 scope)

---

## Conceptual Domain Model

```
Country
├── Supplier (country_id FK)
│   └── crude_grade_ids → Crude Grade
├── Port (country_id FK)
└── Corridor (affected_countries)

Supplier → Route (supplier → origin_port → corridor(s) → destination_port)
Route → Corridor (corridor_ids[])

Refinery → Port (nearest_port_id FK)
Refinery → Refinery Supply Mix → Crude Grade

Geopolitical Event
├── affected_country_ids INT[]
├── affected_corridor_ids INT[]
└── affected_route_ids INT[]

Risk Score → Corridor | Route | Supplier

Scenario → Scenario Result
├── affected_refineries JSONB
├── spr_bridge JSONB
└── national supply gap

Procurement Option → Supplier + Route + Crude Grade + Scenario

Commodity Price (grade, price_usd, source_timestamp)
FX Rate (pair, rate, source_timestamp)

Evidence Record → Evidence Link (parent → child DAG)
Entity Alias → canonical_entity_type + canonical_entity_id
Data Source → status, classification
```

---

## Step 2 Summary — Architecture Freeze (COMPLETE)

Step 2 reconciled all Step-1 corrections into a frozen Phase-1 technical contract. Created `docs/02-architecture/ARCHITECTURE_DECISIONS.md` (ADR-001 through ADR-015). Marked frozen: `SYSTEM_ARCHITECTURE.md`, `DATABASE_SCHEMA.md`, `API_SPEC.md`.

**Architecture is frozen for Phase-1 implementation.**

### Frozen Architecture Summary

| Area | Decision |
|---|---|
| **Architecture pattern** | Monolithic: PostgreSQL + FastAPI + React |
| **Domain model** | 20 entities; corridors first-class; entity resolution layer; LLM outputs names not IDs |
| **Risk engine (Phase 1)** | Weighted deterministic formula (0.0–1.0 internal, 0–100 display) |
| **Risk engine (Phase 2)** | XGBoost disruption-probability candidate — NOT implemented |
| **LLM** | Abstraction layer; extraction + explanation only; **application LLM NOT SELECTED** |
| **NetworkX** | In-memory graph traversal only; PostgreSQL is source of truth |
| **Scenario engine** | Deterministic parametric; config in `config/scenario_assumptions.yaml` |
| **Procurement** | PuLP/scipy LP preferred; ranking fallback; compatibility threshold 0.5 |
| **Price/FX** | Separate `commodity_prices` + `fx_rates`; INR derived at query time |
| **Provenance** | `evidence_records` + `evidence_links` + `data_sources` |
| **Data semantics** | OBSERVED / DERIVED / HISTORICAL_CALIBRATED / ASSUMED / SIMULATED |
| **API boundary** | ~12 endpoint groups / 14 routes (see API_SPEC.md) |
| **UI boundary** | EVENT→RISK→SCENARIO→PROCUREMENT→EVIDENCE; Vanilla CSS |
| **Redis** | Excluded from Phase 1 |

### Canonical Domain Model

Entities: countries, corridors, suppliers, crude_grades, ports, routes, refineries, refinery_supply_mix, geopolitical_events, risk_scores, scenarios, scenario_results, procurement_options, strategic_reserves, commodity_prices, fx_rates, evidence_records, evidence_links, entity_aliases, data_sources.

Key flow: Geopolitical Event → countries/corridors/routes → Risk Score → Scenario → Procurement Option → Evidence chain.

### Out-of-Scope Technologies (Phase 1)

Kafka, Neo4j, MongoDB, Elasticsearch, ClickHouse, Kubernetes, microservices, blockchain, Redis, LSTM, GNN, reinforcement learning, vector databases, enterprise authentication, paid commercial feeds, real-time global AIS.

### Step-2 Resolved Items

U-2 Redis excluded · U-3 ACLED best-effort · U-4 RBI verify Day 1 · U-5 compatibility ≥0.5 · U-6 YAML config files · U-7 Vanilla CSS · U-8 confidence threshold 0.6 default.

### Remaining Open Item

| ID | Item | Status |
|---|---|---|
| U-8b | Final application LLM selection | OPEN — deferred to INDRA-specific benchmark (Step 7 or post-MVP) |

---

## Source Priority Rule

When resolving contradictions, use this priority:

1. Explicit decisions accepted in `PRE_STEP2_DECISIONS.md`
2. Accepted findings from `ARCHITECTURE_REVIEW.md`
3. Current corrected architecture documents
4. Research reports

If two research reports disagree and the review process did not resolve the disagreement: do NOT invent a resolution. Record it as an unresolved architecture decision.

---

## Key Documentation Reference

| Document | Purpose |
|---|---|
| `README.md` | Project overview |
| `docs/DEVELOPMENT_RULES.md` | **READ BEFORE ANY IMPLEMENTATION** |
| `docs/01-product/SOLUTION_OVERVIEW.md` | Product description, success criteria |
| `docs/01-product/MVP_SCOPE.md` | Feature classification: MUST/SHOULD/NICE/DO NOT |
| `docs/02-architecture/ARCHITECTURE_DECISIONS.md` | **Authoritative ADRs — read before implementation** |
| `docs/02-architecture/SYSTEM_ARCHITECTURE.md` | Technical architecture (FROZEN) |
| `docs/02-architecture/ARCHITECTURE_REVIEW.md` | Adversarial review findings |
| `docs/02-architecture/PRE_STEP2_DECISIONS.md` | Accepted corrections + unresolved decisions |
| `docs/03-frontend/UI_UX.md` | UI specification |
| `docs/04-backend/API_SPEC.md` | API endpoint specification |
| `docs/05-database/DATABASE_SCHEMA.md` | Conceptual database schema |
| `docs/06-data/DATA_SOURCES.md` | External data source documentation |
| `docs/07-ai-ml/AI_PIPELINE.md` | LLM extraction pipeline |
| `docs/07-ai-ml/ML_MODEL.md` | Risk model strategy (Phase 1 rules / Phase 2 XGBoost) |
| `docs/07-ai-ml/AI_MODEL_STRATEGY.md` | Development vs application model strategy |
| `docs/08-engines/SCENARIO_ENGINE.md` | Scenario computation specification |
| `docs/08-engines/OPTIMIZATION.md` | Procurement optimization specification |
| `docs/09-testing/TESTING.md` | Testing strategy |
| `docs/10-demo/DEMO_SCRIPT.md` | Demo script and judge Q&A |
| `research/research_report_1.md` | Primary research source (DO NOT rewrite) |
| `research/research_report_2.md` | Primary research source (DO NOT rewrite) |

---

## What Has NOT Been Done

- ✅ Data acquisition and seed datasets (Step 4)
- ✅ Entity resolution (Step 6A)
- ✅ Risk engine — weighted deterministic (Step 6B)
- ✅ Scenario engine — deterministic parametric (Step 6B)
- ✅ Optimization / procurement engine — ranking fallback (Step 6B)
- ✅ Dashboard with EVENT → RISK → SCENARIO → PROCUREMENT → EVIDENCE flow (Step 6C)
- ❌ LLM integration and final application-LLM selection
- ❌ Real-time data ingestion (GDELT, ACLED)
- ❌ EIA commodity prices API integration
- ❌ RBI FX bulk data integration
- ❌ PuLP/scipy linear programming for procurement
- ❌ Maps and advanced visualizations
- ❌ ML / XGBoost risk model
- ❌ Deployment infrastructure

---

## Step 3 Summary — Local Development Foundation (COMPLETE)

*Historical record — reflects Step 3 completion scope. Extended in Steps 5–6.*

Step 3 established a reproducible local foundation without implementing product features:

- Python 3.11+ virtual-environment workflow and a minimal dependency baseline: FastAPI, Uvicorn, Pydantic/Pydantic Settings, SQLAlchemy, and asyncpg.
- FastAPI application skeleton with local CORS and `GET /health` (the only endpoint at Step 3 completion).
- PostgreSQL-only Docker Compose development service with configurable credentials/database name, an exposed local port, named persistent volume, and health check. No Redis or other infrastructure was added.
- React/Vite startup shell using vanilla CSS, configured on port 3000 (no business API calls at Step 3 completion).
- `.env.example` placeholders for application, database, and future LLM provider/model settings.
- Windows PowerShell instructions in `docs/04-backend/DEVELOPMENT_SETUP.md` and `docs/03-frontend/DEVELOPMENT_SETUP.md`.

`db/schema.sql` and `db/seed.sql` were subsequently reconciled and applied in Step 5. Business APIs, engines, and dashboard were implemented in Step 6.

---

## How to Use This Context File

Before performing any development task:

1. Read `CONTEXT.md` (this file)
2. Read the relevant project documentation listed above
3. Follow `docs/DEVELOPMENT_RULES.md`
4. Check the **Current Development Status** table — do not assume later steps are complete
5. Do not invent missing architecture decisions
6. Do not expand scope without explicit approval

If documentation conflicts with this context:
- Inspect the active project documentation
- Do not silently rewrite architecture
- Report the conflict before implementing anything important

---

## Step 4 Summary — Data Foundation (COMPLETE)

*Historical record — reflects Step 4 completion scope.*

### Seed Datasets Created (11 files, 167 rows total)
- `data/seed/countries.csv` — 15 countries (India + supplier/transit nations)
- `data/seed/corridors.csv` — 6 Phase-1 corridors (HORMUZ, RED_SEA, SUEZ, MALACCA, RUSSIA, CAPE)
- `data/seed/crude_grades.csv` — 14 crude oil grades with API gravity/sulfur specs
- `data/seed/ports.csv` — 20 ports (10 Indian + 10 international)
- `data/seed/refineries.csv` — 20 Indian refineries with PPAC-sourced capacities
- `data/seed/suppliers.csv` — 8 major crude supplier entities
- `data/seed/refinery_supply_mix.csv` — 51 refinery-grade compatibility entries (all ESTIMATED)
- `data/seed/routes.csv` — 15 supply routes with distances and corridor refs
- `data/seed/spr.csv` — 3 ISPRL strategic reserve locations
- `data/seed/data_sources.csv` — 10 external data source registry entries
- `data/seed/scenarios.csv` — 5 preset disruption scenarios

### Historical / Reference Data
- OFAC SDN list downloaded (5.4 MB raw; 1,674 energy-relevant entities extracted; status: ACQUIRED)
- RBI FX: 3 real reference-rate data points documented (status: PARTIAL; RBI has no bulk CSV API; full historical requires manual DBIE portal download)
- EIA commodity prices: not acquired (status: REQUIRES_REGISTRATION; free API key at api.eia.gov)

### Schema Reconciliation
- `db/schema.sql` reconciled with frozen `DATABASE_SCHEMA.md` (added corridors, crude_grades, refinery_supply_mix, fx_rates, evidence tables; removed deprecated columns)
- `db/seed.sql` generated from seed CSVs with proper INSERT statements

### Provenance
- `data/metadata/data_manifest.json` — 17 dataset entries with checksums and source metadata
- `data/metadata/historical_acquisition.json` — acquisition execution log

### Validation
- All seed datasets pass validation (0 errors, 167 rows)
- All historical datasets pass validation (0 errors, 1,677 rows)
- Cross-dataset referential integrity verified

### Scripts Created
- `scripts/data/validate_seed_data.py`
- `scripts/data/validate_historical_data.py`
- `scripts/data/load_seed_data.py`
- `scripts/data/acquire_historical_data.py`

### Documentation Created
- `docs/06-data/DATA_ACQUISITION_PLAN.md` (Phase A)
- `docs/06-data/DATA_ACQUISITION_REPORT.md` (Phase B)

### Deferred Sources
- GDELT: deferred to event-ingestion step
- ACLED: deferred to event-ingestion step
- EIA prices: deferred until API key registration
- RBI bulk FX: deferred until manual DBIE download

### Data Semantic Compliance
- All data_semantic values use frozen schema classifications: OBSERVED, DERIVED, HISTORICAL_CALIBRATED, ASSUMED, SIMULATED
- All ESTIMATED values explicitly labeled with methodology
- All UNKNOWN/NULL values documented
- No fabricated values exist
- SIMULATED data never represented as live data
- GDELT/ACLED documented as DEFERRED only

*At Step 4 completion, the following remained deferred: external LLM provider connection, live event ingestion, engines, frontend dashboard, ML, deployment. These were addressed in Step 6 (except external LLM provider, live ingestion, ML, and deployment).*

---

## Step 5 Summary — PostgreSQL Implementation + Verified Data Loading (COMPLETE)

*Historical record — reflects Step 5 completion scope. Business features were added in Step 6.*

- PostgreSQL 16 container is healthy through Docker Compose.
- Frozen schema applied successfully after correcting the `data_sources.classification` width required by the frozen `HISTORICAL_CALIBRATED` semantic label.
- Verified seed data loaded: 15 countries, 6 corridors, 14 crude grades, 20 ports, 20 refineries, 8 suppliers, 51 refinery-supply-mix rows, 15 routes, 3 strategic reserves, 10 data sources, and 5 scenarios.
- All 20 required tables exist; primary keys, foreign-key spot checks, array references, ranges, coordinates, semantic labels, NULL semantics, and orphan checks passed (90 checks).
- SQLAlchemy async connectivity and FastAPI `/health` database status both report PostgreSQL connected.
- Initialization and reset/reseed are reproducible through `scripts/db/init_db.py` and `scripts/db/reset_db.py`; generated seed SQL is conflict-safe on repeated initialization.
- Minimal Alembic structure is prepared with no invented migration; `db/schema.sql` remains authoritative.
- No business APIs or feature engines were implemented at Step 5 completion (added in Step 6).

## Step 6A Summary — Core Backend Domain Layer (COMPLETE)

- Added SQLAlchemy mappings for the frozen reference/domain tables, including countries, corridors, crude grades, ports, refineries, suppliers, refinery supply mix, routes, strategic reserves, data sources, scenarios, and entity aliases.
- Added Pydantic response schemas with nullable fields and semantic/data provenance fields where applicable.
- Added repository/service boundaries for read-only reference data and reserves aggregation.
- Added exact canonical/alias matching with configurable RapidFuzz fallback at the frozen 85% threshold; unresolved values return an explicit unresolved result and are never inserted.
- Implemented only read-only endpoints: `/health`, `/countries`, `/corridors`, `/crude-grades`, `/routes`, `/refineries`, `/suppliers`, and `/reserves`.
- Added backend tests for seeded API responses, invalid corridor filtering, exact/fuzzy/unresolved entity resolution. Current suite: 3 passed.
- Removed hard-coded database URL/password fallbacks from application and database scripts; credentials must be supplied through environment variables.

## Step 6B Summary — Event Intelligence and Risk (COMPLETE)

Step 6B implemented the provider-neutral structured event contract with bounded timeout/retries and validation, Step-6A-compatible entity resolution, deterministic weighted risk scoring, NetworkX supply-graph primitives, scenario supply-gap simulation, procurement ranking fallback, provenance/evidence-chain metadata, and narrow FastAPI intelligence endpoints.

### What Was Implemented
- **LLM Provider Abstraction**: `LLMProvider` protocol with `UnconfiguredLLMProvider` (safe default) and `CallableLLMProvider` (adapter for caller-supplied functions with timeout/retries)
- **Structured Event Contract**: `StructuredEvent` model with validation that rejects database IDs (LLM outputs names only)
- **Entity Resolution Integration**: `resolve_structured_event` joins LLM output to entity resolution
- **Phase-1 Weighted Deterministic Risk Engine**: `calculate_risk` with configurable `RiskWeights` (0.0–1.0 internal, 0–100 display)
- **Risk Classification**: LOW (<0.30), MODERATE (0.30–0.49), HIGH (0.50–0.69), CRITICAL (0.70–0.84), EXTREME (≥0.85)
- **NetworkX Graph Operations**: `build_supply_graph` for in-memory traversal, `affected_refineries` for corridor disruption analysis
- **Deterministic Scenario Engine**: `scenario_supply_gap` calculates supply gap from corridor disruption scenarios
- **Procurement Ranking Fallback**: `rank_procurement` with compatibility threshold (0.5 default), sanctions exclusion, cost+risk ranking
- **Evidence Chain Builder**: `build_evidence_chain` creates provenance DAG from source → extraction → entity_resolution → risk → scenario → optimization

### API Endpoints Added
- `POST /events` — Submit structured event, resolve entities, return evidence chain
- `GET /events` — Event feed (returns empty list with semantic marker)
- `GET /corridors/risk` — Corridor risk scores from seed data
- `POST /risk` — Calculate risk from feature vector
- `GET /risk` — Risk summary
- `POST /scenarios` — Run scenario simulation
- `POST /recommendations` — Get procurement recommendations

### Tests Added
- `test_structured_event_rejects_database_ids` — Validates LLM boundary
- `test_risk_formula_and_thresholds_are_deterministic` — Validates risk calculation
- `test_scenario_and_optimizer_semantics_and_constraints` — Validates scenario and procurement

**Current test suite: 6 passed (3 domain + 3 intelligence)**

## Step 6C Summary — Frontend Dashboard (COMPLETE)

Step 6C implemented the React/Vite dashboard with the full EVENT → RISK → SCENARIO → PROCUREMENT → EVIDENCE workflow, semantic state indicators, evidence presentation, and end-to-end backend integration.

### What Was Implemented
- **React/Vite Dashboard**: Full application shell with responsive layout
- **API Client**: `api.js` with timeout handling, error handling, and methods for risk/scenario/recommendations
- **Event UI**: Event feed panel with semantic markers
- **Corridor Risk UI**: Corridor risk cards with display scores and risk levels
- **Scenario Simulator**: Panel for running 30-day Hormuz disruption scenario
- **Procurement Recommendations**: Panel showing feasibility, unmet volume, selected candidates
- **Evidence Drawer**: Visual chain showing Source → Extraction → Entity Resolution → Risk → Scenario → Optimization
- **Strategic Reserves**: Panel showing SPR locations and levels
- **Supply Network View**: Summary of suppliers → routes → ports → refineries
- **Semantic States**: StatusBadge component for DERIVED, OBSERVED, UNAVAILABLE, LOADING states
- **Error Handling**: Error alerts with retry functionality
- **Loading States**: Busy indicator during flow execution

### Frontend Architecture
- Vanilla CSS (no Tailwind/UI framework)
- No frontend recalculation of backend-derived values
- All computed values come from backend APIs
- Semantic markers on all derived data

### End-to-End Flow Verified
1. Backend APIs respond correctly to all endpoints
2. Frontend calls backend for risk, scenario, and recommendations
3. Results display with semantic markers
4. Evidence chain is presented visually

## Step 6 Verification Summary (21 August 2026)

### Tests Run
- Backend: 6 passed (3 domain + 3 intelligence)
- Frontend: Build successful

### Architecture Compliance Verified
- ✅ No forbidden architecture changes (Kafka, Neo4j, MongoDB, etc. excluded)
- ✅ XGBoost NOT presented as Phase 1 (correctly documented as Phase 2 candidate)
- ✅ LLM does NOT perform deterministic calculations (LLM only for extraction)
- ✅ No fabricated data (all seed data documented with sources)
- ✅ No fake frontend demo data (frontend uses real backend APIs)
- ✅ Risk engine is weighted deterministic (not ML/XGBoost)
- ✅ Scenario engine is deterministic parametric
- ✅ Procurement uses ranking fallback (not PuLP/scipy yet)
- ✅ Entity resolution uses exact alias + RapidFuzz fuzzy (no vector DB)
- ✅ PostgreSQL is source of truth
- ✅ NetworkX for in-memory traversal only

### Data Semantic Compliance
- All computed values marked DERIVED
- Observed values marked OBSERVED
- No SIMULATED data represented as live
- NULL values preserved (not fabricated)

## Step 6 Boundary

> **STEP 6 COMPLETE (6A + 6B + 6C).**
>
> Step 6 delivered: core backend domain layer, event intelligence and risk engines, and the React/Vite dashboard with end-to-end workflow. Step 7 must not start without explicit user direction.

## Step 7 Boundary

> **STEP 7 HAS NOT STARTED.**
>
> Step 7 scope (Polish and Demo Preparation) may include: demo script rehearsal, UI polish, map/visualization enhancements, price/FX panels (if data available), documentation updates, and final application-LLM benchmark. Do not start Step 7 without explicit user direction.
