# INDRA — Architecture Decision Records (Phase 1)

> **Status:** ACCEPTED — Frozen for Phase-1 implementation  
> **Date:** 20 August 2026  
> **Authority:** Step 2 Architecture Freeze  
> **Source priority:** PRE_STEP2_DECISIONS.md → ARCHITECTURE_REVIEW.md → active specifications → research reports

This document is the authoritative Phase-1 technical contract. Implementation agents MUST follow these decisions. Do not introduce alternatives without an explicit future architecture review.

---

## ADR-001: PostgreSQL Single-Database Architecture

**Status:** ACCEPTED

**Context:** INDRA stores reference entities, events, market data, scenario outputs, and provenance in one system. Demo volumes are small (~hundreds of events, ~20 refineries, ~50 routes). Research reports and the architecture review both conclude multi-database complexity is unnecessary for Phase 1.

**Decision:** Use a **single PostgreSQL 16 instance** as the persistent source of truth for all structured data. Semi-structured fields use JSONB. Coordinates use plain `DECIMAL` lat/lon columns. No PostGIS, TimescaleDB, or secondary databases in Phase 1.

**Consequences:**
- Simpler deployment, backup, and development for a single student developer
- Graph traversal and optimization run in Python; PostgreSQL stores entities and results
- All foreign-key relationships and provenance chains live in one database

**Explicitly out-of-scope alternatives:**
- MongoDB, ClickHouse, Elasticsearch
- Neo4j (graph persistence)
- Multi-database or read-replica architecture
- PostGIS (deferred to Phase 2 if spatial queries become necessary)

---

## ADR-002: FastAPI + React Monolith

**Status:** ACCEPTED

**Context:** Phase 1 is a hackathon MVP with one developer and ~4 days. Microservices, event buses, and distributed deployment add complexity without demo value.

**Decision:** Deploy as a **monolithic Phase-1 architecture**:
- **Backend:** Single FastAPI application (Python 3.11) with APScheduler background jobs
- **Frontend:** Single React SPA (React 18 + React-Leaflet + Recharts)
- **Communication:** HTTPS REST JSON API only
- **Authentication:** None in Phase 1

**Consequences:**
- One codebase, one deployment unit, one API surface
- All engines (risk, scenario, procurement, SPR) are Python modules invoked by FastAPI
- Frontend consumes ~12 MVP endpoint groups documented in API_SPEC.md

**Explicitly out-of-scope alternatives:**
- Microservices decomposition
- Kubernetes orchestration
- Mobile application
- Enterprise SSO / SAP integration
- gRPC / GraphQL (REST only for Phase 1)

---

## ADR-003: Corridor-First Domain Model

**Status:** ACCEPTED

**Context:** The architecture review identified corridors as the primary risk-dashboard entity but they were missing from the original schema. LLM extraction outputs corridor names; risk scores are corridor-centric.

**Decision:** **Corridors are first-class entities** stored in the `corridors` table with stable codes (`HORMUZ`, `RED_SEA`, `SUEZ`, `MALACCA`, `RUSSIA`, `CAPE`). A corridor represents a strategic supply-chain/geopolitical pathway or chokepoint region used for risk analysis — not a free-form string in a news article.

Phase-1 corridor set: HORMUZ, RED_SEA, SUEZ, MALACCA, RUSSIA, CAPE.

Relationships:
- `geopolitical_events.affected_corridor_ids` → corridors
- `geopolitical_events.affected_country_ids` → countries
- `geopolitical_events.affected_route_ids` → routes (optional; zero or more)
- `routes.corridor_ids` → corridors traversed by the route
- `risk_scores` polymorphic on corridor, route, supplier, country

**Consequences:**
- Corridor-level risk is calculable, storable, and API-exposable
- No separate `chokepoints` table; chokepoint-type corridors use `corridor_type = CHOKEPOINT`
- Map UI renders corridors from the same entity model as the risk dashboard

**Explicitly out-of-scope alternatives:**
- Corridor-only-as-string modeling in events or risk tables
- Separate chokepoint database unless explicitly required later
- LLM output of internal corridor database IDs

---

## ADR-004: Entity Resolution Layer

**Status:** ACCEPTED

**Context:** LLMs output human-readable names (`"Iran"`, `"HORMUZ"`, `"Saudi Aramco"`). Database rows use integer IDs. There is no Phase-1 capacity for enterprise entity resolution.

**Decision:** Insert an explicit **entity resolution layer** between LLM extraction and database persistence:

```
LLM output (names/codes)
  → Pydantic schema validation
  → entity resolution (entity_aliases exact match → RapidFuzz ≥85% → unresolved log)
  → internal IDs
  → PostgreSQL
```

Phase-1 scope: ~50–100 pre-populated aliases in `entity_aliases`.

**Consequences:**
- The LLM never produces or receives internal database IDs
- Unresolved entities are logged; bad FK references are not inserted
- Fuzzy matching is deterministic (RapidFuzz threshold), not embedding-based

**Explicitly out-of-scope alternatives:**
- Vector databases / embedding similarity for Phase 1
- Full enterprise entity-resolution engine
- LLM-assigned database IDs
- Neo4j entity graph

---

## ADR-005: LLM Abstraction / Provider Architecture

**Status:** ACCEPTED

**Context:** The application LLM is not yet selected. Provider APIs differ; the hackathon must support swapping models after INDRA-specific benchmarking.

**Decision:** All runtime LLM usage goes through an **abstracted provider interface** supporting:
- Event extraction (structured JSON)
- Explanation generation (from validated results only)
- Model metadata for evidence records
- Timeout/retry handling (15s timeout, max 2 retries on malformed JSON)
- Structured-output validation (Pydantic)
- Provider/model swapping without application rewrites

**Application LLM status:** **NOT SELECTED.** Benchmark pool (candidates only):
- GPT-5.6 Terra / Luna
- Kimi K2.6
- GLM 5.2
- MiniMax M3
- Nemotron 3 Super / Nano / Lightning
- Suitable OpenRouter free candidates
- Claude (optional quality/reference benchmark only)

**Consequences:**
- Direct provider SDK calls from business logic are prohibited
- Final model chosen later via INDRA-specific benchmark (≥90% valid JSON threshold)
- Development-agent models and application LLM remain separate decisions

**Explicitly out-of-scope alternatives:**
- Hard-coding a single provider in application code
- Selecting the final application LLM during Step 2
- Using the LLM for numerical computation or optimization

---

## ADR-006: Phase-1 Weighted Deterministic Risk Engine

**Status:** ACCEPTED

**Context:** Research reports disagree on XGBoost in Phase 1. The master report and review conclude explainable rules are more defensible for a 4-day demo.

**Decision:** Phase-1 risk scoring is a **weighted deterministic risk engine**, not ML.

Default formula (configuration-driven via `config/risk_weights.yaml`):
```
risk = 0.25×event_severity + 0.20×event_recency + 0.20×chokepoint_exposure
     + 0.15×conflict_sanctions + 0.10×historical_rate + 0.10×india_dependency
```

Risk representation:
- **Internal:** 0.0–1.0 (storage and computation)
- **Display/API:** 0–100 via `display_score = internal_score × 100`

The engine MUST expose component contributions and calculation provenance via `evidence_records`. The LLM MUST NOT calculate risk scores.

**Consequences:**
- Reproducible, auditable scores for judges
- `RiskEngine` interface allows Phase-2 model drop-in
- Weights changeable without code changes

**Explicitly out-of-scope alternatives:**
- XGBoost or any trained model as Phase-1 risk scorer
- LLM-generated risk numbers
- Black-box scores without component breakdown

---

## ADR-007: Phase-2 XGBoost Extension

**Status:** ACCEPTED (future phase — not implemented in Phase 1)

**Context:** PETRAS proposes XGBoost disruption classification as optional; INDRA Master defers to Phase 2. Architecture should remain ML-ready.

**Decision:** **Phase 2 candidate:** XGBoost disruption-probability model (`XGBoostRiskEngine` implementing `RiskEngine`). Binary classification using ACLED + EIA historical features with temporal cross-validation and SHAP explanations.

Phase 1: **Do not train or deploy XGBoost.** Document as roadmap only.

**Consequences:**
- Demo does not depend on unvalidated ML metrics
- `calculation_method` field on `risk_scores` supports `"weighted_rule_v1"` now and `"xgboost_v1"` later
- ML tests in TESTING.md are Phase-2 only

**Explicitly out-of-scope for Phase 1:**
- Training XGBoost during hackathon
- Claiming ML accuracy without evaluation artifacts
- LSTM, GNN, reinforcement learning, custom transformers

---

## ADR-008: NetworkX Responsibilities

**Status:** ACCEPTED

**Context:** NetworkX role was underspecified. Scenario engine docs mixed graph traversal with parametric arithmetic.

**Decision:** NetworkX is an **in-memory supply graph** built from PostgreSQL at runtime. Phase-1 responsibilities:

| NetworkX IS responsible for | NetworkX is NOT responsible for |
|---|---|
| Supplier → route → port → refinery traversal | Persistent storage (PostgreSQL) |
| Reachability analysis | Risk score calculation |
| Affected-refinery discovery given disrupted corridors/routes | Scenario arithmetic |
| Alternate route discovery | Procurement optimization |
| Graph-based disruption propagation inputs to scenario engine | LLM or ML inference |

PostgreSQL remains the source of truth. The scenario engine receives entity lists from NetworkX and applies deterministic formulas.

**Explicitly out-of-scope alternatives:**
- NetworkX as database replacement
- Neo4j for Phase 1
- Scenario engine performing its own graph traversal

---

## ADR-009: Deterministic Scenario Engine

**Status:** ACCEPTED

**Context:** Scenario outputs must be reproducible, labeled, and defensible. LLM reasoning is inappropriate for volume/cost arithmetic.

**Decision:** Scenario computation is **deterministic, parametric, and reproducible**. Preset scenarios loaded from `config/scenario_assumptions.yaml` (changeable without code edits).

The engine calculates: capacity disruption, supply impact, refinery impact, inventory pressure, national supply gap, SPR support requirement, alternative procurement requirement, modeled cost impact.

Every output value carries a data-semantic label: OBSERVED / DERIVED / HISTORICAL_CALIBRATED / ASSUMED / SIMULATED.

The LLM MUST NOT perform scenario mathematics. Scenario outputs MUST NOT be presented as predictions of actual future events.

**GDP impact:** Removed from scope (requires macroeconomic modeling).

**Explicitly out-of-scope alternatives:**
- LLM scenario reasoning
- Discrete-event simulation engine
- 3D digital twin visualization
- Claiming scenario outputs as measured inventory or official government figures

---

## ADR-010: Procurement Optimization

**Status:** ACCEPTED

**Context:** Procurement is a core differentiator. It must be algorithmic and change with scenario inputs.

**Decision:** Procurement uses **deterministic optimization**:

| Priority | Method |
|---|---|
| Preferred | PuLP or `scipy.optimize.linprog` linear programming |
| Fallback | Deterministic weighted ranking |

Constraints include: supplier availability, route capacity, sanctions, crude compatibility (`refinery_supply_mix`, threshold ≥ 0.5 — see ADR resolution U-5), transit time, disrupted corridors/routes, supply-gap requirement.

The LLM may explain results but MUST NOT generate numerical optimization output.

**Explicitly out-of-scope alternatives:**
- LLM-generated procurement rankings
- Hardcoded static recommendations
- Reinforcement learning for procurement

---

## ADR-011: Price / FX Separation

**Status:** ACCEPTED

**Context:** EIA and RBI pollers operate independently. A PostgreSQL GENERATED column synchronizing USD price and INR rate in one row was invalid.

**Decision:** Maintain **independent observation streams**:
- `commodity_prices` — EIA (and similar) USD prices
- `fx_rates` — RBI USD/INR rates

INR valuation is **derived at query time** using the **nearest-valid-prior FX rate** alignment rule:
1. Commodity price at source timestamp T₁
2. FX rate with max `source_timestamp` ≤ T₁
3. `price_inr = price_usd × fx_rate`
4. Provenance recorded in evidence chain (both timestamps, method ID)

**Explicitly out-of-scope alternatives:**
- Synchronized EIA/RBI in one generated DB column
- LLM-generated prices or FX rates
- Storing derived INR as the authoritative price without provenance

---

## ADR-012: Provenance / Evidence Architecture

**Status:** ACCEPTED

**Context:** Explainability is a product requirement and hackathon differentiator.

**Decision:** Implement a first-class evidence chain:

```
Source → ingestion → LLM extraction → entity resolution → risk calculation
  → scenario computation → optimization → recommendation
```

Tables:
- `evidence_records` — individual provenance nodes
- `evidence_links` — parent→child DAG edges
- `data_sources` — external feed registry and freshness

Every important result (risk score, scenario result, procurement option) MUST be traceable via `/evidence/{entity_type}/{entity_id}`.

**Explicitly out-of-scope alternatives:**
- Scores or recommendations without evidence paths
- Provenance stored only in unstructured logs

---

## ADR-013: Data Semantic Classification

**Status:** ACCEPTED

**Context:** Previous LIVE/RECENT/HISTORICAL terminology was ambiguous. Judges must distinguish observed data from modeled outputs.

**Decision:** Freeze these **exact canonical labels** in all active specifications:

| Category | Definition |
|---|---|
| **OBSERVED** | Directly fetched from external source |
| **DERIVED** | Calculated from observed values via documented formula |
| **HISTORICAL_CALIBRATED** | Parameter from historical event analysis |
| **ASSUMED** | Configuration or user assumption |
| **SIMULATED** | Synthetic state for scenario/demo |

Rules:
- SIMULATED data MUST NOT be represented as live
- UI badges reflect these five categories
- Historical review documents may retain older terminology

**Explicitly out-of-scope alternatives:**
- LIVE / RECENT as active semantic labels
- Unlabeled calculated outputs in the UI

---

## ADR-014: MVP API Boundary

**Status:** ACCEPTED

**Context:** Original API had ~30 endpoints — excessive for one developer. Demo requires ~12 operation groups.

**Decision:** Freeze MVP API at **12 endpoint groups** (~14 routes):

| # | Method | Path | Purpose |
|---|---|---|---|
| 1 | GET | `/health` | System and data-source health |
| 2 | GET | `/events` | Recent geopolitical events |
| 3 | GET | `/events/{id}` | Event detail + provenance |
| 4 | GET | `/risk/corridors` | All corridor risk scores |
| 5 | GET | `/risk/corridors/{corridor_code}` | Corridor risk breakdown |
| 6 | GET | `/routes` | Supply routes for map |
| 7 | GET | `/refineries` | Refineries + compatibility summary |
| 8 | GET | `/reserves` | SPR status |
| 9 | GET | `/prices/current` | Prices + FX + derived INR |
| 10 | GET | `/scenarios/presets` | Preset scenario list |
| 11 | POST | `/scenarios/run` | Run scenario simulation |
| 12 | GET | `/recommendations/{scenario_id}` | Procurement recommendations |
| 13 | GET | `/evidence/{entity_type}/{entity_id}` | Provenance chain |

Base URL: `/api/v1`. No authentication. Risk scores returned on 0–100 display scale.

Full contract: [API_SPEC.md](../04-backend/API_SPEC.md).

**Explicitly out-of-scope for Phase-1 API:**
- Full CRUD on all entities
- `/suppliers`, `/events/extract`, `/prices/history`, enterprise admin endpoints
- API scope expansion without explicit approval

---

## ADR-015: MVP UI Boundary

**Status:** ACCEPTED

**Context:** UI must support one demo loop without unnecessary pages.

**Decision:** Freeze primary workflow:

**EVENT → RISK → SCENARIO → PROCUREMENT → EVIDENCE**

Required UI components only:
- Risk overview dashboard (corridor cards)
- Event feed
- India supply network map (Leaflet)
- Scenario simulator
- Procurement results table
- Evidence drawer (global, via "Why?" links)
- SPR display
- Price/FX display
- Semantic data indicators (five categories)
- Stale-data, loading, error, empty, demo-mode states

Navigation: Risk Overview | Supply Map | Scenario | Procurement + Evidence drawer.

**CSS:** Vanilla CSS for Phase 1 (no Tailwind unless explicitly requested later).

**Explicitly out-of-scope UI:**
- Mobile app
- 3D globe / cosmetic digital twin
- Fake live AIS tanker positions
- Extra dashboards or admin pages

Full contract: [UI_UX.md](../03-frontend/UI_UX.md).

---

## Step-2 Resolution of Pre-Step-2 Open Items

| ID | Decision | Status |
|---|---|---|
| U-1 | NetworkX confirmed for graph traversal | RESOLVED (Step 1) |
| U-2 | **Redis excluded from Phase 1** — remove from docker-compose; direct PostgreSQL queries | RESOLVED |
| U-3 | **ACLED best-effort** — system functions with GDELT + RSS + OFAC if ACLED unavailable | RESOLVED |
| U-4 | **RBI verify Day 1** — fallback: hardcoded recent USD/INR labeled HISTORICAL_CALIBRATED | RESOLVED |
| U-5 | **Compatibility threshold default 0.5** (MEDIUM+ included); configurable | RESOLVED |
| U-6 | **Scenario/risk config via YAML files** in `config/` (not DB table for Phase 1) | RESOLVED |
| U-7 | **Vanilla CSS** for Phase-1 frontend | RESOLVED |
| U-8 | **LLM confidence threshold default 0.6**; tunable in config; may adjust during LLM benchmark | RESOLVED (default frozen; benchmark may tune) |

---

## Canonical Domain Model (Phase 1)

Entities: `countries`, `corridors`, `suppliers`, `crude_grades`, `ports`, `routes`, `refineries`, `refinery_supply_mix`, `geopolitical_events`, `risk_scores`, `scenarios`, `scenario_results`, `procurement_options`, `strategic_reserves`, `commodity_prices`, `fx_rates`, `evidence_records`, `evidence_links`, `entity_aliases`, `data_sources`.

Key relationships are defined in [DATABASE_SCHEMA.md](../05-database/DATABASE_SCHEMA.md) and [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md).

---

## Explicitly Out-of-Scope Technologies (Phase 1)

Kafka · Neo4j · MongoDB · Elasticsearch · ClickHouse · Kubernetes · microservices · blockchain · Redis · LSTM · GNN · reinforcement learning · vector databases · enterprise authentication · paid commercial feeds · real-time global AIS · GPU custom transformer training

---

## Document History

| Date | Event |
|---|---|
| 20 Aug 2026 | Step 2 Architecture Freeze — all ADR-001–015 accepted |
