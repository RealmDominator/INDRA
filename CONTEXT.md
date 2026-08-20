# INDRA — Project Context & Handoff Document

> **Purpose:** Durable context file for AI development agents taking over the INDRA project.
>
> **Date:** 20 August 2026
>
> **Development State:** Step 0 COMPLETE · Step 1 COMPLETE · Step 2 NOT STARTED

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
| **Step 2** | Architecture Freeze | ❌ NOT STARTED |
| Step 3+ | Implementation | ❌ NOT STARTED |

> **IMPORTANT:** The project MUST remain at the boundary between Step 1 and Step 2 until the user explicitly starts Step 2. Do NOT assume the architecture freeze has happened. Do NOT mark architecture as finally frozen.

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
│   │   ├── SYSTEM_ARCHITECTURE.md
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
├── backend/                            ← empty, not implemented
├── frontend/                           ← empty, not implemented
├── data/                               ← empty, no datasets acquired
├── ml/                                 ← empty, no models trained
├── prompts/                            ← empty
├── db/                                 ← empty, no migrations
├── scripts/                            ← empty
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

## Unresolved Decisions (from PRE_STEP2_DECISIONS.md)

These must be resolved during Step 2:

| ID | Question | Status |
|---|---|---|
| U-1 | NetworkX vs SQL Joins | ✅ RESOLVED — NetworkX confirmed |
| U-2 | Redis in Phase 1 | ❌ OPEN — recommendation: remove |
| U-3 | ACLED Availability | ❌ OPEN — treat as best-effort |
| U-4 | RBI API Verification | ❌ OPEN — verify Day 1, fallback: hardcoded rate |
| U-5 | Compatibility Threshold | ❌ OPEN — recommendation: 0.5 default |
| U-6 | Scenario Configuration Source | ❌ OPEN — config file vs DB table |
| U-7 | Frontend CSS Framework | ❌ OPEN — system rules specify Vanilla CSS |
| U-8 | Event Confidence Threshold | ❌ OPEN — current default: 0.6 |

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
| `docs/02-architecture/SYSTEM_ARCHITECTURE.md` | Technical architecture specification |
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

- ❌ Step 2 Architecture Freeze
- ❌ ARCHITECTURE_DECISIONS.md creation
- ❌ Environment setup for implementation
- ❌ PostgreSQL implementation
- ❌ Redis implementation
- ❌ Real external API integration
- ❌ Dataset acquisition
- ❌ LLM benchmark
- ❌ LLM provider implementation
- ❌ Entity resolution implementation
- ❌ Risk engine implementation
- ❌ Scenario engine implementation
- ❌ Optimization engine implementation
- ❌ FastAPI implementation
- ❌ React implementation
- ❌ ML experimentation
- ❌ Deployment

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

## Step 2 Boundary

> **STEP 2 HAS NOT STARTED.**
>
> Do not:
> - Perform architecture freeze
> - Create ARCHITECTURE_DECISIONS.md
> - Mark the architecture as FROZEN
> - Finalize the API contract
> - Finalize the database implementation
> - Finalize the application LLM
> - Start implementation
>
> The user will explicitly initiate Step 2.
