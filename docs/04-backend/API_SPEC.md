# INDRA — API Specification

> **STATUS: FROZEN FOR PHASE 1 IMPLEMENTATION**
>
> Authoritative Phase-1 REST contract for the INDRA backend. Runtime route
> status below was audited against the current FastAPI application.
>
> **Revision:** Step 9C release-candidate audit (22 August 2026). See [ARCHITECTURE_DECISIONS.md](../02-architecture/ARCHITECTURE_DECISIONS.md) ADR-014.

---

## Runtime Implementation Status

Implemented against the verified PostgreSQL seed database: health, domain
reference data, event persistence/listing, corridor risk and graph impact,
deterministic risk/scenario/procurement calculations, bounded extraction and
pipeline processing, and ingestion status/run operations. There are no
implemented prices or standalone evidence routes in the current MVP; price
and evidence data are returned through relevant pipeline/results.

The current monolith is served at the root path; there is no `/api/v1` prefix.

| Runtime status | Paths |
|---|---|
| IMPLEMENTED | `GET /health`, `GET /countries`, `GET /corridors`, `GET /crude-grades`, `GET /suppliers`, `GET /routes`, `GET /refineries`, `GET /reserves` |
| IMPLEMENTED | `POST /events`, `GET /events`, `GET /corridors/risk`, `GET /corridors/risk/live`, `GET /corridors/{corridor_id}/impact` |
| IMPLEMENTED | `GET /risk`, `POST /risk`, `POST /scenarios`, `POST /recommendations` |
| IMPLEMENTED | `POST /events/extract`, `POST /events/process`, `POST /events/ingest-and-process` |
| IMPLEMENTED | `GET /ingestion/status`, `POST /ingestion/run` |
| DEFERRED / NOT IMPLEMENTED | Standalone prices, evidence, entity-detail, route-risk, supplier-risk, and recommendation-explanation routes |

## Base Configuration

| Setting | Value |
|---|---|
| Framework | FastAPI |
| Base URL | `http://localhost:8000` |
| Documentation | Auto-generated at `/docs` (Swagger) and `/redoc` |
| Format | JSON |
| Authentication | None for Phase 1 |
| CORS | Allow frontend origin (default `http://localhost:3000`) |

---

## Cross-Cutting Conventions

### Risk Scale in API Responses

Internal storage uses **0.0–1.0**. API responses use **0–100** display scale:

`display_score = internal_score × 100`

Applies to: `risk_score`, `severity`, `confidence`, component values, compatibility scores where displayed.

### Data Semantics in Responses

Responses include `data_semantic` where relevant: `OBSERVED` | `DERIVED` | `HISTORICAL_CALIBRATED` | `ASSUMED` | `SIMULATED`.

### Error Response Format

```json
{
  "error": true,
  "code": "SCENARIO_INVALID_PARAMS",
  "message": "Human-readable description",
  "detail": null
}
```

| HTTP Status | When |
|---|---|
| 400 | Malformed request body |
| 404 | Entity not found |
| 422 | Pydantic validation failure |
| 500 | Unhandled server error |
| 503 | Critical dependency unavailable (optional; prefer degraded response with stale-data flag for demo) |

### Provenance

Endpoints returning computed results SHOULD include enough identifiers for the evidence drawer (`entity_type`, `entity_id`) or embed a `evidence_url` path.

---

## MVP Endpoint Groups (audited runtime route set)

---

### 1. Health

| | |
|---|---|
| **Method** | GET |
| **Path** | `/health` |
| **Purpose** | Smoke test; report database connectivity and data-source freshness |

**Request:** None

**Response (200):**
```json
{
  "status": "ok",
  "database": "connected",
  "data_sources": [
    {"name": "GDELT", "status": "ACTIVE", "last_fetched_at": "2026-08-20T10:00:00Z"},
    {"name": "EIA", "status": "ACTIVE", "last_fetched_at": "2026-08-19T18:00:00Z"}
  ],
  "demo_mode": false
}
```

**Validation:** None

**Major errors:** 503 if database unreachable

---

### 2. Events — List

| | |
|---|---|
| **Method** | GET |
| **Path** | `/events` |
| **Purpose** | List recent geopolitical events for dashboard feed |

**Query parameters:**
| Parameter | Type | Validation |
|---|---|---|
| `event_type` | string | Optional enum: SANCTION, MILITARY, PORT_CLOSURE, ATTACK, DIPLOMATIC, OTHER |
| `corridor` | string | Optional corridor code (HORMUZ, RED_SEA, etc.) |
| `severity_min` | number | Optional 0–100 display scale |
| `since` | ISO8601 | Optional timestamp lower bound |
| `limit` | int | Default 20, max 100 |
| `offset` | int | Default 0 |

**Response (200):** Array of event summaries (see Event Detail shape, abbreviated).

**Major errors:** 422 invalid query params

**Provenance:** Each event includes `source_url`, `source_name`, `is_simulated`, `data_semantic` (`OBSERVED` for live ingested events).

---

### 3. Events — Detail

| | |
|---|---|
| **Method** | GET |
| **Path** | `/events/{id}` |
| **Purpose** | Single event with full detail for evidence drill-down |

**Path parameters:** `id` — integer event ID

**Response (200):**
```json
{
  "id": 42,
  "event_type": "SANCTION",
  "title": "US sanctions 3 Iranian tankers",
  "description": "...",
  "severity": 60,
  "confidence": 91,
  "affected_corridors": [{"code": "HORMUZ", "name": "Strait of Hormuz"}],
  "affected_countries": [{"iso3": "IRN", "name": "Iran"}],
  "affected_routes": [],
  "source_url": "https://...",
  "source_name": "OFAC",
  "occurred_at": "2026-08-17T14:30:00Z",
  "detected_at": "2026-08-17T14:45:00Z",
  "is_verified": true,
  "is_simulated": false,
  "llm_model_used": "provider/model-name",
  "data_semantic": "OBSERVED",
  "evidence_url": null
}
```

**Major errors:** 404 event not found

---

### 4. Risk — All Corridors

| | |
|---|---|
| **Method** | GET |
| **Path** | `/risk/corridors` |
| **Purpose** | Current risk scores for all monitored corridors (landing page cards) |

**Request:** None

**Response (200):**
```json
{
  "corridors": [
    {
      "corridor_code": "HORMUZ",
      "corridor_name": "Strait of Hormuz",
      "risk_score": 78,
      "risk_level": "CRITICAL",
      "trend_delta": 12,
      "calculated_at": "2026-08-19T12:00:00Z",
      "confidence": 72,
      "contributing_event_count": 3,
      "data_semantic": "DERIVED"
    }
  ]
}
```

**Provenance:** Scores derived from weighted_rule_v1; link to detail endpoint for components.

---

### 5. Risk — Corridor Detail

| | |
|---|---|
| **Method** | GET |
| **Path** | `/risk/corridors/{corridor_code}` |
| **Purpose** | Detailed risk breakdown with component contributions |

**Path parameters:** `corridor_code` — stable code (HORMUZ, RED_SEA, RUSSIA, SUEZ, MALACCA, CAPE)

**Response (200):**
```json
{
  "corridor_code": "HORMUZ",
  "corridor_name": "Strait of Hormuz",
  "risk_score": 78,
  "risk_level": "CRITICAL",
  "calculated_at": "2026-08-19T12:00:00Z",
  "calculation_method": "weighted_rule_v1",
  "components": [
    {"factor": "event_severity", "value": 82, "weight": 0.25, "contributing_events": [42, 43]},
    {"factor": "chokepoint_exposure", "value": 90, "weight": 0.20},
    {"factor": "india_dependency", "value": 42, "weight": 0.10}
  ],
  "confidence": 72,
  "data_freshness": {
    "geopolitical": "10 minutes ago",
    "prices": "today",
    "import_structure": "PPAC FY2024-25"
  },
  "data_semantic": "DERIVED",
  "evidence_url": null
}
```

**Major errors:** 404 unknown corridor code

---

### 6. Routes

| | |
|---|---|
| **Method** | GET |
| **Path** | `/routes` |
| **Purpose** | Supply routes with risk scores and corridor associations for map rendering |

**Query parameters:** `corridor` (optional filter), `operational_only` (bool, default true)

**Response (200):** Array of routes with origin/dest ports, corridor codes, `risk_score` (0–100), `is_operational`, coordinates for map polylines.

**Provenance:** Route risk is DERIVED; corridor associations from reference data (HISTORICAL_CALIBRATED / OBSERVED seed).

---

### 7. Refineries

| | |
|---|---|
| **Method** | GET |
| **Path** | `/refineries` |
| **Purpose** | Indian refineries with capacity, location, and crude compatibility summary |

**Response (200):** Array including `id`, `name`, `owner`, `capacity_mmtpa`, `port_id`, lat/lon, `compatible_grades` (from `refinery_supply_mix`), exposure hints.

**Provenance:** Capacity/location from PPAC seed (HISTORICAL_CALIBRATED); compatibility from `refinery_supply_mix` with `source_type`.

---

### 8. Reserves (SPR)

| | |
|---|---|
| **Method** | GET |
| **Path** | `/reserves` |
| **Purpose** | Strategic Petroleum Reserve status for all locations |

**Response (200):**
```json
{
  "locations": [
    {
      "location_name": "Padur",
      "capacity_mmt": 2.5,
      "current_level_mmt": 2.5,
      "days_coverage": 4.5,
      "data_semantic": "HISTORICAL_CALIBRATED"
    }
  ],
  "total_capacity_mmt": 5.33,
  "total_current_mmt": 5.33,
  "total_days_coverage": 9.5,
  "daily_consumption_mmt_used": 0.56
}
```

**Note:** `days_coverage = current_level_mmt / india_daily_consumption_mmt` computed at query time from config.

---

### 9. Prices

| | |
|---|---|
| **Method** | GET |
| **Path** | `/prices/current` |
| **Purpose** | Current crude prices, USD/INR FX, and derived INR prices |

**Response (200):**
```json
{
  "commodity_prices": [
    {
      "grade_name": "Brent",
      "price_usd_per_barrel": 82.50,
      "source": "EIA",
      "source_timestamp": "2026-08-19T00:00:00Z",
      "observed_at": "2026-08-19T06:00:00Z",
      "data_semantic": "OBSERVED"
    }
  ],
  "fx_rate": {
    "currency_pair": "USD_INR",
    "rate": 83.25,
    "source": "RBI",
    "source_timestamp": "2026-08-19T00:00:00Z",
    "data_semantic": "OBSERVED"
  },
  "derived_inr_prices": [
    {
      "grade_name": "Brent",
      "price_inr_per_barrel": 6868.13,
      "derivation_method": "nearest_valid_prior_fx",
      "commodity_source_timestamp": "2026-08-19T00:00:00Z",
      "fx_source_timestamp": "2026-08-19T00:00:00Z",
      "data_semantic": "DERIVED"
    }
  ]
}
```

**Provenance:** INR derivation uses nearest-valid-prior FX rule (ADR-011).

---

### 10. Scenarios — Presets

| | |
|---|---|
| **Method** | GET |
| **Path** | `/scenarios/presets` |
| **Purpose** | List available preset scenario definitions |

**Response (200):**
```json
{
  "presets": [
    {
      "scenario_type": "HORMUZ_PARTIAL",
      "name": "Hormuz 50% disruption / 30 days",
      "default_parameters": {"capacity_reduction_pct": 50, "duration_days": 30}
    },
    {
      "scenario_type": "HORMUZ_FULL",
      "name": "Hormuz 100% closure / 30 days",
      "default_parameters": {"capacity_reduction_pct": 100, "duration_days": 30}
    },
    {
      "scenario_type": "RUSSIA_LOSS",
      "name": "Russia supply reduction",
      "default_parameters": {"volume_loss_pct": 100, "duration_days": 30}
    },
    {
      "scenario_type": "RED_SEA",
      "name": "Red Sea full suspension",
      "default_parameters": {"capacity_reduction_pct": 100, "duration_days": 30}
    }
  ]
}
```

Parameters loaded from `config/scenario_assumptions.yaml`.

---

### 11. Scenarios — Run

| | |
|---|---|
| **Method** | POST |
| **Path** | `/scenarios/run` |
| **Purpose** | Execute deterministic scenario simulation |

**Request body:**
```json
{
  "scenario_type": "HORMUZ_PARTIAL",
  "capacity_reduction_pct": 50,
  "duration_days": 30,
  "refinery_id": null
}
```

**Validation:**
| Field | Rules |
|---|---|
| `scenario_type` | Required; enum of preset types |
| `capacity_reduction_pct` | 0–100 |
| `duration_days` | 1–365 |
| `refinery_id` | Optional int |

**Response (200):**
```json
{
  "scenario_id": 7,
  "supply_gap_mmt": 7.06,
  "days_until_critical": 22.7,
  "affected_refineries": [{"id": 12, "name": "BPCL Kochi", "shortfall_mmt": 1.2}],
  "price_impact_per_barrel_usd": 5.0,
  "additional_import_cost_usd_bn": 1.9,
  "freight_cost_increase_pct": 40,
  "alternative_routes": ["CAPE"],
  "spr_bridge": {
    "required_mmt": 3.2,
    "available_mmt": 5.33,
    "days_bridged": 5.7,
    "uncovered_gap_mmt": 0
  },
  "assumptions": [
    {"name": "hormuz_share", "value": 0.42, "data_semantic": "HISTORICAL_CALIBRATED", "source": "PPAC FY2024-25"}
  ],
  "data_semantic": "DERIVED",
  "evidence_url": null
}
```

**Major errors:**
- 422 invalid parameters
- 404 unknown scenario_type

**Note:** GDP impact removed from scope. LLM does not compute scenario math.

---

### 12. Recommendations / Procurement

| | |
|---|---|
| **Method** | GET |
| **Path** | `/recommendations/{scenario_id}` |
| **Purpose** | Ranked procurement alternatives for a completed scenario |

**Query parameters:**
| Parameter | Type | Notes |
|---|---|---|
| `refinery_id` | int | Optional; default = most exposed refinery |
| `risk_aversion` | float | Optional λ, default 0.5 |

**Response (200):** Ranked alternatives with compatibility, route, cost, risk (0–100), compliance, scoring_breakdown, `data_semantic: DERIVED`.

**Major errors:** 404 scenario not found; 422 scenario not yet computed

**Provenance:** Links to OPTIMIZATION evidence record.

---

### 13. Evidence

| | |
|---|---|
| **Method** | GET |
| **Path** | `/evidence/{entity_type}/{entity_id}` |
| **Purpose** | Full provenance chain for a result |

**Path parameters:**
| Parameter | Values |
|---|---|
| `entity_type` | `event`, `risk_score`, `scenario_result`, `procurement_option` |
| `entity_id` | Integer ID |

**Response (200):**
```json
{
  "entity_type": "risk_score",
  "entity_id": 123,
  "chain": [
    {
      "evidence_type": "SOURCE",
      "source_url": "https://...",
      "timestamp": "2026-08-19T10:00:00Z",
      "data_semantic": "OBSERVED"
    },
    {
      "evidence_type": "LLM_EXTRACTION",
      "model_or_method": "provider/model",
      "output_summary": {"event_type": "MILITARY", "severity": 0.68},
      "data_semantic": "DERIVED"
    },
    {
      "evidence_type": "RISK_CALCULATION",
      "model_or_method": "weighted_rule_v1",
      "output_summary": {"score": 0.78},
      "data_semantic": "DERIVED"
    }
  ]
}
```

**Major errors:** 404 entity or evidence not found

---

## Deferred Endpoints (Post-MVP)

| Endpoint | Reason |
|---|---|
| `GET /suppliers/{id}` | Detail deferred; list endpoint is implemented and sufficient |
| `GET /routes/{id}`, `GET /refineries/{id}` | Detail deferred; list endpoints sufficient |
| `GET /refineries/{id}/exposure` | Derivable from scenario results |
| `GET /risk/routes`, `GET /risk/suppliers` | Visible on map/recommendations |
| `GET /prices/history`, `GET /prices/fx` | Included in `/prices/current` |
| `GET /reserves/{location_id}`, `GET /reserves/scenario/{id}` | Aggregated in `/reserves` and scenario response |
| `GET /recommendations/{id}/explain` | LLM explanation is NICE TO HAVE |
| Standalone price/evidence endpoints | Current pipeline returns relevant derived/provenance data; standalone routes are deferred |
| `POST /events/extract` | Implemented as bounded provider extraction; live use requires configured credentials |
| `GET /events/feed` | `/events` sufficient |
| `GET /status/data-sources` | Covered by `/health` |

---

## Implementation Notes (Phase 1)

### Current implementation

The current application exposes the audited route set above. Event pipeline
results include entity resolution, deterministic risk, NetworkX impact,
scenario, procurement, and evidence-stage output. External source access and
live LLM extraction remain configuration-dependent; the weighted deterministic
engine remains the production baseline.

- All routes implemented in a single FastAPI app at the root path
- Pydantic models enforce request/response shapes
- Internal 0.0–1.0 → display 0–100 conversion in response serializers
- CORS middleware required for React frontend
- No authentication middleware in Phase 1
