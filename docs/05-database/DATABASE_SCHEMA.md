# INDRA — Database Schema

> **STATUS:** This document defines the planned conceptual and logical schema. The schema has NOT been applied to any database yet.
>
> **Revision:** Post-review corrections applied (Step 1.5). Schema will be frozen in Step 2.
>
> Source: PETRAS Analysis §9; INDRA Master Report §13; Architecture Review corrections

---

## Design Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Database | PostgreSQL 16 (single instance) | Handles structured, semi-structured (JSONB), geospatial (lat/lon), and time-series data. At demo volumes (~hundreds of events, 20 refineries, 50 routes), multi-database architecture is overengineering |
| ORM | SQLAlchemy | Explicit in INDRA Master Report; provides query building |
| Schema management | Manual DDL + Alembic migrations when needed | Sufficient for hackathon |
| Risk scale | Internal: 0.0–1.0 / Display: 0–100 | See §Risk Scale Convention below |
| Extensions | None required for Phase 1 | PostGIS deferred; plain lat/lon columns used |

---

## Risk Scale Convention

> **FROZEN:** All risk/severity/confidence scores in the database use the **internal** 0.0–1.0 scale.
>
> Conversion for display: `display_score = internal_score × 100`
>
> This convention applies to all `DECIMAL(5,3)` score columns across every table.

---

## Conceptual Entity Model

```
┌──────────┐     ┌───────────┐     ┌──────────┐
│ Country  │────▶│ Supplier  │────▶│ Crude    │
│          │     │           │     │ Grade    │
└──────────┘     └───────────┘     └──────┬───┘
     │                                     │
     │           ┌───────────┐             │
     └──────────▶│   Port    │             │
                 └─────┬─────┘      compatibility
                       │               │
                 ┌─────▼─────┐     ┌────▼─────┐
                 │   Route   │     │ Refinery  │
                 └─────┬─────┘     │ Supply Mix│
                       │           └──────────┘
                 ┌─────▼─────┐
                 │ Corridor  │
                 │(chokepoint│
                 │ /region)  │
                 └───────────┘

┌──────────────┐
│ Geopolitical │     ┌──────────┐     ┌──────────────┐
│ Event        │────▶│Risk Score│────▶│ Scenario     │
│              │     └──────────┘     │ Result       │
│ → countries  │                      └──────┬───────┘
│ → corridors  │                             │
│ → routes     │                      ┌──────▼───────┐
└──────────────┘                      │ Procurement  │
                                      │ Option       │
                                      └──────────────┘

┌──────────────┐     ┌──────────┐     ┌──────────────┐
│ Strategic    │     │Commodity │     │ FX Rate      │
│ Reserve      │     │ Price    │     └──────────────┘
└──────────────┘     └──────────┘

┌──────────────┐     ┌──────────────┐
│ Evidence     │────▶│Evidence Link │
│ Record       │     └──────────────┘
└──────────────┘
```

---

## Planned Tables

### Core Reference Entities

#### `countries`
Supplier and transit countries with base risk profiles.

| Column | Type | Notes |
|---|---|---|
| id | SERIAL PK | |
| name | VARCHAR(100) NOT NULL | |
| iso3 | CHAR(3) UNIQUE | ISO 3166-1 alpha-3 |
| base_risk_score | DECIMAL(5,3) | Internal scale 0.0–1.0 |
| region | VARCHAR(50) | Middle East, Africa, Americas, etc. |
| is_hormuz_dependent | BOOLEAN DEFAULT FALSE | Does export route transit Hormuz? |
| is_red_sea_dependent | BOOLEAN DEFAULT FALSE | Does export route transit Red Sea? |
| created_at | TIMESTAMP DEFAULT NOW() | |
| updated_at | TIMESTAMP DEFAULT NOW() | |

#### `corridors`
Strategically meaningful supply-chain/geopolitical corridors and chokepoints.

| Column | Type | Notes |
|---|---|---|
| id | SERIAL PK | |
| code | VARCHAR(20) UNIQUE NOT NULL | Stable identifier: HORMUZ, RED_SEA, RUSSIA, SUEZ, MALACCA, CAPE |
| name | VARCHAR(200) NOT NULL | Human-readable: "Strait of Hormuz" |
| description | TEXT | Strategic significance description |
| corridor_type | VARCHAR(30) | CHOKEPOINT, REGIONAL, SUPPLIER_CORRIDOR |
| affected_countries | TEXT[] | Countries whose supply transits or depends on this corridor |
| base_risk_score | DECIMAL(5,3) | Baseline geopolitical risk (0.0–1.0 internal) |
| india_dependency_share | DECIMAL(5,3) | Fraction of India's imports affected (e.g., 0.42 for Hormuz) |
| is_active | BOOLEAN DEFAULT TRUE | Can be deactivated for scenarios |
| created_at | TIMESTAMP DEFAULT NOW() | |
| updated_at | TIMESTAMP DEFAULT NOW() | |

> **Phase 1 corridors:** HORMUZ, RED_SEA, SUEZ, MALACCA, RUSSIA, CAPE. Additional corridors only if supported by the research reports.

#### `crude_grades`
Controlled vocabulary for crude oil grades. Replaces free-form text everywhere.

| Column | Type | Notes |
|---|---|---|
| id | SERIAL PK | |
| name | VARCHAR(100) UNIQUE NOT NULL | Canonical name: "Arab Light", "Urals", "Basrah Light" |
| api_gravity | DECIMAL(5,2) | Degrees API (light/heavy indicator) |
| sulfur_content_pct | DECIMAL(5,3) | Sulfur % (sweet/sour indicator) |
| category | VARCHAR(20) | LIGHT_SWEET, LIGHT_SOUR, MEDIUM_SOUR, HEAVY_SOUR |
| origin_country_id | INT FK → countries | Primary producing country |
| notes | TEXT | Source/assumptions for data |

> **Phase 1 scope:** ~10–15 crude grades relevant to India's import basket. Not a global taxonomy.

#### `suppliers`
Crude oil supplier entities (companies or state entities).

| Column | Type | Notes |
|---|---|---|
| id | SERIAL PK | |
| name | VARCHAR(200) NOT NULL | |
| country_id | INT FK → countries | |
| crude_grade_ids | INT[] | FK references to crude_grades table |
| annual_supply_capacity_mmtpa | DECIMAL(8,2) | |
| current_sanctions_risk | DECIMAL(5,3) | Internal 0.0–1.0 |
| is_sanctioned | BOOLEAN DEFAULT FALSE | |
| sanction_source | VARCHAR(50) | OFAC, EU, UN, etc. |
| created_at | TIMESTAMP DEFAULT NOW() | |
| updated_at | TIMESTAMP DEFAULT NOW() | |

#### `ports`
Indian and international crude oil ports.

| Column | Type | Notes |
|---|---|---|
| id | SERIAL PK | |
| name | VARCHAR(200) NOT NULL | |
| un_locode | VARCHAR(10) | UN/LOCODE identifier |
| country_id | INT FK → countries | |
| is_indian | BOOLEAN DEFAULT FALSE | |
| latitude | DECIMAL(9,6) | |
| longitude | DECIMAL(9,6) | |
| annual_crude_throughput_mmtpa | DECIMAL(8,2) | |
| current_operational_status | VARCHAR(20) DEFAULT 'OPERATIONAL' | OPERATIONAL, DISRUPTED, CLOSED |
| created_at | TIMESTAMP DEFAULT NOW() | |
| updated_at | TIMESTAMP DEFAULT NOW() | |

#### `refineries`
Indian refineries with capacity and crude compatibility.

| Column | Type | Notes |
|---|---|---|
| id | SERIAL PK | |
| name | VARCHAR(200) NOT NULL | |
| owner | VARCHAR(100) | IOC, BPCL, HPCL, Reliance, etc. |
| state | VARCHAR(100) | Indian state |
| port_id | INT FK → ports | Nearest receiving port |
| capacity_mmtpa | DECIMAL(8,2) | Annual capacity |
| throughput_current_mmtpa | DECIMAL(8,2) | Current operating throughput |
| latitude | DECIMAL(9,6) | |
| longitude | DECIMAL(9,6) | |
| created_at | TIMESTAMP DEFAULT NOW() | |
| updated_at | TIMESTAMP DEFAULT NOW() | |

> **NOTE:** Crude compatibility is now modeled via `refinery_supply_mix`, not TEXT[] arrays on this table.

#### `refinery_supply_mix`
Refinery-level crude grade compatibility and supply allocation.

| Column | Type | Notes |
|---|---|---|
| id | SERIAL PK | |
| refinery_id | INT FK → refineries NOT NULL | |
| crude_grade_id | INT FK → crude_grades NOT NULL | |
| compatibility | VARCHAR(10) NOT NULL | HIGH, MEDIUM, LOW, NONE |
| compatibility_score | DECIMAL(3,2) | Numeric: 0.0–1.0 (where 1.0 = fully compatible) |
| current_share_pct | DECIMAL(5,2) | Current % of refinery intake from this grade. NULL if unknown |
| max_share_pct | DECIMAL(5,2) | Maximum processable % of this grade. NULL if unknown |
| source_type | VARCHAR(30) | PPAC_REPORTED, COMPANY_REPORT, ESTIMATED, UNKNOWN |
| notes | TEXT | Assumptions, caveats |
| updated_at | TIMESTAMP DEFAULT NOW() | |

> **UNIQUE constraint:** (refinery_id, crude_grade_id) — one row per refinery-grade combination.
>
> **Seed data rule:** If actual share data is not available from PPAC or company reports, mark `source_type = 'ESTIMATED'` or `'UNKNOWN'` and document the assumption. Do not invent percentages.

#### `routes`
Supply routes between ports with corridor/chokepoint information.

| Column | Type | Notes |
|---|---|---|
| id | SERIAL PK | |
| name | VARCHAR(200) NOT NULL | Descriptive route name |
| origin_port_id | INT FK → ports | |
| dest_port_id | INT FK → ports | |
| corridor_ids | INT[] | FK references to corridors table — which corridors this route transits |
| distance_nm | INT | Distance in nautical miles |
| avg_transit_days | DECIMAL(5,2) | |
| base_freight_rate_per_mt | DECIMAL(8,2) | |
| current_risk_score | DECIMAL(5,3) | Internal 0.0–1.0 |
| is_operational | BOOLEAN DEFAULT TRUE | |
| created_at | TIMESTAMP DEFAULT NOW() | |
| updated_at | TIMESTAMP DEFAULT NOW() | |

> **NOTE:** The previous boolean columns (`passes_through_hormuz`, `passes_through_red_sea`, etc.) are replaced by the `corridor_ids` array referencing the `corridors` table. This allows dynamic corridor definitions and avoids adding a new boolean column for every corridor.

### Event and Risk Tables

#### `geopolitical_events`
Ingested and classified geopolitical events.

| Column | Type | Notes |
|---|---|---|
| id | SERIAL PK | |
| event_type | VARCHAR(50) | SANCTION, MILITARY, PORT_CLOSURE, ATTACK, DIPLOMATIC, OTHER |
| title | TEXT NOT NULL | |
| description | TEXT | |
| source_url | TEXT | Original source URL |
| source_name | VARCHAR(100) | GDELT, ACLED, OFAC, RSS, etc. |
| affected_country_ids | INT[] | FK refs → countries. Supports multiple countries per event |
| affected_corridor_ids | INT[] | FK refs → corridors. Which corridors are affected |
| affected_route_ids | INT[] | FK refs → routes. Specific routes if identified |
| severity | DECIMAL(5,3) | Internal 0.0–1.0 |
| confidence | DECIMAL(5,3) | LLM extraction confidence, 0.0–1.0 |
| occurred_at | TIMESTAMP | When the event happened |
| detected_at | TIMESTAMP DEFAULT NOW() | When INDRA ingested it |
| is_verified | BOOLEAN DEFAULT FALSE | Cross-source verification |
| raw_text | TEXT | Original article text (truncated for storage) |
| llm_model_used | VARCHAR(100) | Which LLM extracted this event |
| is_simulated | BOOLEAN DEFAULT FALSE | Is this a demo fixture? |

> **Relationship rule:** An event may have:
> - One or more affected countries
> - One or more affected corridors
> - Zero or more directly mapped routes
>
> Not every event maps to a specific route. Corridor-level association is the minimum meaningful resolution.
>
> **Data honesty field:** `is_simulated` is required on every event record. The UI must display this.

#### `risk_scores`
Calculated risk scores with full component breakdown.

| Column | Type | Notes |
|---|---|---|
| id | SERIAL PK | |
| entity_type | VARCHAR(20) | corridor, route, supplier, country |
| entity_id | INT NOT NULL | References the entity |
| score | DECIMAL(5,3) NOT NULL | Internal 0.0–1.0 |
| risk_level | VARCHAR(10) | LOW, MODERATE, HIGH, CRITICAL, EXTREME |
| component_scores | JSONB | Full breakdown of scoring components (all in 0.0–1.0) |
| contributing_event_ids | INT[] | Events that contributed to this score |
| calculated_at | TIMESTAMP DEFAULT NOW() | |
| valid_until | TIMESTAMP | Score expiration |
| calculation_method | VARCHAR(50) | "weighted_rule_v1", "xgboost_v1", etc. |
| confidence | DECIMAL(5,3) | 0.0–1.0 |

> **Risk level classification (applied to internal 0.0–1.0 score):**
> ```
> 0.00–0.29   LOW
> 0.30–0.49   MODERATE
> 0.50–0.69   HIGH
> 0.70–0.84   CRITICAL
> 0.85–1.00   EXTREME
> ```

### Market Data Tables

#### `commodity_prices`
Commodity price observations from external sources.

| Column | Type | Notes |
|---|---|---|
| id | SERIAL PK | |
| grade_name | VARCHAR(100) | Brent, WTI, Dubai, Urals, etc. |
| crude_grade_id | INT FK → crude_grades | NULL for benchmark grades not in the crude_grades table |
| price_usd_per_barrel | DECIMAL(10,4) NOT NULL | |
| source | VARCHAR(50) NOT NULL | EIA, World Bank, etc. |
| source_timestamp | TIMESTAMP | When the source published this price |
| observed_at | TIMESTAMP DEFAULT NOW() | When INDRA recorded it |
| data_semantic | VARCHAR(30) DEFAULT 'OBSERVED' | OBSERVED, HISTORICAL |

> **Replaces** both the old `crude_prices` and `price_history` tables. All price observations go here. Current price = most recent `observed_at` for a given grade.

#### `fx_rates`
Foreign exchange rate observations.

| Column | Type | Notes |
|---|---|---|
| id | SERIAL PK | |
| currency_pair | VARCHAR(10) NOT NULL | "USD_INR" |
| rate | DECIMAL(10,4) NOT NULL | |
| source | VARCHAR(50) NOT NULL | RBI, etc. |
| source_timestamp | TIMESTAMP | When the source published this rate |
| observed_at | TIMESTAMP DEFAULT NOW() | When INDRA recorded it |
| data_semantic | VARCHAR(30) DEFAULT 'OBSERVED' | OBSERVED, HISTORICAL |

> **INR price derivation rule:** To compute INR-denominated crude prices, the application layer must:
> 1. Take the commodity price record with `source_timestamp` = T₁
> 2. Find the FX rate with the nearest `source_timestamp` ≤ T₁ (nearest-valid-prior rule)
> 3. Compute: `price_inr = price_usd × fx_rate`
> 4. Record the derivation with both source timestamps in the evidence trail
>
> This is a **query-time calculation**, not a stored generated column.

### Scenario and Output Tables

#### `scenarios`
User-created or preset scenario definitions.

| Column | Type | Notes |
|---|---|---|
| id | SERIAL PK | |
| name | VARCHAR(200) NOT NULL | |
| scenario_type | VARCHAR(50) | HORMUZ_FULL, HORMUZ_PARTIAL, RUSSIA_LOSS, RED_SEA, PRICE_SPIKE |
| parameters | JSONB | All scenario parameters |
| created_at | TIMESTAMP DEFAULT NOW() | |
| created_by | VARCHAR(100) | |

#### `scenario_results`
Computed results from scenario simulations.

| Column | Type | Notes |
|---|---|---|
| id | SERIAL PK | |
| scenario_id | INT FK → scenarios NOT NULL | |
| affected_corridors | JSONB | Which corridors are disrupted and how |
| affected_routes | JSONB | Which routes are affected |
| supply_gap_mmt | DECIMAL(8,3) | |
| price_impact_usd_per_barrel | DECIMAL(8,4) | |
| freight_cost_increase_pct | DECIMAL(8,2) | |
| spr_bridge | JSONB | { required_mmt, available_mmt, days_bridged, uncovered_gap_mmt } |
| affected_refineries | JSONB | Per-refinery impact breakdown |
| assumptions | JSONB | All assumptions used, with data_semantic tags |
| calculated_at | TIMESTAMP DEFAULT NOW() | |

> **REMOVED:** `gdp_impact_estimate_usd_bn` — GDP impact estimation requires macroeconomic modeling beyond this system's scope. Removed from MVP per architecture review.
>
> **REMOVED:** `reserve_drawdown_days` — replaced by structured `spr_bridge` JSONB with explicit days_bridged field.
>
> **REMOVED:** `recommendations` JSONB — procurement recommendations are stored in `procurement_options` table, not duplicated here.

#### `procurement_options`
Ranked procurement alternatives.

| Column | Type | Notes |
|---|---|---|
| id | SERIAL PK | |
| scenario_id | INT FK → scenarios NOT NULL | Context scenario |
| refinery_id | INT FK → refineries NOT NULL | Target refinery |
| supplier_id | INT FK → suppliers | |
| route_id | INT FK → routes | |
| crude_grade_id | INT FK → crude_grades | |
| volume_available_mmt | DECIMAL(8,3) | |
| price_cif_usd_per_barrel | DECIMAL(10,4) | |
| transit_days | DECIMAL(5,2) | |
| risk_score | DECIMAL(5,3) | Internal 0.0–1.0 |
| compatibility | VARCHAR(10) | HIGH, MEDIUM, LOW |
| is_sanctioned | BOOLEAN DEFAULT FALSE | |
| ranking_score | DECIMAL(10,6) | Composite ranking score |
| scoring_breakdown | JSONB | Component scores used in ranking |
| created_at | TIMESTAMP DEFAULT NOW() | |

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
| last_updated | TIMESTAMP DEFAULT NOW() | |
| latitude | DECIMAL(9,6) | |
| longitude | DECIMAL(9,6) | |
| data_classification | VARCHAR(20) DEFAULT 'HISTORICAL' | HISTORICAL, ESTIMATED |

> **REMOVED:** `days_coverage` GENERATED column. Days of coverage is now computed at the application/query layer:
> ```
> days_coverage = current_level_mmt / india_daily_consumption_mmt
> ```
> where `india_daily_consumption_mmt` comes from configuration or the scenario context, not a hardcoded constant.

### Provenance / Evidence Tables

#### `evidence_records`
Source and processing provenance for traceability.

| Column | Type | Notes |
|---|---|---|
| id | SERIAL PK | |
| evidence_type | VARCHAR(30) NOT NULL | SOURCE, LLM_EXTRACTION, ENTITY_RESOLUTION, RISK_CALCULATION, SCENARIO_COMPUTATION, OPTIMIZATION, RECOMMENDATION |
| source_url | TEXT | Original source URL (for SOURCE type) |
| source_name | VARCHAR(100) | Data source identifier |
| timestamp | TIMESTAMP DEFAULT NOW() | When this evidence was created |
| related_entity_type | VARCHAR(30) | event, risk_score, scenario_result, procurement_option |
| related_entity_id | INT | FK to the related entity |
| model_or_method | VARCHAR(100) | LLM model name, algorithm version, formula ID |
| input_summary | JSONB | Summary of inputs used |
| output_summary | JSONB | Summary of outputs produced |
| data_semantic | VARCHAR(30) | OBSERVED, DERIVED, HISTORICAL_CALIBRATED, ASSUMED, SIMULATED |
| confidence | DECIMAL(5,3) | 0.0–1.0 |
| notes | TEXT | Human-readable context |

#### `evidence_links`
Connects evidence records into chains (source → extraction → risk → scenario → recommendation).

| Column | Type | Notes |
|---|---|---|
| id | SERIAL PK | |
| parent_evidence_id | INT FK → evidence_records NOT NULL | Upstream evidence |
| child_evidence_id | INT FK → evidence_records NOT NULL | Downstream evidence |
| relationship | VARCHAR(30) | DERIVED_FROM, CONTRIBUTED_TO, USED_IN |

> **Provenance chain example:**
> ```
> evidence[SOURCE: Reuters article]
>     → evidence[LLM_EXTRACTION: structured event]
>         → evidence[ENTITY_RESOLUTION: mapped to corridor HORMUZ]
>             → evidence[RISK_CALCULATION: Hormuz score = 0.78]
>                 → evidence[SCENARIO_COMPUTATION: 7.06 MMT gap]
>                     → evidence[OPTIMIZATION: Arab Light ranked #1]
> ```
>
> The UI evidence drawer traverses this chain to show the full source → recommendation path.

### Data Source Tracking

#### `data_sources`
Registry of all external data sources and their status.

| Column | Type | Notes |
|---|---|---|
| id | SERIAL PK | |
| name | VARCHAR(100) NOT NULL | GDELT, ACLED, EIA, etc. |
| url | TEXT | |
| update_frequency | VARCHAR(50) | |
| last_fetched_at | TIMESTAMP | |
| status | VARCHAR(20) DEFAULT 'ACTIVE' | ACTIVE, STALE, ERROR, UNAVAILABLE |
| classification | VARCHAR(20) | OBSERVED, HISTORICAL_CALIBRATED |

### Entity Resolution Support

#### `entity_aliases`
Alias table for entity resolution. Maps variant names to canonical entities.

| Column | Type | Notes |
|---|---|---|
| id | SERIAL PK | |
| alias | VARCHAR(200) NOT NULL | The variant string (e.g., "Saudi Aramco", "Hormuz") |
| canonical_entity_type | VARCHAR(30) NOT NULL | country, corridor, supplier, port, refinery, crude_grade |
| canonical_entity_id | INT NOT NULL | FK to the corresponding reference table |
| match_type | VARCHAR(20) | EXACT, FUZZY, ALIAS |
| created_at | TIMESTAMP DEFAULT NOW() | |

> **Purpose:** When the LLM outputs `"corridor_names": ["HORMUZ"]` or `"country_names": ["Iran"]`, the entity resolution layer looks up this table to map human-readable names to internal IDs.
>
> **Phase 1 strategy:** Pre-populate ~50–100 aliases covering key entities. Use RapidFuzz for fuzzy matching against this table when exact match fails.

---

## Data Semantic Classification

Every major data value should carry a semantic tag indicating its provenance category:

| Classification | Definition | Example |
|---|---|---|
| **OBSERVED** | Directly fetched from an external API/source | EIA Brent price, GDELT event, OFAC sanctions entry |
| **DERIVED** | Calculated from observed values using a documented formula | Risk score, supply gap, procurement ranking |
| **HISTORICAL_CALIBRATED** | Parameter derived from analysis of historical events | $15/bbl Hormuz closure price impact (from Gulf War II data) |
| **ASSUMED** | Configuration/user assumption not derived from data | Freight multiplier, risk weight, compatibility score estimate |
| **SIMULATED** | Synthetic state generated for scenario/demo purposes | Scenario disruption level, demo fixture events |

The `data_semantic` column on `evidence_records`, `commodity_prices`, and `fx_rates` enforces this classification. The `is_simulated` flag on `geopolitical_events` is a shortcut for the most critical case.

---

## Transparency Fields

Every important record must include sufficient provenance information:

```
source              — where did this data come from?
source_timestamp    — when was the source data created?
observed_at         — when did INDRA receive it?
confidence          — how confident is the extraction/calculation? (0.0–1.0)
data_semantic       — OBSERVED / DERIVED / HISTORICAL_CALIBRATED / ASSUMED / SIMULATED
is_simulated        — is this demo/scenario data? (shortcut for events)
```

---

## Conceptual vs Implemented Status

| Entity | Conceptual | Implemented |
|---|---|---|
| countries | ✅ Defined | ❌ Not yet |
| corridors | ✅ Defined | ❌ Not yet |
| crude_grades | ✅ Defined | ❌ Not yet |
| suppliers | ✅ Defined | ❌ Not yet |
| refineries | ✅ Defined | ❌ Not yet |
| refinery_supply_mix | ✅ Defined | ❌ Not yet |
| ports | ✅ Defined | ❌ Not yet |
| routes | ✅ Defined | ❌ Not yet |
| geopolitical_events | ✅ Defined | ❌ Not yet |
| risk_scores | ✅ Defined | ❌ Not yet |
| commodity_prices | ✅ Defined | ❌ Not yet |
| fx_rates | ✅ Defined | ❌ Not yet |
| scenarios | ✅ Defined | ❌ Not yet |
| scenario_results | ✅ Defined | ❌ Not yet |
| procurement_options | ✅ Defined | ❌ Not yet |
| strategic_reserves | ✅ Defined | ❌ Not yet |
| evidence_records | ✅ Defined | ❌ Not yet |
| evidence_links | ✅ Defined | ❌ Not yet |
| data_sources | ✅ Defined | ❌ Not yet |
| entity_aliases | ✅ Defined | ❌ Not yet |

---

## Notes

1. **Risk score scale:** FROZEN. Internal = 0.0–1.0. Display = 0–100. All DECIMAL(5,3) score columns store 0.0–1.0. Conversion happens at the API/UI layer.

2. **Single PostgreSQL justification:** At most hundreds of events, 20 refineries, 50 routes, 200 procurement options. PostgreSQL JSONB handles semi-structured scenario parameters. Plain lat/lon handles coordinates. This is not a scale problem.

3. **Price/FX derivation:** INR prices are computed at query time using the nearest-valid-prior FX rate, not stored as generated columns. Both source timestamps are recorded in the evidence trail.

4. **Entity resolution:** The `entity_aliases` table + RapidFuzz provides Phase 1 entity resolution. The LLM outputs human-readable names; the entity resolution layer maps them to database IDs before insertion.
