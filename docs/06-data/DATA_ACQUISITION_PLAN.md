# INDRA — Data Acquisition Plan

> **Step 4 — India Supply-Chain Data Foundation**
>
> This document specifies every dataset required, its source, access method, fields, semantic classification, and target database table.
>
> **Date:** 21 August 2026

---

## Acquisition Policy

1. **No fabricated data.** Every value must be traceable to a documented source.
2. **Estimation must be explicit.** Values marked ESTIMATED or UNKNOWN with methodology documented.
3. **Raw sources preserved.** Original downloads stored separately from normalized data.
4. **Provenance required.** Every dataset has a manifest entry with source, timestamp, and transformation.

---

## Dataset Group A — Countries

| Field | Detail |
|---|---|
| **Target entity** | `countries` |
| **Required fields** | name, iso3, region, is_hormuz_dependent, is_red_sea_dependent |
| **Source** | ISO 3166-1 standard; research reports for Hormuz/Red Sea dependency classification |
| **Source URL** | iso.org/iso-3166-country-codes.html |
| **Source organization** | ISO / INDRA research reports |
| **Access method** | Manual curation from ISO standard + research report §6 |
| **Format** | CSV (manual) |
| **Update frequency** | Static reference data |
| **Historical coverage** | N/A |
| **Data semantics** | OBSERVED (ISO codes), HISTORICAL_CALIBRATED (dependency flags) |
| **License** | ISO codes are public reference; dependency flags from INDRA research |
| **Expected cleaning** | Normalize country names, verify ISO3 codes |
| **Target DB table** | `countries` |
| **Provenance** | ISO 3166-1 + PPAC import-by-source data for dependency classification |
| **Sufficient?** | ✅ Yes |
| **Missing fields** | `base_risk_score` — deferred to risk engine (Step 5+) |
| **Estimation allowed?** | No — only factual reference data |
| **Manual curation required?** | ✅ Yes — select ~15 countries relevant to India's crude supply chain |

### Field-Level Mapping

| Target field | Source | Semantic class | Status |
|---|---|---|---|
| name | ISO 3166-1 | OBSERVED | AVAILABLE |
| iso3 | ISO 3166-1 alpha-3 | OBSERVED | AVAILABLE |
| region | Manual classification | ASSUMED | CURATED |
| base_risk_score | Risk engine output | DERIVED | DEFERRED (NULL) |
| is_hormuz_dependent | Research reports + PPAC source data | HISTORICAL_CALIBRATED | CURATED |
| is_red_sea_dependent | Research reports + PPAC source data | HISTORICAL_CALIBRATED | CURATED |

---

## Dataset Group B — Corridors

| Field | Detail |
|---|---|
| **Target entity** | `corridors` |
| **Required fields** | code, name, description, corridor_type, affected_countries, base_risk_score, india_dependency_share |
| **Source** | INDRA architecture docs (DATABASE_SCHEMA.md §corridors); research reports |
| **Source URL** | Internal architecture documentation |
| **Source organization** | INDRA project |
| **Access method** | Manual curation from architecture + research |
| **Format** | CSV (manual) |
| **Update frequency** | Static reference data |
| **Data semantics** | ASSUMED (corridor definitions), HISTORICAL_CALIBRATED (dependency shares from PPAC) |
| **Target DB table** | `corridors` |
| **Sufficient?** | ✅ Yes for Phase 1 |
| **Missing fields** | None — all frozen schema fields can be populated |
| **Estimation allowed?** | ✅ For `india_dependency_share` using PPAC import-by-source data |
| **Manual curation required?** | ✅ Yes |

### Field-Level Mapping

| Target field | Source | Semantic class | Status |
|---|---|---|---|
| code | Architecture docs | ASSUMED | CURATED |
| name | Architecture docs | ASSUMED | CURATED |
| description | Research reports | ASSUMED | CURATED |
| corridor_type | Architecture docs | ASSUMED | CURATED |
| affected_countries | Research reports + PPAC | HISTORICAL_CALIBRATED | CURATED |
| base_risk_score | Research reports (scenario calibration data) | HISTORICAL_CALIBRATED | ESTIMATED |
| india_dependency_share | PPAC import-by-source FY2024-25 | HISTORICAL_CALIBRATED | CURATED |

---

## Dataset Group C — Ports

| Field | Detail |
|---|---|
| **Target entity** | `ports` |
| **Required fields** | name, un_locode, country_id, is_indian, latitude, longitude |
| **Source** | Indian Port Association; UN/LOCODE database; research reports §6 |
| **Source URL** | unece.org/trade/cefact/unlocode-code-list-country-and-territory (UN/LOCODE); indianports.gov.in |
| **Source organization** | UNECE (UN/LOCODE), Indian Port Association, PPAC |
| **Access method** | Manual curation from UN/LOCODE + research report refinery/port data |
| **Format** | CSV (manual) |
| **Update frequency** | Static reference data |
| **Data semantics** | OBSERVED (coordinates, LOCODE), ASSUMED (crude throughput estimates) |
| **Target DB table** | `ports` |
| **Sufficient?** | ✅ Yes |
| **Missing fields** | `annual_crude_throughput_mmtpa` — not available for all ports |
| **Estimation allowed?** | ✅ For throughput, marked ESTIMATED |
| **Manual curation required?** | ✅ Yes — select ~20 ports relevant to India crude supply chain |

### Field-Level Mapping

| Target field | Source | Semantic class | Status |
|---|---|---|---|
| name | UN/LOCODE + IPA | OBSERVED | AVAILABLE |
| un_locode | UN/LOCODE database | OBSERVED | AVAILABLE |
| country_id | FK → countries | OBSERVED | DERIVED |
| is_indian | Manual flag | OBSERVED | CURATED |
| latitude | UN/LOCODE / public geo data | OBSERVED | AVAILABLE |
| longitude | UN/LOCODE / public geo data | OBSERVED | AVAILABLE |
| annual_crude_throughput_mmtpa | PPAC / port authority | HISTORICAL_CALIBRATED | PARTIAL |

---

## Dataset Group D — Refineries

| Field | Detail |
|---|---|
| **Target entity** | `refineries` |
| **Required fields** | name, owner, state, capacity_mmtpa, latitude, longitude |
| **Source** | PPAC Annual Report 2024-25; company annual reports; research report §6 |
| **Source URL** | ppac.gov.in |
| **Source organization** | PPAC (MoPNG), company reports |
| **Access method** | Manual curation from PPAC data in research reports |
| **Format** | CSV (manual) |
| **Update frequency** | Annual (PPAC report cycle) |
| **Historical coverage** | FY2024-25 |
| **Data semantics** | HISTORICAL_CALIBRATED (capacities from PPAC) |
| **Target DB table** | `refineries` |
| **Sufficient?** | ✅ Yes |
| **Missing fields** | `throughput_current_mmtpa` — not available for all refineries (set NULL) |
| **Estimation allowed?** | ❌ No — do not fabricate throughput. Use NULL. |
| **Manual curation required?** | ✅ Yes |

### Field-Level Mapping

| Target field | Source | Semantic class | Status |
|---|---|---|---|
| name | PPAC / research report | OBSERVED | AVAILABLE |
| owner | PPAC / company reports | OBSERVED | AVAILABLE |
| state | Public knowledge | OBSERVED | AVAILABLE |
| port_id | FK → ports (nearest crude-receiving port) | ASSUMED | CURATED |
| capacity_mmtpa | PPAC Annual Report | HISTORICAL_CALIBRATED | AVAILABLE |
| throughput_current_mmtpa | Company reports | HISTORICAL_CALIBRATED | PARTIAL (NULL if unknown) |
| latitude | Public geo data | OBSERVED | AVAILABLE |
| longitude | Public geo data | OBSERVED | AVAILABLE |

---

## Dataset Group E — Suppliers

| Field | Detail |
|---|---|
| **Target entity** | `suppliers` |
| **Required fields** | name, country_id, crude_grade_ids, is_sanctioned |
| **Source** | PPAC import-by-source; OFAC SDN list; research reports |
| **Source URL** | ppac.gov.in; sanctionslist.treasury.gov |
| **Source organization** | PPAC, OFAC, research reports |
| **Access method** | Manual curation from research report §6 + PPAC data |
| **Format** | CSV (manual) |
| **Data semantics** | HISTORICAL_CALIBRATED (supply shares), OBSERVED (sanctions status) |
| **Target DB table** | `suppliers` |
| **Sufficient?** | ✅ Yes for Phase 1 |
| **Missing fields** | `annual_supply_capacity_mmtpa` — approximate only |
| **Estimation allowed?** | ✅ For capacity, marked ESTIMATED |
| **Manual curation required?** | ✅ Yes |

### Field-Level Mapping

| Target field | Source | Semantic class | Status |
|---|---|---|---|
| name | Research reports / PPAC | OBSERVED | AVAILABLE |
| country_id | FK → countries | OBSERVED | DERIVED |
| crude_grade_ids | FK → crude_grades | HISTORICAL_CALIBRATED | CURATED |
| annual_supply_capacity_mmtpa | EIA / research reports | HISTORICAL_CALIBRATED | ESTIMATED |
| current_sanctions_risk | OFAC / research | OBSERVED | AVAILABLE |
| is_sanctioned | OFAC SDN list | OBSERVED | AVAILABLE |
| sanction_source | OFAC | OBSERVED | AVAILABLE |

---

## Dataset Group F — Crude Grades

| Field | Detail |
|---|---|
| **Target entity** | `crude_grades` |
| **Required fields** | name, api_gravity, sulfur_content_pct, category, origin_country_id |
| **Source** | EIA crude grade reference; industry standard references; research reports |
| **Source URL** | eia.gov |
| **Source organization** | EIA, industry references |
| **Access method** | Manual curation from authoritative crude grade data |
| **Format** | CSV (manual) |
| **Data semantics** | OBSERVED (API gravity, sulfur from official specs) |
| **Target DB table** | `crude_grades` |
| **Sufficient?** | ✅ Yes |
| **Missing fields** | None |
| **Estimation allowed?** | ❌ No — only use reliably sourced API gravity / sulfur values |
| **Manual curation required?** | ✅ Yes |

### Field-Level Mapping

| Target field | Source | Semantic class | Status |
|---|---|---|---|
| name | Industry standard names | OBSERVED | AVAILABLE |
| api_gravity | EIA / industry specs | OBSERVED | AVAILABLE |
| sulfur_content_pct | EIA / industry specs | OBSERVED | AVAILABLE |
| category | Derived from API gravity + sulfur | DERIVED | AVAILABLE |
| origin_country_id | FK → countries | OBSERVED | AVAILABLE |
| notes | Source references | N/A | AVAILABLE |

---

## Dataset Group G — Refinery Supply Mix

| Field | Detail |
|---|---|
| **Target entity** | `refinery_supply_mix` |
| **Required fields** | refinery_id, crude_grade_id, compatibility, source_type |
| **Source** | Research report crude-slate categories; PPAC partial; company reports |
| **Source URL** | Research reports §6 |
| **Source organization** | INDRA research / PPAC |
| **Access method** | Manual curation; cross-reference research report crude-slate categories |
| **Format** | CSV (manual) |
| **Data semantics** | ESTIMATED (compatibility scores), UNKNOWN (exact shares) |
| **Target DB table** | `refinery_supply_mix` |
| **Sufficient?** | ⚠️ Partial — exact share percentages are NOT available from public sources |
| **Missing fields** | `current_share_pct`, `max_share_pct` — mostly NULL/UNKNOWN |
| **Estimation allowed?** | ✅ For compatibility (HIGH/MEDIUM/LOW), marked ESTIMATED |
| **Manual curation required?** | ✅ Yes — this is the most labor-intensive seed dataset |

### Estimation Methodology

Compatibility is derived from refinery crude-slate category (from research report):
- "Complex, heavy sour" → HIGH compatibility with heavy sour grades, MEDIUM with medium, LOW with light
- "Light" → HIGH with light sweet grades, LOW with heavy sour
- "Medium sour" → HIGH with medium sour, MEDIUM with light and heavy

`source_type` = `'ESTIMATED'` for all compatibility-derived values. `current_share_pct` and `max_share_pct` are NULL unless PPAC or company reports provide actual data.

---

## Dataset Group H — Routes

| Field | Detail |
|---|---|
| **Target entity** | `routes` |
| **Required fields** | name, origin_port_id, dest_port_id, corridor_ids, distance_nm, avg_transit_days |
| **Source** | Nautical distance references; research reports; industry transit-time standards |
| **Source URL** | sea-distances.org (public reference), ports.com |
| **Source organization** | Public maritime references |
| **Access method** | Manual curation from nautical distance databases + research |
| **Format** | CSV (manual) |
| **Data semantics** | OBSERVED (distances from reference), ESTIMATED (transit times at standard VLCC speed) |
| **Target DB table** | `routes` |
| **Sufficient?** | ✅ Yes |
| **Missing fields** | `base_freight_rate_per_mt` — volatile, not seeded with static values |
| **Estimation allowed?** | ✅ For transit times (distance / avg VLCC speed) |
| **Manual curation required?** | ✅ Yes |

### Transit Time Estimation

`avg_transit_days = distance_nm / (14 knots × 24 hours/day)` — standard VLCC cruising speed.
This is marked as `ESTIMATED` in provenance.

---

## Dataset Group I — Strategic Petroleum Reserves

| Field | Detail |
|---|---|
| **Target entity** | `strategic_reserves` |
| **Required fields** | location_name, operator, state, capacity_mmt, latitude, longitude |
| **Source** | ISPRL official website; MoPNG reports; research report §6 |
| **Source URL** | isprl.gov.in |
| **Source organization** | ISPRL (Indian Strategic Petroleum Reserves Ltd) |
| **Access method** | Manual curation from public ISPRL data |
| **Format** | CSV (manual) |
| **Data semantics** | OBSERVED (capacity from ISPRL), UNKNOWN (current fill levels) |
| **Target DB table** | `strategic_reserves` |
| **Sufficient?** | ✅ Yes |
| **Missing fields** | `current_level_mmt` — NOT publicly disclosed in real-time |
| **Estimation allowed?** | ❌ No — use NULL for unknown fill levels |
| **Manual curation required?** | ✅ Yes |

---

## Historical Data — EIA Commodity Prices

| Field | Detail |
|---|---|
| **Target entity** | `commodity_prices` |
| **Source** | EIA (US Energy Information Administration) |
| **Source URL** | api.eia.gov (API), eia.gov/petroleum/data.php (bulk) |
| **Access method** | API (requires free key) or bulk CSV download |
| **Format** | CSV / JSON |
| **Update frequency** | Daily/weekly |
| **Historical coverage** | 1987–present (Brent), 1986–present (WTI) |
| **Data semantics** | OBSERVED |
| **Target DB table** | `commodity_prices` |
| **Registration required?** | ✅ Free API key at api.eia.gov |
| **Status** | REQUIRES_REGISTRATION for API; bulk download may be available without key |

---

## Historical Data — RBI FX Rates

| Field | Detail |
|---|---|
| **Target entity** | `fx_rates` |
| **Source** | Reserve Bank of India (RBI) |
| **Source URL** | rbi.org.in/scripts/ReferenceRateArchive.aspx; DBIE portal |
| **Access method** | Web download (CSV/Excel) from RBI reference rate archive |
| **Format** | CSV / Excel |
| **Update frequency** | Daily (business days) |
| **Historical coverage** | 2000–present |
| **Data semantics** | OBSERVED |
| **Target DB table** | `fx_rates` |
| **Registration required?** | ❌ No |
| **Status** | AVAILABLE — publicly downloadable |

---

## Historical Data — OFAC SDN List

| Field | Detail |
|---|---|
| **Target entity** | Sanctions reference (for supplier screening) |
| **Source** | OFAC (Office of Foreign Assets Control, US Treasury) |
| **Source URL** | sanctionslist.treasury.gov |
| **Access method** | Direct download (XML, CSV, JSON) |
| **Format** | XML / CSV |
| **Update frequency** | Multiple times per day |
| **Data semantics** | OBSERVED |
| **Target storage** | `data/raw/ofac/` → `data/processed/ofac/` |
| **Registration required?** | ❌ No |
| **Status** | AVAILABLE — freely downloadable |

---

## Deferred Sources — LATER STEP

### GDELT

| Field | Detail |
|---|---|
| **Status** | DEFERRED — later event-ingestion step |
| **Reason** | GDELT is a live event source, not seed data. Step 4 is data foundation only. |
| **Notes** | Access verified: gdeltproject.org, free, 15-minute updates via BigQuery or direct download. |

### ACLED

| Field | Detail |
|---|---|
| **Status** | DEFERRED — later event-ingestion step |
| **Reason** | ACLED requires account registration; weekly update cycle. Not seed data. |
| **Notes** | Access: acleddata.com, free for research, API available after registration. |

### NewsAPI / RSS

| Field | Detail |
|---|---|
| **Status** | DEFERRED — later event-ingestion step |
| **Notes** | Free tier has 24-hour delay. Not seed data. |

---

## Summary Table (Updated: Phase B Execution)

| Dataset | Target Table | Source | Plan Status | Execution Status | Records | Semantic Class |
|---|---|---|---|---|---|---|
| Countries | `countries` | ISO 3166-1 / research | CURATED | **ACQUIRED** | 15 | OBSERVED |
| Corridors | `corridors` | Architecture docs / research | CURATED | **ACQUIRED** | 6 | ASSUMED |
| Ports | `ports` | UN/LOCODE / IPA / research | CURATED | **ACQUIRED** | 20 | OBSERVED |
| Refineries | `refineries` | PPAC / research report | CURATED | **ACQUIRED** | 20 | HISTORICAL_CALIBRATED |
| Suppliers | `suppliers` | PPAC / OFAC / research | CURATED | **ACQUIRED** | 8 | HISTORICAL_CALIBRATED |
| Crude Grades | `crude_grades` | EIA / industry refs | CURATED | **ACQUIRED** | 14 | OBSERVED |
| Refinery Supply Mix | `refinery_supply_mix` | Research / PPAC partial | CURATED | **ACQUIRED** | 51 | ESTIMATED |
| Routes | `routes` | Nautical refs / research | CURATED | **ACQUIRED** | 15 | ESTIMATED |
| SPR | `strategic_reserves` | ISPRL official | CURATED | **ACQUIRED** | 3 | OBSERVED |
| Data Sources | `data_sources` | Architecture docs | CURATED | **ACQUIRED** | 10 | N/A |
| Preset Scenarios | `scenarios` | Scenario Engine doc | CURATED | **ACQUIRED** | 5 | ASSUMED |
| EIA Prices | `commodity_prices` | EIA API/bulk | REQUIRES_REGISTRATION | REQUIRES_REGISTRATION | 0 | OBSERVED |
| RBI FX | `fx_rates` | RBI DBIE | AVAILABLE | **DOCUMENTED** | 3 (sample) | OBSERVED |
| OFAC SDN | Reference data | OFAC Treasury | AVAILABLE | **ACQUIRED** | 1,674 (filtered) | OBSERVED |
| GDELT | `geopolitical_events` | gdeltproject.org | DEFERRED | DEFERRED | 0 | N/A |
| ACLED | `geopolitical_events` | acleddata.com | DEFERRED | DEFERRED | 0 | N/A |
