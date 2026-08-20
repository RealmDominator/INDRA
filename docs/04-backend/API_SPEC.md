# INDRA — API Specification

> **STATUS: PLANNED — Not yet implemented.**
>
> This document defines the planned API surface for the INDRA backend. All endpoints listed here are design targets, not implemented routes. Actual implementation may differ in request/response details.
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

## Planned API Surface

### Events

| Method | Endpoint | Description | Status |
|---|---|---|---|
| GET | `/events` | List recent geopolitical events with filters | PLANNED |
| GET | `/events/{id}` | Get single event with full detail and source | PLANNED |
| GET | `/events/feed` | Real-time event feed (latest N events) | PLANNED |
| POST | `/events/extract` | Trigger LLM extraction on a news article URL | PLANNED |

**Planned query parameters for GET `/events`:**
- `event_type` — filter by type (SANCTION, MILITARY, PORT_CLOSURE, ATTACK, DIPLOMATIC, OTHER)
- `corridor` — filter by affected corridor (HORMUZ, RED_SEA, SUEZ, MALACCA)
- `severity_min` — minimum severity threshold
- `since` — timestamp filter
- `limit` — pagination limit
- `offset` — pagination offset

**Planned response shape (conceptual):**
```json
{
  "id": 42,
  "event_type": "SANCTION",
  "title": "US sanctions 3 Iranian tankers",
  "severity": 0.6,
  "confidence": 0.91,
  "affected_corridors": ["HORMUZ"],
  "affected_entities": ["OFAC", "Iranian tanker fleet"],
  "source_url": "https://...",
  "source_name": "OFAC",
  "occurred_at": "2026-08-17T14:30:00Z",
  "detected_at": "2026-08-17T14:45:00Z",
  "is_verified": true,
  "data_classification": "LIVE"
}
```

---

### Risk

| Method | Endpoint | Description | Status |
|---|---|---|---|
| GET | `/risk/corridors` | Current risk scores for all monitored corridors | PLANNED |
| GET | `/risk/corridors/{corridor_id}` | Detailed risk breakdown for a corridor | PLANNED |
| GET | `/risk/routes` | Risk scores for all routes | PLANNED |
| GET | `/risk/routes/{route_id}` | Detailed risk for a specific route | PLANNED |
| GET | `/risk/suppliers` | Risk scores for all suppliers | PLANNED |
| GET | `/risk/evidence/{entity_type}/{entity_id}` | Full evidence chain for a risk score | PLANNED |

**Planned evidence response shape:**
```json
{
  "entity_type": "corridor",
  "entity_id": "HORMUZ",
  "risk_score": 78,
  "risk_level": "CRITICAL",
  "calculated_at": "2026-08-19T12:00:00Z",
  "components": [
    {"factor": "event_severity", "value": 82, "weight": 0.25, "contributing_events": [42, 43]},
    {"factor": "chokepoint_exposure", "value": 90, "weight": 0.20},
    {"factor": "india_dependency", "value": 42, "weight": 0.10}
  ],
  "confidence": 0.72,
  "data_freshness": {
    "geopolitical": "10 minutes ago",
    "prices": "today",
    "import_structure": "PPAC FY2024-25"
  }
}
```

---

### Scenarios

| Method | Endpoint | Description | Status |
|---|---|---|---|
| GET | `/scenarios/presets` | List available preset scenarios | PLANNED |
| POST | `/scenarios/run` | Run a scenario simulation | PLANNED |
| GET | `/scenarios/{id}` | Get saved scenario results | PLANNED |
| GET | `/scenarios/{id}/impact` | Detailed impact breakdown | PLANNED |

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
  "affected_refineries": ["Kochi BPCL", "Paradip IOC"],
  "price_impact_per_barrel_usd": 5.0,
  "additional_import_cost_usd_bn": 1.9,
  "freight_cost_increase_pct": 40,
  "alternative_routes": ["CAPE_OF_GOOD_HOPE"],
  "spr_bridge": {
    "required_mmt": 3.2,
    "available_mmt": 5.33,
    "days_bridged": 5.7
  },
  "data_classification": "DERIVED",
  "assumptions_visible": true
}
```

---

### Recommendations / Procurement

| Method | Endpoint | Description | Status |
|---|---|---|---|
| GET | `/recommendations/{scenario_id}` | Get procurement recommendations for a scenario | PLANNED |
| GET | `/recommendations/{scenario_id}/refinery/{refinery_id}` | Refinery-specific recommendations | PLANNED |
| GET | `/recommendations/{scenario_id}/explain` | LLM-generated action brief | PLANNED |

**Planned recommendation response shape:**
```json
{
  "refinery_id": 14,
  "refinery_name": "BPCL Kochi",
  "supply_gap_mmt": 1.2,
  "alternatives": [
    {
      "rank": 1,
      "supplier": "Saudi Arabia",
      "crude_grade": "Arab Light",
      "compatibility": "HIGH",
      "route": "Cape of Good Hope",
      "transit_days": 21,
      "cost_premium_usd_per_barrel": 3.5,
      "route_risk": "LOW",
      "compliance": "CLEAR",
      "overall_score": 0.87
    }
  ]
}
```

---

### Reserves (SPR)

| Method | Endpoint | Description | Status |
|---|---|---|---|
| GET | `/reserves` | Current SPR status for all locations | PLANNED |
| GET | `/reserves/{location_id}` | Detail for a specific SPR location | PLANNED |
| GET | `/reserves/scenario/{scenario_id}` | SPR drawdown analysis for a scenario | PLANNED |

---

### Prices

| Method | Endpoint | Description | Status |
|---|---|---|---|
| GET | `/prices/current` | Current crude oil prices (EIA) | PLANNED |
| GET | `/prices/history` | Historical price data | PLANNED |
| GET | `/prices/fx` | Current USD/INR exchange rate (RBI) | PLANNED |

---

### Routes

| Method | Endpoint | Description | Status |
|---|---|---|---|
| GET | `/routes` | All supply routes with risk scores | PLANNED |
| GET | `/routes/{id}` | Route detail with chokepoint information | PLANNED |

---

### Suppliers

| Method | Endpoint | Description | Status |
|---|---|---|---|
| GET | `/suppliers` | All suppliers with risk and sanctions status | PLANNED |
| GET | `/suppliers/{id}` | Supplier detail | PLANNED |

---

### Refineries

| Method | Endpoint | Description | Status |
|---|---|---|---|
| GET | `/refineries` | All Indian refineries with capacity and compatibility | PLANNED |
| GET | `/refineries/{id}` | Refinery detail with compatible crude grades | PLANNED |
| GET | `/refineries/{id}/exposure` | Current risk exposure for a refinery | PLANNED |

---

### System / Health

| Method | Endpoint | Description | Status |
|---|---|---|---|
| GET | `/health` | System health check | PLANNED |
| GET | `/status/data-sources` | Status of all external data source connections | PLANNED |

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

## Rate Limiting

No rate limiting for Phase 1. External API call rate limiting is handled by the ingestion layer, not the client-facing API.

## CORS

Frontend origin (default `http://localhost:3000`) must be allowed in CORS configuration.
