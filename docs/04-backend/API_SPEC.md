# INDRA — API Specification

> **STATUS: FROZEN FOR PHASE 1 IMPLEMENTATION**
>
> This is the audited contract for the current FastAPI monolith. It describes
> implemented root-path routes only; it does not promise deferred endpoints.
> Revision: Step 10D final submission audit (22 August 2026).

## Service Contract

| Setting | Value |
|---|---|
| Base URL | `http://localhost:8000` |
| API documentation | `/docs` and `/redoc` |
| Authentication | None in Phase 1 |
| CORS | Explicit `CORS_ORIGINS` or `FRONTEND_URL` configuration |
| Persistent source of truth | PostgreSQL |
| Numerical engines | Deterministic risk, scenario, and procurement code; never the LLM |

All relevant outputs use these semantic labels: `OBSERVED`, `DERIVED`,
`HISTORICAL_CALIBRATED`, `ASSUMED`, and `SIMULATED`. Internal risk values are
`0.0–1.0`; `display_score = score × 100`.

Validation errors are returned by FastAPI as `422` responses. Unknown domain
resources return `404` where implemented. The production exception handler
returns `500 {"detail":"Internal server error"}` without a traceback.

## Implemented Endpoints

### Health and reference data

| Method | Path | Purpose | Validation / major errors |
|---|---|---|---|
| GET | `/health` | Application, environment, uptime, and PostgreSQL connectivity. | Returns HTTP 200 with `database: connected` or `unavailable`; no secret values. |
| GET | `/countries` | Paginated country reference data. | `limit` 1–100, `offset` ≥0. |
| GET | `/corridors` | Paginated first-class corridor reference data. | `limit` 1–100, `offset` ≥0. |
| GET | `/crude-grades` | Paginated crude-grade reference data. | `limit` 1–100, `offset` ≥0. |
| GET | `/suppliers` | Paginated supplier reference data. | `limit` 1–100, `offset` ≥0. |
| GET | `/routes` | Routes, optionally filtered by corridor and operational state. | Unknown `corridor` → 404; `operational_only` defaults to true. |
| GET | `/refineries` | Refineries and compatible-grade IDs. | `limit` 1–100, `offset` ≥0. |
| GET | `/reserves` | Aggregate and site-level SPR reference data. | Unavailable current reserve levels remain `null`; they are never fabricated. |

### Events, extraction, and entity resolution

| Method | Path | Purpose | Request / result | Major errors |
|---|---|---|---|---|
| GET | `/events` | Persisted event feed. | `limit` defaults to 50; response contains `items`, source fields, and an event semantic label. | Database failure → safe 500. |
| POST | `/events` | Validate a structured event and resolve human-readable country, corridor, and route names. | `StructuredEvent`: title, enum event type, severity 1–10, confidence 0–1, and name/code lists only. Returns `resolved`, `unresolved`, and staged evidence. | IDs in entity-name fields and invalid fields → 422. |
| POST | `/events/extract` | Bounded provider extraction plus validation and entity resolution. | `{ "text": "…" }`, minimum 20 characters. Returns structured event, provider metadata, resolution, and evidence. | No provider / unavailable provider → 503; invalid structured output → 422. |
| POST | `/events/process` | Process a persisted event through the deterministic pipeline. | `{ "event_id": integer }`; returns pipeline stages, resolution, risk, network impact, scenario, procurement, and evidence where available. | Pipeline failure → safe 500. |
| POST | `/events/ingest-and-process` | Persist raw event text and process it through the pipeline. | `{ "text": "…", "source_name": "manual" }`, text minimum 20 characters. | Pipeline failure → safe 500. |

The LLM never supplies database IDs and never computes risk, scenario, or
procurement values. Without an LLM credential, extraction is explicitly
unavailable/skipped; no extraction result is fabricated.

### Risk, graph impact, scenario, and procurement

| Method | Path | Purpose | Request / result | Major errors |
|---|---|---|---|---|
| GET | `/corridors/risk` | Seeded corridor baseline risk for dashboard cards. | Returns `items` with `display_score`, risk level, and `OBSERVED` semantic. | Database failure → safe 500. |
| GET | `/corridors/risk/live` | Recalculate corridor risk from persisted events. | Returns weighted-rule component contributions and `DERIVED` semantic. | Database failure → safe 500. |
| GET | `/corridors/{corridor_id}/impact` | NetworkX route/refinery impact traversal for one corridor. | Returns affected routes/refineries with `DERIVED` semantic. | Unknown corridor → 404. |
| GET | `/risk` | Risk-engine readiness summary. | Returns `data_semantic: DERIVED`. | — |
| POST | `/risk` | Calculate a reproducible weighted deterministic risk score. | `{ "features": {six 0–1 feature values}, "weights": optional }`; response includes score, display score, level, components, and `weighted_rule_v1`. | Invalid fields → 422. |
| POST | `/scenarios` | Run parametric deterministic supply-gap arithmetic. | `scenario_type`, `duration_days` 0–365, optional `reduction_pct`; response includes modeled gap and `DERIVED` semantic. | Invalid duration → 422. |
| POST | `/recommendations` | Optimize caller-supplied procurement candidates. | Candidate constraints include availability, sanctions, route status/disruption, compatibility, optional transit bound, cost, and risk. Response includes selection, allocation, feasibility, solver/fallback status, constraints, provenance, and `DERIVED` semantic. | Invalid target/constraint ranges → 422. |

`/recommendations` uses SciPy `linprog` when every required candidate identity
and numerical constraint is supplied; otherwise it returns the deterministic
ranking fallback with an explicit `fallback_reason`. Infeasibility is explicit.
No route capacity, compatibility, transit time, or quote is invented.

### Ingestion status and manual run

| Method | Path | Purpose | Result | Major errors |
|---|---|---|---|---|
| GET | `/ingestion/status` | Source configuration, freshness, last run state, and errors. | `sources` with explicit unavailable/stale/deferred states. | Database failure → safe 500. |
| POST | `/ingestion/run` | Trigger the configured adapters once. | Per-source accepted/rejected/duplicate counts, freshness, and error strings. | Runner failure → safe 500. |

External access is configuration-dependent. Step 8B remains **PARTIAL**:
EIA/ACLED credentials are not supplied for the reproducible demo. The API does
not label unavailable sources as live.

## Deferred / Not Implemented Routes

The following are intentionally not part of the current MVP: standalone price
and evidence retrieval, event-detail routes, scenario preset/run routes,
entity-detail routes, route/supplier risk routes, recommendation explanation,
and any `/api/v1` path namespace. Price and evidence information is exposed in
the applicable pipeline or computation response instead.

## Provenance Contract

Pipeline output carries a staged evidence chain in this order when its stages
are available: source → extraction → entity resolution → risk → scenario →
optimization. Inputs preserve their own semantic labels; calculations are
`DERIVED`; controlled demo input is `SIMULATED`; scenario parameters are
`ASSUMED` or `HISTORICAL_CALIBRATED` as documented.

See [SYSTEM_ARCHITECTURE.md](../02-architecture/SYSTEM_ARCHITECTURE.md),
[AI_PIPELINE.md](../07-ai-ml/AI_PIPELINE.md), and
[OPTIMIZATION.md](../08-engines/OPTIMIZATION.md).
