# INDRA — Database Schema

> **STATUS:** This document defines the planned conceptual and logical schema. The schema has NOT been applied to any database yet.
>
> The `db/schema.sql` file contains the DDL ready for execution when the database is set up.
>
> Source: PETRAS Analysis §9; INDRA Master Report §13

---

## Design Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Database | PostgreSQL 16 (single instance) | Handles structured, semi-structured (JSONB), geospatial (PostGIS), and time-series data. At demo volumes (~hundreds of events, 20 refineries, 50 routes), multi-database architecture is pure overengineering. |
| ORM | SQLAlchemy | Explicit in INDRA Master Report; provides migration support and query building |
| Schema management | Manual DDL + Alembic migrations when needed | Sufficient for hackathon |
| Extensions | PostGIS (geospatial), optionally TimescaleDB (time-series) | PostGIS for map queries; TimescaleDB is optional |

---

## Conceptual Entity Model

```
┌──────────┐     ┌───────────┐     ┌──────────┐
│ Country  │────▶│ Supplier  │────▶│ Crude    │
│          │     │           │     │ Grade    │
└──────────┘     └───────────┘     └──────┬───┘
     │                                     │
     │           ┌───────────┐             │
     └──────────▶│   Port    │◀────────────┘
                 └─────┬─────┘      compatibility
                       │
                 ┌─────▼─────┐     ┌──────────┐
                 │   Route   │────▶│Chokepoint│
                 └─────┬─────┘     └──────────┘
                       │
                 ┌─────▼─────┐     ┌──────────┐
                 │ Refinery  │◀───▶│ Compat.  │
                 └───────────┘     │ Matrix   │
                                   └──────────┘
┌──────────────┐
│ Geopolitical │     ┌──────────┐     ┌──────────────┐
│ Event        │────▶│Risk Score│────▶│ Scenario     │
└──────────────┘     └──────────┘     │ Result       │
                                      └──────┬───────┘
                                             │
                                      ┌──────▼───────┐
                                      │ Procurement  │
                                      │ Option       │
                                      └──────────────┘

┌──────────────┐     ┌──────────┐
│ Strategic    │     │ Crude    │
│ Reserve      │     │ Price    │
└──────────────┘     └──────────┘
```

---

## Planned Tables

### Core Reference Entities

#### `countries`
Supplier and transit countries with base risk profiles.

| Column | Type | Notes |
|---|---|---|
| id | SERIAL PK | |
| name | VARCHAR(100) | |
| iso3 | CHAR(3) UNIQUE | ISO 3166-1 alpha-3 |
| base_risk_score | DECIMAL(5,3) | Static country risk baseline |
| region | VARCHAR(50) | Middle East, Africa, Americas, etc. |
| is_hormuz_dependent | BOOLEAN | Does export route transit Hormuz? |
| is_red_sea_dependent | BOOLEAN | Does export route transit Red Sea? |

#### `suppliers`
Crude oil supplier entities (companies or state entities).

| Column | Type | Notes |
|---|---|---|
| id | SERIAL PK | |
| name | VARCHAR(200) | |
| country_id | INT FK → countries | |
| crude_grades | TEXT[] | Array of grade names |
| annual_supply_capacity_mmtpa | DECIMAL(8,2) | |
| current_sanctions_risk | DECIMAL(5,3) | |
| is_sanctioned | BOOLEAN | |
| sanction_source | VARCHAR(50) | OFAC, EU, UN, etc. |

#### `refineries`
Indian refineries with capacity and crude compatibility.

| Column | Type | Notes |
|---|---|---|
| id | SERIAL PK | |
| name | VARCHAR(200) | |
| owner | VARCHAR(100) | IOC, BPCL, HPCL, Reliance, etc. |
| state | VARCHAR(100) | Indian state |
| port_id | INT FK → ports | Nearest receiving port |
| capacity_mmtpa | DECIMAL(8,2) | Annual capacity |
| throughput_current_mmtpa | DECIMAL(8,2) | Current operating throughput |
| compatible_crude_grades | TEXT[] | Array of compatible grade names |
| latitude | DECIMAL(9,6) | |
| longitude | DECIMAL(9,6) | |

#### `ports`
Indian and international crude oil ports.

| Column | Type | Notes |
|---|---|---|
| id | SERIAL PK | |
| name | VARCHAR(200) | |
| un_locode | VARCHAR(10) | UN/LOCODE identifier |
| country_id | INT FK → countries | |
| is_indian | BOOLEAN | |
| latitude | DECIMAL(9,6) | |
| longitude | DECIMAL(9,6) | |
| annual_crude_throughput_mmtpa | DECIMAL(8,2) | |
| current_operational_status | VARCHAR(20) | OPERATIONAL, DISRUPTED, CLOSED |

#### `routes`
Supply routes between ports with chokepoint information.

| Column | Type | Notes |
|---|---|---|
| id | SERIAL PK | |
| name | VARCHAR(200) | Descriptive route name |
| origin_port_id | INT FK → ports | |
| dest_port_id | INT FK → ports | |
| distance_nm | INT | Distance in nautical miles |
| avg_transit_days | DECIMAL(5,2) | |
| passes_through_hormuz | BOOLEAN | |
| passes_through_red_sea | BOOLEAN | |
| passes_through_malacca | BOOLEAN | |
| passes_through_cape | BOOLEAN | |
| base_freight_rate_per_mt | DECIMAL(8,2) | |
| current_risk_score | DECIMAL(5,3) | |
| is_operational | BOOLEAN | |

### Event and Risk Tables

#### `geopolitical_events`
Ingested and classified geopolitical events.

| Column | Type | Notes |
|---|---|---|
| id | SERIAL PK | |
| event_type | VARCHAR(50) | SANCTION, MILITARY, PORT_CLOSURE, ATTACK, DIPLOMATIC, OTHER |
| title | TEXT | |
| description | TEXT | |
| source_url | TEXT | Original source URL |
| source_name | VARCHAR(100) | GDELT, ACLED, OFAC, RSS, etc. |
| country_id | INT FK → countries | |
| affected_route_ids | INT[] | Array of route IDs |
| severity | DECIMAL(5,3) | |
| confidence | DECIMAL(5,3) | LLM extraction confidence |
| occurred_at | TIMESTAMP | When the event happened |
| detected_at | TIMESTAMP | When INDRA ingested it |
| is_verified | BOOLEAN | Cross-source verification |
| raw_text | TEXT | Original article text |
| llm_model_used | VARCHAR(100) | Which LLM extracted this event |
| is_simulated | BOOLEAN | Is this a demo fixture? |

> **Data honesty field:** `is_simulated` is required on every event record. The UI must display this.

#### `risk_scores`
Calculated risk scores with full component breakdown.

| Column | Type | Notes |
|---|---|---|
| id | SERIAL PK | |
| entity_type | VARCHAR(20) | corridor, route, supplier, country |
| entity_id | INT | References the entity |
| score | DECIMAL(5,3) | Composite risk score |
| component_scores | JSONB | Full breakdown of scoring components |
| contributing_event_ids | INT[] | Events that contributed to this score |
| calculated_at | TIMESTAMP | |
| valid_until | TIMESTAMP | Score expiration |
| source | VARCHAR(50) | Algorithm version or model name |
| confidence | DECIMAL(5,3) | |

### Market Data Tables

#### `crude_prices`
Current crude oil prices from EIA.

| Column | Type | Notes |
|---|---|---|
| id | SERIAL PK | |
| grade_name | VARCHAR(100) | Brent, WTI, Dubai, Urals, etc. |
| price_usd_per_barrel | DECIMAL(10,4) | |
| recorded_at | TIMESTAMP | |
| source | VARCHAR(50) | EIA, etc. |

#### `price_history`
Historical price time series.

| Column | Type | Notes |
|---|---|---|
| time | TIMESTAMP | |
| grade_name | VARCHAR(100) | |
| price_usd_per_barrel | DECIMAL(10,4) | |
| usd_inr_rate | DECIMAL(10,4) | |
| price_inr_per_barrel | DECIMAL(12,4) | GENERATED: usd price × fx rate |

### Scenario and Output Tables

#### `scenarios`
User-created or preset scenario definitions.

| Column | Type | Notes |
|---|---|---|
| id | SERIAL PK | |
| name | VARCHAR(200) | |
| scenario_type | VARCHAR(50) | HORMUZ_FULL, HORMUZ_PARTIAL, RUSSIA_LOSS, RED_SEA, PRICE_SPIKE |
| parameters | JSONB | All scenario parameters |
| created_at | TIMESTAMP | |
| created_by | VARCHAR(100) | |

#### `scenario_results`
Computed results from scenario simulations.

| Column | Type | Notes |
|---|---|---|
| id | SERIAL PK | |
| scenario_id | INT FK → scenarios | |
| affected_routes | JSONB | |
| supply_gap_mmt | DECIMAL(8,3) | |
| price_impact_usd_per_barrel | DECIMAL(8,4) | |
| reserve_drawdown_days | DECIMAL(8,2) | |
| gdp_impact_estimate_usd_bn | DECIMAL(10,3) | |
| freight_cost_increase_pct | DECIMAL(8,2) | |
| recommendations | JSONB | |
| calculated_at | TIMESTAMP | |

#### `procurement_options`
Ranked procurement alternatives.

| Column | Type | Notes |
|---|---|---|
| id | SERIAL PK | |
| scenario_id | INT FK → scenarios | Context scenario |
| refinery_id | INT FK → refineries | Target refinery |
| supplier_id | INT FK → suppliers | |
| route_id | INT FK → routes | |
| crude_grade | VARCHAR(100) | |
| volume_available_mmt | DECIMAL(8,3) | |
| price_cif_usd_per_barrel | DECIMAL(10,4) | |
| transit_days | DECIMAL(5,2) | |
| risk_score | DECIMAL(5,3) | |
| compatibility | VARCHAR(10) | HIGH, MEDIUM, LOW |
| is_sanctioned | BOOLEAN | |
| ranking_score | DECIMAL(10,6) | Composite ranking |
| last_updated | TIMESTAMP | |

#### `strategic_reserves`
India's Strategic Petroleum Reserve locations.

| Column | Type | Notes |
|---|---|---|
| id | SERIAL PK | |
| location_name | VARCHAR(200) | |
| operator | VARCHAR(100) | ISPRL |
| state | VARCHAR(100) | Indian state |
| capacity_mmt | DECIMAL(8,3) | |
| current_level_mmt | DECIMAL(8,3) | Estimated |
| days_coverage | DECIMAL(8,2) | GENERATED: level / daily consumption |
| last_updated | TIMESTAMP | |
| latitude | DECIMAL(9,6) | |
| longitude | DECIMAL(9,6) | |
| data_classification | VARCHAR(20) | HISTORICAL, ESTIMATED |

### Transparency Table

#### `data_sources`
Registry of all external data sources and their status.

| Column | Type | Notes |
|---|---|---|
| id | SERIAL PK | |
| name | VARCHAR(100) | GDELT, ACLED, EIA, etc. |
| url | TEXT | |
| update_frequency | VARCHAR(50) | |
| last_fetched_at | TIMESTAMP | |
| status | VARCHAR(20) | ACTIVE, STALE, ERROR, UNAVAILABLE |
| classification | VARCHAR(20) | LIVE, RECENT, HISTORICAL |

---

## Transparency Fields

The INDRA Master Report requires that every important record include:

```
source              — where did this data come from?
source_timestamp    — when was the source data created?
ingested_at         — when did INDRA receive it?
confidence          — how confident is the extraction/calculation?
is_simulated        — is this demo/scenario data?
```

These fields must be present on `geopolitical_events`, `risk_scores`, `procurement_options`, and `strategic_reserves` at minimum.

---

## Conceptual vs Implemented Status

| Entity | Conceptual | Implemented |
|---|---|---|
| countries | ✅ Defined | ❌ Not yet |
| suppliers | ✅ Defined | ❌ Not yet |
| refineries | ✅ Defined | ❌ Not yet |
| ports | ✅ Defined | ❌ Not yet |
| routes | ✅ Defined | ❌ Not yet |
| geopolitical_events | ✅ Defined | ❌ Not yet |
| risk_scores | ✅ Defined | ❌ Not yet |
| crude_prices | ✅ Defined | ❌ Not yet |
| price_history | ✅ Defined | ❌ Not yet |
| scenarios | ✅ Defined | ❌ Not yet |
| scenario_results | ✅ Defined | ❌ Not yet |
| procurement_options | ✅ Defined | ❌ Not yet |
| strategic_reserves | ✅ Defined | ❌ Not yet |
| data_sources | ✅ Defined | ❌ Not yet |
| refinery_compatibility | ✅ Conceptual | ❌ Not yet |

---

## Notes

1. **Risk score scale conflict:** PETRAS uses 0.0–1.0 decimal; INDRA Master uses 0–100 integer. The schema uses DECIMAL(5,3) which can accommodate either. The final scale decision will be made during implementation.

2. **Severity scale conflict:** PETRAS uses 0.0–1.0 float; INDRA Master examples show integer 1–5. The schema uses DECIMAL(5,3). Final decision deferred.

3. **Single PostgreSQL justification:** At most hundreds of events, 20 refineries, 50 routes, 200 procurement options. PostgreSQL JSONB handles semi-structured scenario parameters. PostGIS handles geospatial queries. This is not a scale problem.
