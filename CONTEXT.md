# INDRA — Project Context & Handoff Document

> **Purpose:** Durable context file for AI development agents taking over the INDRA project.
>
> **Date:** 21 August 2026
>
> **Development State:** Step 0 COMPLETE · Step 1 COMPLETE · Step 2 COMPLETE · Step 3 COMPLETE · Step 4 COMPLETE · Step 5 NOT STARTED

---

## Project

**INDRA — India Disruption Response Architecture**

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
| **Step 5** | Feature Implementation | ❌ NOT STARTED |

> **Architecture is frozen for Phase-1 implementation.** Step 4 established the India-specific data foundation. Step 5 must not start without explicit user direction.

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
├── backend/                            ← FastAPI development foundation exists; /health endpoint implemented; business API routes not implemented
├── frontend/                           ← React/Vite development foundation exists; basic application shell exists; business dashboard/features not implemented
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
| **Phase 1** | Weighted deterministic risk engine |
| **Phase 2 candidate** | XGBoost disruption-probability model |

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

The application must use a **provider abstraction** so the model can be changed without rewriting application code.

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

Scenario computation is **deterministic and parametric**.

It may calculate: disrupted capacity, affected supply, refinery impact, inventory pressure, national supply gap, SPR support requirement, procurement gap, modeled cost effects.

Every important scenario value must be classified using the five semantic categories.

The LLM is NOT responsible for scenario mathematics.

---

## Procurement Engine Status

| Approach | Description |
|---|---|
| **Preferred (Phase 1)** | PuLP/scipy linear programming |
| **Fallback** | Deterministic weighted ranking |

Potential constraints: supplier availability, route capacity, sanctions, crude compatibility, transit time, disrupted routes, required supply volume.

LLM may explain the result but must NOT generate the numerical optimization result.

---

## API Status

The current API is still a **specification** (not implemented).

The intended MVP is deliberately small (~12 endpoint groups):
- events, corridor risk, routes, refineries, reserves, prices, scenarios, recommendations, evidence, health

Do NOT expand the API into a large CRUD surface.

Step 2 has NOT frozen the final API contract yet.

---

## UI Status

The primary UI workflow: EVENT → RISK → SCENARIO → PROCUREMENT → EVIDENCE

Planned UI includes: risk dashboard, corridor risk cards, event feed, India supply-network map, scenario simulator, procurement recommendations, evidence drawer, SPR information, price/FX information, data-semantic indicators.

Do NOT build the frontend yet.

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
| U-8b | Final application LLM selection | OPEN — deferred to INDRA-specific benchmark during Step 3 |

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
- ❌ LLM integration and final application-LLM selection
- ❌ Entity resolution
- ❌ Risk engine
- ❌ Scenario engine
- ❌ Optimization / procurement engine
- ❌ Real dashboard (maps, charts, risk cards, simulator, recommendations, evidence drawer)
- ❌ ML
- ❌ Deployment

---

## Step 3 Summary — Local Development Foundation (COMPLETE)

Step 3 established a reproducible local foundation without implementing product features:

- Python 3.11+ virtual-environment workflow and a minimal dependency baseline: FastAPI, Uvicorn, Pydantic/Pydantic Settings, SQLAlchemy, and asyncpg.
- FastAPI application skeleton with local CORS and the sole implemented endpoint, `GET /health`. The endpoint reports PostgreSQL connectivity without exposing credentials.
- PostgreSQL-only Docker Compose development service with configurable credentials/database name, an exposed local port, named persistent volume, and health check. No Redis or other infrastructure was added.
- React/Vite startup shell using vanilla CSS, configured on port 3000. It makes no business API calls.
- `.env.example` placeholders for application, database, and future LLM provider/model settings; no real `.env`, API keys, or secrets were added.
- Windows PowerShell instructions in `docs/04-backend/DEVELOPMENT_SETUP.md` and `docs/03-frontend/DEVELOPMENT_SETUP.md`; README and testing documentation reflect the foundation scope.

`db/schema.sql` and `db/seed.sql` remain planned review artifacts. They were not deployed and no fabricated data was inserted.

**Review note:** `db/schema.sql` is syntactically structured PostgreSQL DDL, but it still reflects the pre-freeze model (for example, it lacks the frozen `corridors` table and uses the older price table names). It must be reconciled with the frozen database documentation in its own authorized implementation step before any schema deployment; Step 3 did not change or execute it.

**NOT IMPLEMENTED YET:** data acquisition; external API ingestion; LLM integration; entity resolution; risk engine; scenario engine; optimization; real dashboard; ML; deployment.

---

## How to Use This Context File

Before performing any development task:

1. Read `CONTEXT.md` (this file)
2. Read the relevant project documentation listed above
3. Follow `docs/DEVELOPMENT_RULES.md`
4. Do not assume later steps are complete
5. Do not invent missing architecture decisions
6. Do not expand scope without explicit approval

If documentation conflicts with this context:
- Inspect the active project documentation
- Do not silently rewrite architecture
- Report the conflict before implementing anything important

---

## Step 4 Summary — Data Foundation (COMPLETE)

Step 4 created the India-specific supply-chain data foundation:

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
- OFAC SDN list downloaded (5.4 MB raw; 1,674 energy-relevant entities extracted)
- RBI FX sample format file created (bulk download requires manual DBIE access)
- EIA commodity prices: REQUIRES_REGISTRATION (free API key at api.eia.gov)

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

### Data Honesty
- All ESTIMATED values explicitly labeled with methodology
- All UNKNOWN/NULL values documented
- No fabricated values exist
- SIMULATED data never represented as live data
- GDELT/ACLED documented as DEFERRED only

**NOT IMPLEMENTED:** LLM integration; entity resolution; risk engine; scenario engine; optimization; frontend dashboard; ML; deployment.

---

## Step 5 Boundary

> **STEP 5 HAS NOT STARTED.**
>
> Do not:
> - Implement business features without explicit user direction
> - Integrate external data services or an LLM
> - Implement entity resolution or any engine
> - Build dashboard views or deployment infrastructure
>
> The user will explicitly initiate Step 5.
