# INDRA — API Specification

> **STATUS: PLANNED — TO BE FROZEN IN STEP 2.**
>
> This document defines the planned MVP API surface for the INDRA backend. All endpoints are design targets, not implemented routes. Exact request/response schemas will be finalized during Step 2.
>
> **Revision:** Post-review corrections. Reduced from ~30 to ~12 MVP endpoint groups. Risk scores use 0–100 display scale in API responses.
>
> Source: PETRAS Analysis §16; INDRA Master Report §11

---

## Base Configuration

| Setting | Value |
|---|---|
| Framework | FastAPI |
| Base URL | `http://localhost:8000/api/v1` |
| Documentation | Auto-generated at `/docs` (Swagger) and `/redoc` |
| Format | JSON |
| Authentication | None for Phase 1 |

---

## Risk Scale in API Responses

> **Convention:** API responses display risk/severity/confidence scores on the **0–100 scale** for human readability. Internal database storage uses 0.0–1.0. The API layer performs the conversion: `display_score = internal_score × 100`.

---

## MVP Endpoint Groups (~12)

### 1. Events

| Method | Endpoint | Description | Status |
|---|---|---|---|
| GET | `/events` | List recent geopolitical events with filters | PLANNED |
| GET | `/events/{id}` | Single event with full detail and source | PLANNED |

**Planned query parameters for GET `/events`:**
- `event_type` — filter by type (SANCTION, MILITARY, PORT_CLOSURE, ATTACK, DIPLOMATIC, OTHER)
- `corridor` — filter by affected corridor code (HORMUZ, RED_SEA, SUEZ, RUSSIA)
- `severity_min` — minimum severity threshold (0–100 display scale)
- `since` — timestamp filter
- `limit` / `offset` — pagination

**Planned response shape (conceptual):**
```json
{
  "id": 42,
  "event_type": "SANCTION",
  "title": "US sanctions 3 Iranian tankers",
  "severity": 60,
  "confidence": 91,
  "affected_corridors": [{"code": "HORMUZ", "name": "Strait of Hormuz"}],
  "affected_countries": [{"iso3": "IRN", "name": "Iran"}],
  "source_url": "https://...",
  "source_name": "OFAC",
  "occurred_at": "2026-08-17T14:30:00Z",
  "detected_at": "2026-08-17T14:45:00Z",
  "is_verified": true,
  "is_simulated": false,
  "data_semantic": "OBSERVED"
}
```

> **Note:** `severity` and `confidence` are displayed on 0–100 scale. Internally stored as 0.0–1.0.

---

### 2. Risk — Corridors

| Method | Endpoint | Description | Status |
|---|---|---|---|
| GET | `/risk/corridors` | Current risk scores for all monitored corridors | PLANNED |
| GET | `/risk/corridors/{corridor_code}` | Detailed risk breakdown for a corridor | PLANNED |

**Planned response shape (conceptual):**
```json
{
  "corridor_code": "HORMUZ",
  "corridor_name": "Strait of Hormuz",
  "risk_score": 78,
  "risk_level": "CRITICAL",
  "calculated_at": "2026-08-19T12:00:00Z",
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
  "data_semantic": "DERIVED"
}
```

> **Note:** All scores in the response (risk_score, component values, confidence) are 0–100 display scale.

---

### 3. Supply Chain — Routes

| Method | Endpoint | Description | Status |
|---|---|---|---|
| GET | `/routes` | All supply routes with risk scores and corridor associations | PLANNED |

---

### 4. Supply Chain — Refineries

| Method | Endpoint | Description | Status |
|---|---|---|---|
| GET | `/refineries` | All Indian refineries with capacity, location, and crude compatibility | PLANNED |

---

### 5. Reserves (SPR)

| Method | Endpoint | Description | Status |
|---|---|---|---|
| GET | `/reserves` | Current SPR status for all locations | PLANNED |

> **Note:** `days_coverage` is calculated at query time: `current_level_mmt / india_daily_consumption_mmt`. Not stored.

---

### 6. Prices

| Method | Endpoint | Description | Status |
|---|---|---|---|
| GET | `/prices/current` | Current crude oil prices + USD/INR rate | PLANNED |

**Response includes:**
- Latest commodity prices per grade (from `commodity_prices`)
- Latest USD/INR FX rate (from `fx_rates`)
- Derived INR prices (computed using nearest-valid-prior FX rate)
- Source timestamps for both price and FX observations

---

### 7. Scenarios

| Method | Endpoint | Description | Status |
|---|---|---|---|
| GET | `/scenarios/presets` | List available preset scenarios | PLANNED |
| POST | `/scenarios/run` | Run a scenario simulation | PLANNED |

**Planned preset scenarios:**
1. Hormuz 50% disruption / 30 days
2. Hormuz 100% closure / 30 days
3. Russia supply reduction (100% loss)
4. Red Sea full suspension

**Planned scenario request shape:**
```json
{
  "scenario_type": "HORMUZ_PARTIAL",
  "capacity_reduction_pct": 50,
  "duration_days": 30
}
```

**Planned scenario response shape:**
```json
{
  "scenario_id": 7,
  "supply_gap_mmt": 7.06,
  "days_until_critical": 22.7,
  "affected_refineries": ["BPCL Kochi", "IOC Paradip"],
  "price_impact_per_barrel_usd": 5.0,
  "additional_import_cost_usd_bn": 1.9,
  "freight_cost_increase_pct": 40,
  "alternative_routes": ["Cape of Good Hope"],
  "spr_bridge": {
    "required_mmt": 3.2,
    "available_mmt": 5.33,
    "days_bridged": 5.7,
    "uncovered_gap_mmt": 0
  },
  "assumptions": [
    {"name": "hormuz_share", "value": 0.42, "data_semantic": "HISTORICAL_CALIBRATED", "source": "PPAC FY2024-25"},
    {"name": "price_impact", "value": 5.0, "data_semantic": "HISTORICAL_CALIBRATED", "source": "EIA historical"},
    {"name": "freight_multiplier", "value": 1.4, "data_semantic": "ASSUMED", "source": "Distance ratio estimate"}
  ],
  "data_semantic": "DERIVED"
}
```

> **REMOVED from MVP:** `gdp_impact_estimate_usd_bn` — requires macroeconomic modeling beyond scope.

---

### 8. Recommendations / Procurement

| Method | Endpoint | Description | Status |
|---|---|---|---|
| GET | `/recommendations/{scenario_id}` | Procurement recommendations for a scenario | PLANNED |

**Planned response shape:**
```json
{
  "scenario_id": 7,
  "refinery": "BPCL Kochi",
  "supply_gap_mmt": 1.2,
  "alternatives": [
    {
      "rank": 1,
      "supplier": "Saudi Arabia",
      "crude_grade": "Arab Light",
      "compatibility": "HIGH",
      "route": "Cape of Good Hope",
      "transit_days": 21,
      "price_cif_usd_per_barrel": 86.00,
      "cost_premium_vs_normal": "+$3.50/bbl",
      "route_risk": 15,
      "compliance": "CLEAR",
      "overall_score": 87,
      "scoring_breakdown": {
        "compatibility": 90,
        "cost": 70,
        "risk": 85,
        "transit": 65,
        "compliance": 100
      },
      "data_semantic": "DERIVED"
    }
  ]
}
```

> **Note:** All scores in 0–100 display scale.

---

### 9. Evidence

| Method | Endpoint | Description | Status |
|---|---|---|---|
| GET | `/evidence/{entity_type}/{entity_id}` | Full evidence/provenance chain for a result | PLANNED |

**Supported `entity_type` values:** event, risk_score, scenario_result, procurement_option

Returns the provenance chain from the `evidence_records` and `evidence_links` tables, showing the path from source to result.

---

### 10. Health / Status

| Method | Endpoint | Description | Status |
|---|---|---|---|
| GET | `/health` | System health check | PLANNED |

---

## Deferred Endpoints (Post-MVP)

The following endpoints were in the original specification but are deferred to reduce MVP scope:

| Endpoint | Reason for Deferral |
|---|---|
| `GET /suppliers` | Not needed for core demo flow |
| `GET /suppliers/{id}` | Not needed for core demo flow |
| `GET /routes/{id}` | Individual route detail not critical |
| `GET /refineries/{id}` | Individual refinery detail not critical |
| `GET /refineries/{id}/exposure` | Can be derived from scenario results |
| `GET /risk/routes` | Route risk visible on map |
| `GET /risk/suppliers` | Supplier risk visible in recommendations |
| `GET /prices/history` | Historical chart is SHOULD HAVE |
| `GET /prices/fx` | FX included in `/prices/current` |
| `GET /reserves/{location_id}` | Individual SPR detail not critical |
| `GET /reserves/scenario/{id}` | SPR impact included in scenario results |
| `GET /recommendations/{id}/refinery/{id}` | Refinery-level detail can come later |
| `GET /recommendations/{id}/explain` | LLM explanation is NICE TO HAVE |
| `POST /events/extract` | Manual extraction trigger not in core demo |
| `GET /events/feed` | Event list is sufficient |
| `GET /status/data-sources` | Useful but not demo-critical |

---

## Error Response Format (Planned)

```json
{
  "error": true,
  "code": "SCENARIO_INVALID_PARAMS",
  "message": "Duration must be between 1 and 365 days",
  "detail": null
}
```

## CORS

Frontend origin (default `http://localhost:3000`) must be allowed in CORS configuration.
