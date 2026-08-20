# INDRA — Pre-Step 2 Decision Record

> **Purpose:** Documents all architectural corrections applied between the adversarial architecture review and the Architecture Freeze (Step 2).
>
> **Date:** 20 August 2026
>
> **Scope:** Documentation and conceptual schema changes ONLY. No application code, API integrations, ML pipelines, or infrastructure changes.

---

## Summary of Corrections Applied

### Correction 1: First-Class Corridor Modeling

**Problem:** Corridors (Hormuz, Red Sea, Russia, Suez) were referenced throughout the API, risk engine, UI, and LLM extraction — but had no database entity. They existed only as free-form strings.

**Change:** Added `corridors` table with fields: id, code, name, description, corridor_type, affected_countries, base_risk_score, india_dependency_share, is_active, timestamps.

**Files modified:** DATABASE_SCHEMA.md, SYSTEM_ARCHITECTURE.md, API_SPEC.md, UI_UX.md, MVP_SCOPE.md

---

### Correction 2: Event → Country → Corridor → Route Relationship

**Problem:** The `geopolitical_events` table had `country_id INT` (single value) and `affected_route_ids INT[]`, but no corridor reference. LLM extraction outputs corridor names, not route IDs.

**Change:**
- Changed `country_id` → `affected_country_ids INT[]` (supports multi-country events)
- Added `affected_corridor_ids INT[]` (supports corridor-level association)
- Kept `affected_route_ids INT[]` (optional — not every event maps to specific routes)
- Documented that events may have countries and corridors without specific route mapping

**Files modified:** DATABASE_SCHEMA.md, SYSTEM_ARCHITECTURE.md, AI_PIPELINE.md

---

### Correction 3: Entity Resolution Layer

**Problem:** The LLM extraction pipeline had no documented mechanism for mapping human-readable names (e.g., "Strait of Hormuz", "Iran") to internal database IDs. The LLM cannot produce database IDs.

**Change:**
- Added `entity_aliases` table (alias → canonical_entity_type + canonical_entity_id)
- Documented the entity resolution pipeline: LLM output → exact match against aliases → RapidFuzz fuzzy match (≥85%) → internal IDs
- Documented fallback behavior for unresolved entities (log, don't insert bad FK references)
- Scoped Phase 1 at ~50–100 pre-populated aliases

**Files modified:** DATABASE_SCHEMA.md, SYSTEM_ARCHITECTURE.md, AI_PIPELINE.md, MVP_SCOPE.md

---

### Correction 4: Normalized Crude Grades

**Problem:** Crude grades were stored as free-form `TEXT[]` arrays on suppliers and refineries. No controlled vocabulary existed, making compatibility matching brittle (e.g., "Arab light" vs "Arab Light").

**Change:**
- Added `crude_grades` table (id, name, api_gravity, sulfur_content_pct, category, origin_country_id)
- Updated suppliers, refineries, and procurement_options to reference crude_grades by FK
- Scoped Phase 1 at ~10–15 grades relevant to India's import basket

**Files modified:** DATABASE_SCHEMA.md, OPTIMIZATION.md, MVP_SCOPE.md

---

### Correction 5: Refinery Supply Mix

**Problem:** No data structure captured which crude grades a refinery can process, at what share, or with what compatibility score. The scenario engine and optimizer had no data for refinery-level impact calculation.

**Change:**
- Added `refinery_supply_mix` table (refinery_id, crude_grade_id, compatibility, compatibility_score, current_share_pct, max_share_pct, source_type, notes)
- Documented that unknown values must be marked as source_type = 'UNKNOWN' or 'ESTIMATED', not invented
- Updated scenario engine to reference this table for refinery exposure calculation

**Files modified:** DATABASE_SCHEMA.md, OPTIMIZATION.md, SCENARIO_ENGINE.md, MVP_SCOPE.md

---

### Correction 6: Price + FX Asynchronous Architecture

**Problem:** The `price_history` table used a PostgreSQL GENERATED column (`price_inr = price_usd × usd_inr_rate`) that assumed both values arrive in the same row simultaneously. EIA and RBI pollers operate independently and at different frequencies.

**Change:**
- Replaced `crude_prices` and `price_history` tables with separate `commodity_prices` and `fx_rates` tables
- Documented the "nearest-valid-prior FX rate" alignment rule for INR derivation
- INR prices are now computed at query time, not stored as generated columns
- Added source_timestamp and observed_at to both tables for provenance

**Files modified:** DATABASE_SCHEMA.md, DATA_SOURCES.md, SYSTEM_ARCHITECTURE.md

---

### Correction 7: Risk Scale Standardization

**Problem:** Research reports used conflicting risk scales (0.0–1.0 decimal vs 0–100 integer). Documentation mixed both scales inconsistently, creating implementation ambiguity.

**Change:**
- FROZEN: Internal storage and computation = 0.0–1.0
- FROZEN: Display and API responses = 0–100
- FROZEN: Conversion = `display_score = internal_score × 100`
- Updated all risk classification tables to use 0.0–1.0 thresholds
- Updated all example JSON to show correct scale per context
- Resolved weight conflict: INDRA Master Report weights as default, configuration-driven

**Files modified:** DATABASE_SCHEMA.md, SYSTEM_ARCHITECTURE.md, API_SPEC.md, ML_MODEL.md, UI_UX.md

---

### Correction 8: Provenance / Evidence Architecture

**Problem:** No formal mechanism existed for tracing how a recommendation was derived. The evidence chain (source → event → risk → scenario → recommendation) was described in prose but had no database support.

**Change:**
- Added `evidence_records` table (evidence_type, source_url, source_name, timestamp, related_entity_type, related_entity_id, model_or_method, input_summary, output_summary, data_semantic, confidence)
- Added `evidence_links` table (parent_evidence_id, child_evidence_id, relationship) for chaining evidence
- Documented evidence creation at each pipeline step (SOURCE, LLM_EXTRACTION, ENTITY_RESOLUTION, RISK_CALCULATION, SCENARIO_COMPUTATION, OPTIMIZATION, RECOMMENDATION)
- Updated UI spec to reference provenance chain for evidence drawer

**Files modified:** DATABASE_SCHEMA.md, SYSTEM_ARCHITECTURE.md, AI_PIPELINE.md, SCENARIO_ENGINE.md, OPTIMIZATION.md, UI_UX.md, MVP_SCOPE.md

---

### Correction 9: Data Semantic Classification

**Problem:** The previous classification (LIVE, RECENT, HISTORICAL, DERIVED, SIMULATED) didn't distinguish between observed data, calibrated parameters, and configuration assumptions.

**Change:**
- Replaced with: OBSERVED, DERIVED, HISTORICAL_CALIBRATED, ASSUMED, SIMULATED
- Every scenario parameter now carries a data_semantic tag
- Updated all documentation to use the new classification consistently
- Updated UI badge colors and definitions

**Files modified:** DATABASE_SCHEMA.md, SYSTEM_ARCHITECTURE.md, DATA_SOURCES.md, SCENARIO_ENGINE.md, UI_UX.md, MVP_SCOPE.md, SOLUTION_OVERVIEW.md, README.md

---

### Correction 10: MVP API Scope Reduction

**Problem:** The original API spec defined ~30 endpoints. For a single developer with 4 days, this is excessive.

**Change:**
- Reduced to ~12 MVP endpoint groups
- Prioritized endpoints needed for the demo flow only
- Documented deferred endpoints with reasons
- Marked all endpoints as "PLANNED — TO BE FROZEN IN STEP 2"

**Files modified:** API_SPEC.md

---

### Correction 11: GDP Impact Removal

**Problem:** `scenario_results.gdp_impact_estimate_usd_bn` requires macroeconomic modeling beyond this system's scope. Any number produced would be challenged by judges.

**Change:**
- Removed `gdp_impact_estimate_usd_bn` from scenario_results table
- Removed from API response shapes
- Replaced `recommendations` JSONB with structured `spr_bridge` and `affected_refineries` JSONB
- GDP impact noted as explicitly removed with rationale

**Files modified:** DATABASE_SCHEMA.md, SCENARIO_ENGINE.md, API_SPEC.md

---

### Correction 12: Generated days_coverage Removal

**Problem:** `strategic_reserves.days_coverage` was a GENERATED column using hardcoded daily consumption (0.56 MMT/day). This constant cannot vary by scenario or be updated from configuration.

**Change:**
- Removed the GENERATED column
- Documented that days_coverage is computed at the application/query layer: `current_level_mmt / india_daily_consumption_mmt`
- The daily consumption value comes from configuration or scenario context

**Files modified:** DATABASE_SCHEMA.md

---

## All Files Modified

| # | File | Changes Applied |
|---|---|---|
| 1 | `README.md` | Data semantic policy, architecture diagram (entity resolution, corridors, provenance), hackathon reference cleanup |
| 2 | `docs/01-product/SOLUTION_OVERVIEW.md` | Success criteria updated to data semantic categories |
| 3 | `docs/01-product/MVP_SCOPE.md` | M2 corridors, M7 provenance, M13 seed data scope, M15 entity resolution, M16 data semantic labels, X5 clarification |
| 4 | `docs/02-architecture/SYSTEM_ARCHITECTURE.md` | Full rewrite: corridors, entity resolution layer, provenance architecture, risk scale, price/FX separation, data semantic classification, failure boundaries, httpx standardization |
| 5 | `docs/03-frontend/UI_UX.md` | Risk display 0–100, data semantic badges (OBSERVED/DERIVED/HISTORICAL_CALIBRATED/ASSUMED/SIMULATED), evidence panel provenance |
| 6 | `docs/04-backend/API_SPEC.md` | Reduced to ~12 MVP endpoint groups, corridor endpoints, evidence endpoint, risk display scale, GDP impact removed |
| 7 | `docs/05-database/DATABASE_SCHEMA.md` | Full rewrite: corridors table, crude_grades table, refinery_supply_mix table, entity_aliases table, evidence_records/evidence_links tables, commodity_prices/fx_rates separation, risk scale 0.0–1.0, GDP impact removed, days_coverage GENERATED removed |
| 8 | `docs/06-data/DATA_SOURCES.md` | Data semantic classification, price/FX async architecture |
| 9 | `docs/07-ai-ml/AI_PIPELINE.md` | Entity resolution layer, provenance tracking, LLM retry/timeout/fallback, severity normalization |
| 10 | `docs/07-ai-ml/ML_MODEL.md` | Risk scale frozen, weight conflict resolved (INDRA Master weights as default), all examples in 0.0–1.0 |
| 11 | `docs/08-engines/SCENARIO_ENGINE.md` | Data semantic tags on assumptions, refinery_supply_mix reference, provenance, GDP impact removed |
| 12 | `docs/08-engines/OPTIMIZATION.md` | crude_grades and refinery_supply_mix references, provenance tracking |

## File Created

| # | File | Purpose |
|---|---|---|
| 1 | `docs/02-architecture/PRE_STEP2_DECISIONS.md` | This document |

---

## Unresolved Decisions for Step 2

These decisions were identified during the correction process and must be resolved during the Architecture Freeze (Step 2).

### ~~U-1: NetworkX vs SQL Joins for Supply Graph~~ — RESOLVED

**Decision:** NetworkX is confirmed for Phase 1 with precisely defined responsibilities:
- Graph traversal: identify affected refineries, disrupted routes, alternative paths
- Reachability queries: can supplier X reach refinery Y without passing through corridor Z?

SQL joins remain insufficient for these traversal queries. NetworkX is built in-memory from PostgreSQL at runtime. PostgreSQL remains the persistent source of truth.

See `SYSTEM_ARCHITECTURE.md §5a` and `SCENARIO_ENGINE.md — NetworkX / PostgreSQL / Arithmetic Boundary`.

---

### U-2: Redis in Phase 1

**Question:** Should Redis be included in Phase 1 docker-compose?

**Context:** At demo data volumes (~hundreds of events, 20 refineries), PostgreSQL queries will be fast. Redis adds deployment complexity with no measurable benefit.

**Recommendation from review:** Remove Redis from Phase 1.

**Decision needed:** Include or exclude Redis from Phase 1 docker-compose.

---

### U-3: ACLED Availability

**Question:** Will ACLED API access be approved in time?

**Context:** ACLED requires registration approval which can take days. If not approved by Day 2, the system must function without it (GDELT + RSS + OFAC provide sufficient coverage).

**Decision needed:** Treat ACLED as best-effort. Verify on Day 1.

---

### U-4: RBI API Verification

**Question:** Does the RBI statistical API actually work reliably?

**Context:** RBI's API documentation is sparse. The reference rate page may require scraping rather than clean API calls.

**Decision needed:** Verify RBI API on Day 1. Fallback: hardcoded recent USD/INR rate labeled HISTORICAL_CALIBRATED.

---

### U-5: Compatibility Threshold

**Question:** What `compatibility_score` threshold means "incompatible" for the optimizer?

**Context:** The `refinery_supply_mix` table stores compatibility as HIGH/MEDIUM/LOW/NONE with a numeric score (0.0–1.0). The LP optimizer needs a binary include/exclude decision at some threshold.

**Recommendation:** Use 0.5 as default threshold (MEDIUM or above = include). Make configurable.

**Decision needed:** Freeze the default threshold during Step 2.

---

### U-6: Scenario Configuration Source

**Question:** Should hardcoded scenario parameters (hormuz_share, freight_multiplier, price_impact) come from a config file, database table, or environment variables?

**Context:** These values must be changeable without code changes per the development rules. A `scenario_assumptions` config file or database table would work.

**Decision needed:** Choose the configuration mechanism during Step 2.

---

### U-7: Frontend CSS Framework

**Question:** Vanilla CSS or another approach?

**Context:** User's system rules specify Vanilla CSS unless explicitly requested otherwise. This is viable but slower for building a polished UI in 4 days.

**Decision needed:** Confirm with user during Step 2.

---

### U-8: Event Confidence Threshold

**Question:** Should the default LLM extraction confidence threshold (currently 0.6) be adjusted?

**Context:** The threshold determines which extracted events enter the risk calculation. Too high = miss real events. Too low = noise.

**Decision needed:** Finalize during LLM benchmarking (Step 2 or later).

---

## No New Blockers Discovered

No additional blockers were discovered during this correction step that were not already documented in the Architecture Review.

---

## Confirmation

- ✅ No datasets were downloaded
- ✅ No APIs were connected
- ✅ No feature code was written
- ✅ No ML models were trained
- ✅ No production infrastructure was added
- ✅ No Docker services were started
- ✅ No database migrations were created
- ✅ Only documentation and conceptual schema files were modified
