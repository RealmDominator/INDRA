# INDRA -- Data Acquisition Report

> **Step 4, Phase B -- Data Acquisition + Normalization + Validation**
>
> **Date:** 21 August 2026
>
> **Status:** COMPLETE

---

## 1. Datasets Actually Acquired

| Dataset | Target Table | Source | Records | File | Status |
|---|---|---|---|---|---|
| Countries | `countries` | ISO 3166-1 / PPAC / research | 15 | `data/seed/countries.csv` | ACQUIRED |
| Corridors | `corridors` | Architecture docs / PPAC | 6 | `data/seed/corridors.csv` | ACQUIRED |
| Crude Grades | `crude_grades` | EIA / industry refs | 14 | `data/seed/crude_grades.csv` | ACQUIRED |
| Ports | `ports` | UN/LOCODE / IPA | 20 | `data/seed/ports.csv` | ACQUIRED |
| Refineries | `refineries` | PPAC Annual Report | 20 | `data/seed/refineries.csv` | ACQUIRED |
| Suppliers | `suppliers` | PPAC / OFAC / research | 8 | `data/seed/suppliers.csv` | ACQUIRED |
| Refinery Supply Mix | `refinery_supply_mix` | Research / PPAC partial | 51 | `data/seed/refinery_supply_mix.csv` | ACQUIRED |
| Routes | `routes` | Sea-distances / industry refs | 15 | `data/seed/routes.csv` | ACQUIRED |
| Strategic Reserves | `strategic_reserves` | ISPRL official | 3 | `data/seed/spr.csv` | ACQUIRED |
| Data Sources | `data_sources` | Architecture docs | 10 | `data/seed/data_sources.csv` | ACQUIRED |
| Preset Scenarios | `scenarios` | Scenario Engine doc | 5 | `data/seed/scenarios.csv` | ACQUIRED |
| OFAC SDN (raw) | Reference | OFAC Treasury | ~12,500+ | `data/raw/ofac/sdn.csv` | ACQUIRED |
| OFAC SDN (processed) | Reference | OFAC (filtered) | 1,674 | `data/processed/ofac/sanctions_entities.csv` | ACQUIRED |
| RBI FX rates (sample) | `fx_rates` | RBI | 3 | `data/processed/rbi/fx_rates.csv` | DOCUMENTED |

**Total seed records:** 167
**Total historical/reference records:** 1,677

---

## 2. Source URLs

| Source | URL | Status |
|---|---|---|
| ISO 3166-1 | iso.org/iso-3166-country-codes.html | Reference standard |
| UN/LOCODE | unece.org/trade/cefact/unlocode-code-list-country-and-territory | Reference standard |
| PPAC | ppac.gov.in | Public reports (manual curation) |
| ISPRL | isprl.gov.in | Public data |
| EIA | api.eia.gov | REQUIRES_REGISTRATION |
| RBI | rbi.org.in/scripts/ReferenceRateArchive.aspx | DOCUMENTED (no bulk CSV API) |
| OFAC SDN | treasury.gov/ofac/downloads/sdn.csv | Downloaded successfully |
| Sea-distances | sea-distances.org | Public nautical reference |

---

## 3. Acquisition Timestamps

All seed datasets were curated on 21 August 2026.

OFAC SDN list was downloaded at the time of acquisition script execution.

---

## 4. File Formats

| File | Format | Encoding | Size |
|---|---|---|---|
| `data/seed/*.csv` (11 files) | CSV | UTF-8 | 1.2 KB -- 3.6 KB each |
| `data/raw/ofac/sdn.csv` | CSV | UTF-8 | 5,647,099 bytes (5.4 MB) |
| `data/processed/ofac/sanctions_entities.csv` | CSV | UTF-8 | 445,068 bytes (435 KB) |
| `data/processed/rbi/fx_rates.csv` | CSV | UTF-8 | 217 bytes |
| `data/metadata/data_manifest.json` | JSON | UTF-8 | 13,925 bytes |
| `data/metadata/historical_acquisition.json` | JSON | UTF-8 | 1,162 bytes |
| `db/schema.sql` | SQL | UTF-8 | 16,641 bytes |
| `db/seed.sql` | SQL | UTF-8 | Generated from CSVs |

---

## 5. Record Counts

| Dataset | Records |
|---|---|
| countries | 15 |
| corridors | 6 |
| crude_grades | 14 |
| ports | 20 |
| refineries | 20 |
| suppliers | 8 |
| refinery_supply_mix | 51 |
| routes | 15 |
| strategic_reserves | 3 |
| data_sources | 10 |
| scenarios | 5 |
| **Seed total** | **167** |
| OFAC energy entities | 1,674 |
| RBI FX sample | 3 |
| **Historical total** | **1,677** |

---

## 6. Fields Available vs Missing

### Fields Fully Available

| Entity | Available Fields |
|---|---|
| countries | name, iso3, region, is_hormuz_dependent, is_red_sea_dependent |
| corridors | code, name, description, corridor_type, affected_countries, base_risk_score, india_dependency_share |
| crude_grades | name, api_gravity, sulfur_content_pct, category, origin_country_id |
| ports | name, un_locode, country_id, is_indian, latitude, longitude |
| refineries | name, owner, state, capacity_mmtpa, latitude, longitude |
| suppliers | name, country_id, crude_grade_ids, is_sanctioned, sanction_source |
| routes | name, origin_port_id, dest_port_id, corridor_ids, distance_nm, avg_transit_days |
| strategic_reserves | location_name, operator, state, capacity_mmt, latitude, longitude |

### Fields Marked NULL / UNKNOWN

| Entity | Field | Reason |
|---|---|---|
| countries | base_risk_score | Deferred to risk engine (Step 5+) |
| ports | annual_crude_throughput_mmtpa | Not available for all ports |
| refineries | throughput_current_mmtpa | Not publicly available; not fabricated |
| refineries | port_id | Some inland refineries have no direct port (set NULL) |
| suppliers | annual_supply_capacity_mmtpa | Varies by contract; not fabricated |
| refinery_supply_mix | current_share_pct | Not available from public sources |
| refinery_supply_mix | max_share_pct | Not available from public sources |
| routes | base_freight_rate_per_mt | Volatile; not seeded with static values |
| strategic_reserves | current_level_mmt | Not publicly disclosed in real-time |

---

## 7. Values Marked ESTIMATED

| Entity | Field | Estimation Methodology |
|---|---|---|
| corridors | base_risk_score | HISTORICAL_CALIBRATED from research reports and historical disruption data |
| corridors | india_dependency_share | HISTORICAL_CALIBRATED from PPAC import-by-source FY2024-25 data |
| refinery_supply_mix | compatibility | ESTIMATED from refinery crude-slate category matching (complex/heavy/light) |
| refinery_supply_mix | compatibility_score | ESTIMATED numeric equivalent of compatibility category |
| routes | avg_transit_days | ESTIMATED as `distance_nm / (14 knots * 24 hours/day)` |
| routes | current_risk_score | HISTORICAL_CALIBRATED from corridor base risk |

---

## 8. Transformations Applied

| Transformation | Description |
|---|---|
| Transit time estimation | `avg_transit_days = distance_nm / (14 * 24)` -- standard VLCC cruising speed |
| OFAC energy filtering | SDN list filtered for energy-relevant keywords (oil, petroleum, tanker, etc.) |
| Compatibility scoring | Refinery crude-slate category mapped to HIGH/MEDIUM/LOW compatibility |
| Corridor dependency | India import shares derived from PPAC country-of-origin data |

---

## 9. Validation Results

### Seed Data Validation

```
[PASS] VALIDATION PASSED -- all seed datasets are valid
   Total datasets: 11
   Total rows: 167
```

Validated: required fields, duplicate records, ISO3 codes, coordinates, FK references, enum values, refinery-grade uniqueness.

### Historical Data Validation

```
[PASS] VALIDATION PASSED -- all historical datasets are valid
   Total datasets validated: 3
   Total rows: 1677
```

One warning: EIA commodity prices not yet acquired (REQUIRES_REGISTRATION).

---

## 10. Cross-Dataset Integrity

All cross-dataset references validated:

| Relationship | Status |
|---|---|
| suppliers.country_id -> countries | VALID |
| ports.country_id -> countries | VALID |
| refineries.port_id -> ports | VALID (NULL for inland refineries) |
| routes.origin_port_id -> ports | VALID |
| routes.dest_port_id -> ports | VALID |
| routes.corridor_ids -> corridors | VALID |
| crude_grades.origin_country_id -> countries | VALID |
| suppliers.crude_grade_ids -> crude_grades | VALID |
| refinery_supply_mix.refinery_id -> refineries | VALID |
| refinery_supply_mix.crude_grade_id -> crude_grades | VALID |

No unresolved references in final curated seed datasets.

---

## 11. Source Limitations

| Limitation | Impact |
|---|---|
| PPAC data is from annual reports, not real-time API | Refinery capacities reflect FY2024-25 |
| ISPRL fill levels not publicly disclosed | current_level_mmt = NULL for all SPR sites |
| Refinery crude compatibility is estimated, not verified | All refinery_supply_mix source_type = ESTIMATED |
| Transit times assume standard VLCC speed (14 knots) | Actual transit varies by vessel, weather, routing |
| Freight rates are volatile and not seeded | base_freight_rate_per_mt = NULL |
| EIA API requires free registration | Historical commodity prices not yet acquired |
| RBI has no simple bulk CSV download API | Only sample format file created |

---

## 12. Deferred Datasets

| Dataset | Reason | When |
|---|---|---|
| GDELT events | Live event source, not seed data | Event-ingestion step |
| ACLED events | Live event source, requires registration | Event-ingestion step |
| NewsAPI | Live event source, 24-hour delay on free tier | Event-ingestion step |
| EIA commodity prices | Requires free API key registration | After registration |
| RBI bulk FX rates | Requires manual DBIE portal download | Manual download step |

---

## 13. Access / Registration Requirements

| Source | Requirement | Cost | Status |
|---|---|---|---|
| EIA API | Free API key at api.eia.gov | Free | REQUIRES_REGISTRATION |
| ACLED | Academic registration | Free | DEFERRED |
| NewsAPI | Developer key | Free tier | DEFERRED |
| GDELT | None (open access) | Free | DEFERRED |
| RBI | None (public portal) | Free | DOCUMENTED |
| OFAC | None (public download) | Free | ACQUIRED |

---

## 14. Large File / Git Handling

| File | Size | Git Policy |
|---|---|---|
| `data/seed/*.csv` (11 files) | < 4 KB each | Committed (small seed data) |
| `data/raw/ofac/sdn.csv` | 5.4 MB | **Not committed** (in .gitignore via `data/raw/*`) |
| `data/processed/ofac/sanctions_entities.csv` | 435 KB | **Not committed** (in .gitignore via `data/processed/*`) |
| `data/processed/rbi/fx_rates.csv` | 217 bytes | **Not committed** (in .gitignore via `data/processed/*`) |
| `data/metadata/*.json` | < 14 KB each | Committed |

Reproduction: Run `python scripts/data/acquire_historical_data.py` to re-download raw/processed data.

---

## 15. Files Created in Step 4

### Seed Datasets (data/seed/)

- `countries.csv` (15 rows)
- `corridors.csv` (6 rows)
- `crude_grades.csv` (14 rows)
- `ports.csv` (20 rows)
- `refineries.csv` (20 rows)
- `suppliers.csv` (8 rows)
- `refinery_supply_mix.csv` (51 rows)
- `routes.csv` (15 rows)
- `spr.csv` (3 rows)
- `data_sources.csv` (10 rows)
- `scenarios.csv` (5 rows)

### Historical / Reference Data

- `data/raw/ofac/sdn.csv` (raw OFAC SDN list)
- `data/processed/ofac/sanctions_entities.csv` (energy-relevant extract)
- `data/processed/rbi/fx_rates.csv` (sample format file)

### Database Files

- `db/schema.sql` (reconciled with frozen DATABASE_SCHEMA.md)
- `db/seed.sql` (generated INSERT statements from seed CSVs)

### Provenance

- `data/metadata/data_manifest.json` (17 dataset entries)
- `data/metadata/historical_acquisition.json` (acquisition log)

### Scripts

- `scripts/data/validate_seed_data.py`
- `scripts/data/validate_historical_data.py`
- `scripts/data/load_seed_data.py`
- `scripts/data/acquire_historical_data.py`

### Documentation

- `docs/06-data/DATA_ACQUISITION_PLAN.md` (Phase A)
- `docs/06-data/DATA_ACQUISITION_REPORT.md` (this file)

---

## 16. Confirmation

- [x] No Step 5 implementation was started
- [x] No FastAPI endpoints, event ingestion, LLM integration, risk engine, scenario engine, optimizer, or frontend dashboard was added
- [x] No fabricated values exist in any dataset
- [x] All ESTIMATED values are explicitly labeled with methodology
- [x] All UNKNOWN/NULL values are documented
- [x] GDELT and ACLED are documented as DEFERRED only
