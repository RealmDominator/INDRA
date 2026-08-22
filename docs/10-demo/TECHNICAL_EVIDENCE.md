# INDRA — Technical Evidence Package

> **Status:** Step 10C final-submission support material. Claims below are
> limited to the current repository and recorded verification evidence.

## Executive Claim

INDRA is a Phase-1 India-focused disruption-response MVP that combines a
bounded event-extraction interface with deterministic risk, scenario,
network-impact, and procurement computation. PostgreSQL is the persistent
source of truth, and important results carry provenance and semantic labels.

## Implementation Evidence

### Architecture — IMPLEMENTED

- Single React/Vite frontend, FastAPI backend, and PostgreSQL database.
- NetworkX is limited to in-memory supply-graph traversal and impact analysis.
- No Kafka, Neo4j, MongoDB, Redis, microservices, or second persistent database.
- Frozen architecture: `docs/02-architecture/SYSTEM_ARCHITECTURE.md`.

### API and frontend — IMPLEMENTED

- Root-path API includes health, domain reference, events, corridor risk and
  impact, deterministic risk, scenarios, recommendations, bounded extraction,
  full event pipeline, and ingestion-status/run routes.
- Frontend uses backend API calls for corridor risk, events, reserves, routes,
  refineries, scenarios, recommendations, pipeline results, and evidence stages.
- Authoritative route contract: `docs/04-backend/API_SPEC.md`.

### Entity resolution — IMPLEMENTED

- Exact alias/canonical lookup followed by RapidFuzz fallback.
- The LLM/structured contract accepts human-readable names/codes, not DB IDs.
- Unresolved values are retained rather than invented.

### Risk, scenario, network, procurement — IMPLEMENTED

- Phase-1 risk: weighted deterministic formula with component contributions.
- Scenario: deterministic, parametric supply-gap calculations.
- NetworkX: route/refinery impact traversal only.
- Procurement: SciPy LP for complete candidate data; deterministic ranking
  fallback; explicit infeasible result; sanctions, availability, compatibility,
  route, and optional transit constraints.

### Provenance and data honesty — IMPLEMENTED

- Evidence chain stages: source, extraction, entity resolution, risk, scenario,
  optimization.
- Canonical semantics: `OBSERVED`, `DERIVED`, `HISTORICAL_CALIBRATED`,
  `ASSUMED`, `SIMULATED`.
- Scenario and procurement outputs are not presented as measured live data.

## Verification Evidence

| Verification | Recorded result | What it establishes |
|---|---:|---|
| `python -m pytest backend/tests -q` | 61 passed | Unit, integration, provider, ingestion, optimizer, security, pipeline, and reliability coverage |
| `python backend/tests/test_e2e_pipeline.py` | 54 passed, 0 failed | Event/entity/risk/scenario/procurement/evidence workflow, route filtering, CORS |
| `python scripts/db/check_db.py` | 90/90 passed | Tables, seeded rows, PK/FK/range/semantic/null checks |
| `npm run build` | passed, 34 modules | Production frontend build |
| `docker compose -f docker-compose.production.yml config --quiet` | valid | Compose configuration syntax |

## Primary Demonstration Evidence

The final walkthrough in `docs/10-demo/DEMO_SCRIPT.md` uses a controlled
structured event payload with India, Iraq, “Strait of Hurmuz”, Red Sea, and
unresolved Atlantis. It shows exact/fuzzy/unresolved resolution, deterministic
Hormuz risk/scenario/procurement behavior, NetworkX impact, and evidence
stages without EIA, ACLED, or live LLM credentials.

For the 30-day, 100% Hormuz scenario, the verified deterministic supply-gap
result is `7.056 MMT` (`DERIVED`) with disruption settings labeled `ASSUMED`.
The controlled demo input is `SIMULATED`; it is not a live event claim.

## Status Boundaries

### PARTIAL

- Step 8B external-source completion: adapters and fixture tests exist, but
  EIA/ACLED credentials are unavailable and not all live-source paths are
  fully verified.
- Runtime LLM: provider implementation exists, but the live benchmark remains
  pending `OPENROUTER_API_KEY`.

### DEFERRED

- Standalone prices and evidence endpoints.
- Live AIS, paid commercial feeds, enterprise authentication, and distributed
  infrastructure.

### FUTURE / NOT STARTED

- Step 8D-B XGBoost candidate: no training, model, metrics, or integration.
- Enterprise pilot/production capabilities.

## Claims Explicitly Excluded From Submission

- “All external sources are live.”
- “The LLM benchmark chose a final model.”
- “XGBoost is implemented.”
- “The dashboard provides live tanker tracking.”
- “INDRA is enterprise production-ready.”

## Source Basis

- Product and research framing: `README.md`,
  `docs/01-product/SOLUTION_OVERVIEW.md`, `research/research_report_1.md`,
  `research/research_report_2.md`.
- Architecture: `docs/02-architecture/SYSTEM_ARCHITECTURE.md`.
- LLM: `docs/07-ai-ml/AI_MODEL_STRATEGY.md`, `docs/07-ai-ml/AI_PIPELINE.md`.
- Procurement: `docs/08-engines/OPTIMIZATION.md`.
- Test evidence: `docs/09-testing/TESTING.md` and the commands above.
