# INDRA — Final Presentation Story

> **Status:** Step 10C presentation support material. This is a judge-facing
> story structure based only on the implemented MVP and verified evidence.

## Status Legend

- **IMPLEMENTED** — present in the repository and verified.
- **PARTIAL** — implemented in software but limited by unavailable external access.
- **DEFERRED** — intentionally outside the MVP runtime/API boundary.
- **FUTURE** — not implemented in Phase 1.

## Slide 1 — INDRA turns disruption signals into India-specific decisions

**On slide**

India Disruption Response Architecture

From a disruption signal to a traceable supply-gap and procurement decision.

**Status:** IMPLEMENTED MVP / release candidate; not enterprise production.

## Slide 2 — India’s crude supply chain has concentrated disruption risk

**On slide**

- India’s crude imports and key seaborne corridors create exposure to disruption.
- The Strait of Hormuz is a strategic dependency in the project’s seeded scenario model.
- A disruption can propagate from a corridor to routes, refineries, reserves, and procurement choices.

**Evidence basis:** project research reports and PPAC/ISPRL-oriented seed documentation.

## Slide 3 — Manual workflows break at the propagation step

**On slide**

Teams can read news, maintain spreadsheets, and source market data, but the
decision chain is fragmented: event → affected corridor → refinery exposure →
supply gap → alternative procurement → evidence.

INDRA’s value is joining that chain for the India-specific use case.

## Slide 4 — The product is one traceable decision loop

**On slide**

`Event → structured event → entity resolution → risk → network impact → scenario → procurement → evidence → dashboard`

Each output retains its data semantic: `OBSERVED`, `DERIVED`,
`HISTORICAL_CALIBRATED`, `ASSUMED`, or `SIMULATED`.

**Status:** IMPLEMENTED for the seeded/manual demonstration path.

## Slide 5 — A deliberately small architecture keeps the MVP explainable

**On slide**

React/Vite dashboard → single FastAPI backend → single PostgreSQL database.

NetworkX supports in-memory graph operations. PostgreSQL remains the persistent
source of truth. No Kafka, Neo4j, MongoDB, Redis, or microservices are used.

**Status:** IMPLEMENTED.

## Slide 6 — The data pipeline preserves availability and provenance states

**On slide**

- Ingestion adapters normalize and persist source-aware records.
- Entity resolution maps names/codes only after schema validation.
- Evidence links source, extraction, resolution, risk, scenario, optimization,
  and recommendation stages.

**Status:** ingestion framework IMPLEMENTED; live-source completion PARTIAL.

## Slide 7 — The LLM is bounded to language tasks

**On slide**

The LLM provider abstraction supports structured event extraction, validation,
metadata, timeout/retry handling, and provider swapping.

It does **not** calculate risk, scenarios, or procurement allocations, and it
never supplies database IDs.

**Status:** IMPLEMENTED abstraction; runtime model is provisional
`openai/gpt-4o-mini` via OpenRouter; live benchmark is PARTIAL/pending API key.

## Slide 8 — Entity resolution is explicit and fails honestly

**On slide**

Resolution sequence:

`exact alias → exact canonical name/code → RapidFuzz fallback → unresolved log`

The verified demo resolves India and Iraq, fuzzy-matches “Strait of Hurmuz”,
and leaves “Atlantis” unresolved.

**Status:** IMPLEMENTED.

## Slide 9 — Phase 1 risk is a weighted deterministic model

**On slide**

Inputs: event severity, recency, chokepoint exposure, conflict/sanctions,
historical rate, and India dependency.

Output: internal `0.0–1.0`, display `0–100`, component contributions, and
calculation provenance.

**Status:** IMPLEMENTED. XGBoost is FUTURE / NOT STARTED.

## Slide 10 — NetworkX answers graph questions, not database questions

**On slide**

NetworkX traverses supplier → route → port → refinery relationships to identify
reachability and disruption impact.

It is not the database, risk engine, scenario engine, or optimizer.

**Status:** IMPLEMENTED.

## Slide 11 — Scenarios are parametric, reproducible calculations

**On slide**

For the primary Hormuz demonstration:

- Assumptions: 30 days, 100% reduction.
- Output: `7.056 MMT` modeled supply gap.
- Semantic contract: assumptions are `ASSUMED`; output is `DERIVED`.

This is not a forecast or a claim about a future event.

**Status:** IMPLEMENTED.

## Slide 12 — Procurement uses optimization, with a deterministic fallback

**On slide**

Primary method: SciPy `linprog(method="highs")` for fully identified supplier,
crude-grade, route, capacity, cost, compatibility, and route-status inputs.

Constraints include availability, target volume, sanctions, route disruption,
compatibility, and optional transit limits. Incomplete inputs or solver issues
fall back to deterministic ranking; infeasibility remains explicit.

**Status:** IMPLEMENTED.

## Slide 13 — Evidence is a first-class result, not a footnote

**On slide**

`Source → extraction → entity resolution → risk → scenario → optimization`

Evidence records, evidence links, and stage-specific semantics let a user see
what was observed, assumed, derived, unavailable, or simulated.

**Status:** IMPLEMENTED in pipeline results; standalone evidence API is DEFERRED.

## Slide 14 — The dashboard follows the decision workflow

**On slide**

The React dashboard shows:

- event input and pipeline result;
- corridor risk and recent events;
- India supply-network reference panel;
- scenario controls and modeled supply gap;
- procurement feasibility; and
- evidence trail, semantic badges, loading/error/empty states.

**Status:** IMPLEMENTED. It is a reference panel, not a live AIS map.

## Slide 15 — The MVP is validated across the full path

**On slide**

- 61 backend tests passed.
- 54/54 scripted E2E checks passed.
- 90/90 database integrity checks passed.
- Frontend production build passed (34 modules).
- Docker Compose production configuration validated.

The E2E flow covers database health, entities, resolution, deterministic risk,
scenario, procurement, evidence, route filtering, and CORS.

## Slide 16 — Limits are explicit

**On slide**

- External ingestion is PARTIAL: EIA and ACLED credentials are unavailable;
  OFAC/RBI/RSS completion is not fully live-verified.
- Live OpenRouter benchmark is pending API-key availability.
- No XGBoost model is trained or integrated.
- No live AIS, commercial feeds, enterprise authentication, or enterprise
  production-readiness claim.

Honesty about unavailable inputs is a product requirement, not a disclaimer.

## Slide 17 — The roadmap builds from evidence, not hype

**On slide**

1. Complete external-source access and operational freshness checks.
2. Run an INDRA-specific live LLM benchmark before final model selection.
3. Acquire defensible time-indexed disruption labels before starting XGBoost.
4. Evaluate pilot requirements only after data and operational evidence exist.

**Closing statement**

INDRA is a transparent Phase-1 decision-support MVP: bounded AI for language,
deterministic computation for decisions, and evidence for every important step.

## Sources for Presenter Notes

- `research/research_report_1.md` — problem decomposition, manual workflow,
  Phase-1 architecture, data honesty, deterministic/LLM split.
- `research/research_report_2.md` — final product definition, MVP workflow,
  scenario/procurement rationale, exclusions, roadmap.
- `docs/02-architecture/SYSTEM_ARCHITECTURE.md` — frozen architecture,
  NetworkX boundary, evidence and semantic model.
- `docs/07-ai-ml/AI_MODEL_STRATEGY.md` and `AI_PIPELINE.md` — provider and
  LLM limitations.
- `docs/08-engines/OPTIMIZATION.md` — LP/fallback contract.
- `docs/09-testing/TESTING.md` — verified results and limitations.
