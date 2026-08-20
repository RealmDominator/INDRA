# INDRA — Architecture Review Report

> **Reviewers:** Principal Software Architect, Backend Engineer, Data Engineer, ML Engineer, AI/LLM Engineer, Database Engineer, Frontend Engineer, Optimization/OR Engineer, Security Engineer, Hackathon Judge, Skeptical Energy-Domain Reviewer, Reliability/Failure-Engineering Reviewer
>
> **Review Date:** 20 August 2026
>
> **Reviewed Documents:** All Step 0 documentation, both research reports, schema.sql, docker-compose.yml, .env.example
>
> **Status:** REVIEW ONLY — no code written, no architecture modified

---

## 1. Executive Verdict

The INDRA Step 0 foundation is **substantially sound** and unusually disciplined for a hackathon project. The data-honesty policy, LLM boundary enforcement, deterministic-computation design, evidence-chain requirement, and explicit DO NOT BUILD list are all correct and well-aligned with the research reports.

However, the review identifies **3 critical blockers**, **7 high-risk architectural issues**, and **12 medium-risk items** that must be addressed before implementation begins. The most important finding is a **schema-level gap**: corridors and chokepoints — the primary entities in the risk dashboard — have no database table, no API entity model, and no seed data definition. The entire risk visualization is structurally disconnected from the data model.

**Overall assessment: PROCEED WITH TARGETED FIXES — do not redesign.**

---

## 2. Current Architecture Reconstruction

```
EXTERNAL DATA (GDELT, ACLED, OFAC, EIA, RBI, RSS, PPAC/ISPRL seed)
        ↓
INGESTION (APScheduler pollers + static seed loader)
        ↓
PROCESSING (Pydantic validation + RapidFuzz entity matching)
        ↓
LLM EXTRACTION (abstracted provider → structured JSON)
        ↓
POST-LLM VALIDATION (enum/range/schema checks)
        ↓
DATABASE (PostgreSQL single instance — 14 tables)
        ↓
RISK ENGINE (weighted deterministic formula)
        ↓
SUPPLY GRAPH (NetworkX — suppliers→routes→ports→refineries)
        ↓
SCENARIO ENGINE (parametric disruption propagation)
        ↓
PROCUREMENT ENGINE (deterministic ranking, optional LP via scipy/PuLP)
        ↓
SPR ENGINE (deterministic drawdown arithmetic)
        ↓
RECOMMENDATION BUILDER (structured output + optional LLM explanation)
        ↓
FASTAPI REST API (~30 endpoints across 9 resource groups)
        ↓
REACT DASHBOARD (Leaflet map + risk cards + scenario sim + procurement table + evidence drawer)
```

**Key design constraints preserved from research:**
- LLM restricted to extraction + explanation only
- All quantitative outputs are deterministic
- Data classification tags (LIVE/RECENT/HISTORICAL/DERIVED/SIMULATED) on every output
- Evidence trail from source article to recommendation
- No Kafka/Neo4j/Kubernetes/multi-DB
- Single-developer hackathon constraint acknowledged

---

## 3. Critical Blockers

> [!CAUTION]
> These issues will cause implementation failure if not resolved before coding begins.

### BLOCKER-1: No `corridors` or `chokepoints` table in schema

**Severity:** CRITICAL
**Source:** Database Engineer, Backend Engineer

The entire product revolves around corridor risk scores (Hormuz, Red Sea, Suez, Russia). The risk dashboard (UI_UX.md Page 1) displays corridor risk cards. The API spec defines `/risk/corridors` and `/risk/corridors/{corridor_id}`. The LLM extraction schema outputs `affected_corridors`. The scenario engine is parameterized by corridor.

Yet **the database schema has no `corridors` table and no `chokepoints` table.** The `risk_scores` table uses a polymorphic `entity_type` + `entity_id` pattern, but there is no entity table for corridors to reference. The `geopolitical_events` table stores `affected_route_ids` (integer array of route IDs) but not `affected_corridor_ids`.

**Impact:**
- Risk scores for corridors cannot be stored with proper foreign keys
- The API cannot serve `/risk/corridors/{corridor_id}` without knowing what corridor IDs exist
- The LLM extraction output (`affected_corridors: ["HORMUZ"]`) cannot be mapped to database entities
- Corridor-level risk aggregation has no data source

**Recommendation:** CHANGE — Add a `corridors` table (id, name, code, description, affected_countries, geometry) and optionally a `chokepoints` table. Alternatively, corridors could be modeled as a view/enum with a small reference table. This must be resolved before schema deployment.

---

### BLOCKER-2: `geopolitical_events.affected_route_ids` vs LLM output `affected_corridors`

**Severity:** CRITICAL
**Source:** Data Engineer, AI/LLM Engineer

The LLM extraction prompt (AI_PIPELINE.md) asks the model to output `affected_chokepoints: [HORMUZ | RED_SEA | SUEZ | MALACCA | NONE]`. The API response shape (API_SPEC.md) shows `affected_corridors: ["HORMUZ"]`. But the database column is `affected_route_ids INT[]` — an array of route table foreign keys.

These are fundamentally different data types:
- LLM outputs corridor/chokepoint **names** (strings)
- Database stores route **IDs** (integers)
- A corridor contains many routes; a route passes through zero or more corridors

There is no documented mapping layer between corridor names and route IDs. The LLM cannot output route IDs (it doesn't know them). The events table cannot store corridor strings.

**Impact:** Data flow from LLM → database → risk engine is broken at the schema level.

**Recommendation:** CHANGE — The events table should store `affected_corridors TEXT[]` (or FK to corridors table) as the primary LLM output field. The mapping from corridor → affected routes should be a lookup in the corridors/routes relationship, not something the LLM is expected to produce.

---

### BLOCKER-3: `price_history.price_inr_per_barrel` GENERATED column depends on nullable `usd_inr_rate`

**Severity:** CRITICAL (deployment-level)
**Source:** Database Engineer

In schema.sql line 139–140:
```sql
price_inr_per_barrel DECIMAL(12,4)
    GENERATED ALWAYS AS (price_usd_per_barrel * usd_inr_rate) STORED
```

If either `price_usd_per_barrel` or `usd_inr_rate` is NULL (which is allowed by the schema since neither column has a NOT NULL constraint), the generated column will be NULL silently. More critically, FX data comes from RBI (daily poll) while price data comes from EIA (separate poll). These will rarely arrive at the same timestamp. This table assumes synchronized insertion of both values in the same row, but the ingestion architecture polls them independently.

**Impact:** The `price_history` table cannot be populated by independent EIA and RBI pollers without a join/merge step that is not documented anywhere.

**Recommendation:** CHANGE — Either (a) separate price and FX into distinct tables and compute INR prices at query time, or (b) add a documented merge step that combines EIA prices with RBI FX rates before insertion.

---

## 4. High-Risk Architectural Decisions

### HIGH-1: ~30 API endpoints for one developer in 4 days

**Severity:** HIGH
**Source:** Principal Architect, Backend Engineer

The API spec defines 30+ endpoints across 9 resource groups. For a single developer with 4 days to build the entire stack (backend + frontend + data + engines), this is excessive. Most hackathon demos can be driven by 8–12 endpoints.

**Recommendation:** CHANGE — Prioritize endpoints needed for the demo flow only. The following ~12 endpoints cover the entire demo script:

| Priority | Endpoint | Demo Use |
|---|---|---|
| 1 | `GET /health` | Smoke test |
| 2 | `GET /risk/corridors` | Landing page risk cards |
| 3 | `GET /events` | Event feed |
| 4 | `GET /events/{id}` | Evidence drill-down |
| 5 | `GET /refineries` | Map data + scenario context |
| 6 | `GET /routes` | Map routes |
| 7 | `GET /reserves` | SPR display |
| 8 | `GET /prices/current` | Quick stats |
| 9 | `POST /scenarios/run` | Scenario simulation |
| 10 | `GET /scenarios/presets` | Preset scenario list |
| 11 | `GET /recommendations/{scenario_id}` | Procurement results |
| 12 | `GET /risk/evidence/{type}/{id}` | Evidence chain |

Defer `/suppliers`, `/suppliers/{id}`, `/routes/{id}`, `/refineries/{id}/exposure`, `/prices/history`, `/prices/fx`, `/reserves/{location_id}`, `/reserves/scenario/{id}`, `/recommendations/{id}/explain`, `/events/extract`, `/events/feed`, `/status/data-sources` to post-MVP.

---

### HIGH-2: `strategic_reserves.days_coverage` hardcodes daily consumption

**Severity:** HIGH
**Source:** Database Engineer, Scenario Engine Reviewer

```sql
days_coverage DECIMAL(8,2)
    GENERATED ALWAYS AS (current_level_mmt / 0.56) STORED
```

The magic number `0.56` (India's daily import in MMT) is hardcoded in the schema DDL. If the PPAC data is updated or if a scenario changes consumption assumptions, this column cannot reflect it. Generated columns cannot reference other tables or runtime parameters.

**Recommendation:** CHANGE — Remove the GENERATED column. Compute `days_coverage` at the application layer where it can use the current daily consumption rate from the scenario context or a configuration table.

---

### HIGH-3: No `crude_grades` reference table

**Severity:** HIGH
**Source:** Database Engineer, Optimization Engineer

Crude grades appear in:
- `suppliers.crude_grades TEXT[]` — what the supplier offers
- `refineries.compatible_crude_grades TEXT[]` — what the refinery accepts
- `procurement_options.crude_grade VARCHAR(100)` — what's being recommended

These are all free-text strings. There is no reference table ensuring "Arab Light" is spelled consistently everywhere. The compatibility matrix (the product's strongest differentiator) depends on matching these strings.

**Recommendation:** CHANGE — Add a `crude_grades` reference table (id, name, api_gravity, sulfur_content, category) and use foreign keys or at least a consistent enum. Without this, a typo ("Arab light" vs "Arab Light") silently breaks compatibility matching.

---

### HIGH-4: NetworkX graph role is underspecified

**Severity:** HIGH
**Source:** Principal Architect, Data Engineer

The architecture lists NetworkX as MUST for "supply graph," but the scenario engine documentation (SCENARIO_ENGINE.md) describes purely arithmetic propagation logic that doesn't require graph traversal. The scenario engine's `calculate_supply_impact` function uses hardcoded share percentages (`hormuz_share = 0.42`) rather than traversing a graph.

The question is: **when does NetworkX actually get used?**

Possible legitimate uses:
1. Finding alternative routes when a corridor is disrupted
2. Computing which refineries are reachable from which suppliers via non-disrupted routes
3. Propagating disruption through the supplier→route→port→refinery chain

But the current scenario engine pseudo-code doesn't do any of this — it uses fixed percentages.

**Recommendation:** TEST FIRST — Before implementation, determine whether the scenario engine actually needs graph traversal or whether the fixed-share arithmetic is sufficient for the demo. If NetworkX is used, document exactly which graph operations are needed. If it's only used for one or two lookups, simple SQL joins may be sufficient and eliminate a dependency.

---

### HIGH-5: Risk score scale conflict remains unresolved

**Severity:** HIGH
**Source:** ML Engineer, Frontend Engineer

Both research reports use different risk scales:
- PETRAS: 0.0–1.0 decimal
- INDRA Master: 0–100 integer

The schema uses `DECIMAL(5,3)` which can store either, but the UI spec shows 0–100 scores, the API response examples show 0–100, and the risk classification table uses 0–100 ranges. Yet the LLM extraction asks for severity on 0.0–1.0.

If not resolved, implementing agents will mix scales causing bugs where a score of 0.78 is displayed as "0.78" instead of "78" or vice versa.

**Recommendation:** CHANGE — Freeze the decision NOW: **use 0–100 for display-facing risk scores and 0.0–1.0 for internal component weights and LLM-extracted severity.** Document the conversion rule: `display_score = internal_score × 100`. This prevents implementation ambiguity.

---

### HIGH-6: Scenario engine has no refinery-supplier mapping data

**Severity:** HIGH
**Source:** Scenario Engine Reviewer, Data Engineer

The scenario propagation logic (Step 4: "Refinery Intake Reduced") requires knowing which refineries are supplied by which suppliers via which routes. But no table captures this relationship. We have:
- `refineries.port_id` → receiving port
- `routes.origin_port_id / dest_port_id` → route endpoints
- `suppliers.country_id` → supplier country

But there is no `refinery_supplier_mix` or `supply_allocation` table that says "BPCL Kochi gets 40% of its crude from Iraq via Hormuz route." Without this, the scenario engine cannot determine which refineries are affected by a Hormuz disruption except by indirect inference (port → route → chokepoint).

**Recommendation:** CHANGE — Either add a `refinery_supply_mix` join table (refinery_id, supplier_id, route_id, share_pct) as seed data, or document that the scenario engine will infer exposure from the route/port/chokepoint graph. The first approach is more defensible for the demo.

---

### HIGH-7: `events.country_id` allows only one country per event

**Severity:** HIGH
**Source:** Data Engineer, AI/LLM Engineer

The `geopolitical_events` table has `country_id INT REFERENCES countries(id)` — a single foreign key. But many geopolitical events affect multiple countries (e.g., "Iran-Saudi tensions" affects both Iran and Saudi Arabia; "Hormuz naval drills" affects all Gulf exporters). The LLM extraction schema produces `affected_countries: [list of country names]` — a list.

**Recommendation:** CHANGE — Use `affected_country_ids INT[]` (integer array) or a junction table. A single country_id field loses critical multi-country event information.

---

## 5. Medium-Risk Issues

### MED-1: ACLED API requires registration approval — not guaranteed

The DATA_SOURCES.md correctly notes that ACLED "Required — apply for API access." ACLED approval is not instant; it can take days. If the developer applies on Day 1, access may not arrive by Day 2.

**Recommendation:** DEFER — Treat ACLED as SHOULD HAVE. The system must function without it. GDELT + RSS + OFAC provide sufficient event coverage for the demo.

---

### MED-2: RBI API availability is uncertain

The documentation claims RBI has a statistical data API. In practice, RBI's API documentation is sparse and the endpoints sometimes change. The reference rate page at rbi.org.in is web-scraping territory, not a clean REST API.

**Recommendation:** TEST FIRST — Verify RBI API access on Day 1. Fallback: hardcode a recent USD/INR rate from RBI website with HISTORICAL label.

---

### MED-3: `risk_scores.entity_type` polymorphic pattern is fragile

Using a string `entity_type` + integer `entity_id` without foreign keys means no referential integrity. A risk score referencing entity_type="corridor", entity_id=999 will not fail even if corridor 999 doesn't exist.

**Recommendation:** KEEP for Phase 1 (pragmatic), but document the risk. Polymorphic FK patterns are acceptable for hackathons but should be replaced with proper table-per-type in Phase 2.

---

### MED-4: No `updated_at` timestamps on most tables

Only `suppliers` has `updated_at`. The `countries`, `ports`, `refineries`, `routes` tables have `created_at` but no `updated_at`. This makes it impossible to track when seed data was last refreshed.

**Recommendation:** CHANGE — Add `updated_at TIMESTAMP DEFAULT NOW()` to all reference tables.

---

### MED-5: `procurement_options.scenario_id` has no FK constraint

In schema.sql, `procurement_options.scenario_id INT` lacks a `REFERENCES scenarios(id)` constraint, unlike `scenario_results.scenario_id` which has it.

**Recommendation:** CHANGE — Add the FK constraint.

---

### MED-6: Demo mode / fixture data architecture is not defined

The failure boundary table mentions "demo mode" and "fixture data" multiple times, but there is no documented architecture for how demo fixtures are loaded, triggered, or labeled. A developer implementing this ad hoc will likely produce inconsistent results.

**Recommendation:** CHANGE — Add a section to SYSTEM_ARCHITECTURE.md or create a `docs/10-demo/DEMO_MODE.md` defining: (a) how demo fixtures are stored, (b) how demo mode is activated, (c) how demo data is labeled in the UI.

---

### MED-7: `crude_prices` and `price_history` overlap

Both tables store crude prices. `crude_prices` appears to be "current" prices while `price_history` is historical. But there's no documented logic for when a `crude_prices` row becomes a `price_history` row, or whether they're independently populated.

**Recommendation:** CHANGE — Merge into a single `crude_prices` table with a `is_current BOOLEAN` or simply use `price_history` for everything and query `MAX(time)` for current prices. Two overlapping tables will cause data inconsistency.

---

### MED-8: Frontend testing with Jest + React Testing Library is ambitious for hackathon

The testing strategy includes frontend component tests. For a single developer with 4 days, frontend tests are the lowest-priority testing layer.

**Recommendation:** DEFER — Skip frontend unit tests. Focus on backend unit tests (risk engine, scenario engine, procurement engine) and one E2E pipeline test. Frontend testing is Phase 2.

---

### MED-9: PostGIS extension listed as SHOULD but may not be needed

The schema mentions PostGIS for geospatial queries, but all coordinates are stored as plain DECIMAL lat/lon columns. Leaflet handles client-side rendering. Unless the backend needs geospatial queries (e.g., "find all ports within 500km of this chokepoint"), PostGIS adds installation complexity with no demo value.

**Recommendation:** REMOVE for Phase 1. Use plain lat/lon columns. PostGIS is Phase 2 if spatial queries become necessary.

---

### MED-10: `aiohttp / httpx` — pick one

The architecture lists "aiohttp / httpx" as the HTTP client. These are different libraries with different APIs. A single developer should use one.

**Recommendation:** CHANGE — Standardize on `httpx` (async-capable, simpler API, better maintained). Remove aiohttp from the tech stack.

---

### MED-11: Export/share functionality mentioned in UI workflow but never specified

UI_UX.md step 12: "User can export or share the analysis." No API endpoint, no export format, no sharing mechanism is defined.

**Recommendation:** DEFER — Remove from Phase 1 scope. Export is a nice-to-have that takes time away from the core chain.

---

### MED-12: Scenario results include `gdp_impact_estimate_usd_bn` — high fabrication risk

The `scenario_results` table includes a GDP impact estimate. Credibly estimating GDP impact from a crude oil disruption requires macroeconomic modeling that is far beyond this system's scope. A judge will immediately challenge "GDP impact: $4.2 billion" and ask for the methodology.

**Recommendation:** REMOVE — Drop `gdp_impact_estimate_usd_bn` from scenario results. Focus on supply gap, cost increase, and SPR bridge — these are directly calculable from the data. GDP impact is an economist's job, not a supply-chain tool's.

---

## 6. Low-Risk Improvements

| # | Issue | Recommendation | Classification |
|---|---|---|---|
| LOW-1 | README.md line 224–226 still references "PSB Cybersecurity, Fraud & AI Hackathon 2026" and "Problem Statement 1" which the user removed from research_report_2.md | CHANGE — Update README to match user's edit | CHANGE |
| LOW-2 | `.env.example` defaults to `openai` provider and `gpt-4o-mini` model, which partially contradicts the "no hard-coded provider" rule | KEEP — It's an example file with comments explaining the abstraction layer | KEEP |
| LOW-3 | No `.editorconfig` or formatting configuration | DEFER — Nice to have but not critical | DEFER |
| LOW-4 | Docker-compose uses PostgreSQL 16 Alpine — confirm developer has Docker Desktop installed | TEST FIRST | TEST FIRST |
| LOW-5 | `db/migrations/` directory exists but no migration tool (Alembic) is configured | KEEP — Manual DDL is fine for hackathon | KEEP |

---

## 7. Data Risks

### Per-Source Analysis

| Source | Used For | Availability Risk | Schema Change Risk | Fallback | Labeling |
|---|---|---|---|---|---|
| **GDELT** | Live geopolitical events | LOW — public, no auth | MEDIUM — GDELT has changed API formats before | Demo fixture events | LIVE |
| **RSS/News** | Live news articles for LLM extraction | LOW — public feeds | LOW — RSS is stable | Demo fixture articles | LIVE |
| **ACLED** | Conflict event data | HIGH — requires approval | LOW — stable API schema | Skip; use GDELT only | RECENT |
| **OFAC** | Sanctions list | LOW — public, no auth | LOW — XML/CSV format stable | Pre-loaded snapshot | LIVE |
| **EIA** | Crude prices (Brent, WTI) | LOW — free API key | LOW — well-documented API | Hardcoded recent prices | RECENT |
| **RBI** | USD/INR exchange rate | MEDIUM — API uncertain | HIGH — no stable API contract | Hardcoded recent rate | RECENT |
| **PPAC** | India import structure, refinery data | N/A — static seed | N/A | Already pre-loaded | HISTORICAL |
| **ISPRL** | SPR locations/capacity | N/A — static seed | N/A | Already pre-loaded | HISTORICAL |
| **NewsAPI** | Supplementary news | LOW | LOW | Skip; use RSS only | RECENT (24hr delay) |

### Data Storage Recommendations

| Data | Store Permanently? | Cache? | Classification |
|---|---|---|---|
| Extracted events | YES — in `geopolitical_events` | NO | LIVE/RECENT |
| Risk scores | YES — in `risk_scores` (time series of scores) | YES — current scores in Redis | DERIVED |
| Crude prices | YES — in `price_history` | YES — current in Redis | RECENT |
| Seed data (refineries, ports, routes) | YES — in reference tables | NO (changes rarely) | HISTORICAL |
| Scenario results | YES — in `scenario_results` | NO (computed on demand) | DERIVED |
| OFAC sanctions snapshot | YES — in supplier flags | NO | LIVE |

---

## 8. LLM Risks

### Provider Abstraction Assessment

The abstraction layer design (AI_PIPELINE.md, AI_MODEL_STRATEGY.md) is **well-structured conceptually** but needs the following additions:

| Risk | Impact | Mitigation |
|---|---|---|
| **Malformed JSON from LLM** | Event extraction fails silently | MUST add retry with re-prompt (max 2 retries), then log and skip |
| **Hallucinated entity** | "Hormuz" mapped to wrong corridor | MUST validate all entities against known entity list post-extraction |
| **Missing confidence field** | Evidence chain incomplete | Default to confidence = 0.5 with a "confidence_defaulted: true" flag |
| **LLM timeout (>10s)** | Ingestion pipeline stalls | Set timeout at 15s, skip article on timeout, log |
| **Provider rate limit** | Burst of articles hits limit | Queue articles, process sequentially with backoff |
| **Provider unavailable** | No extraction possible | Fall back to pre-parsed seed events; show "LLM unavailable" in UI |
| **Prompt injection from news article** | Malicious text manipulates extraction | Sanitize input: strip HTML, limit to first 2000 chars, don't echo raw text in prompts |

### Boundaries — CONFIRMED CORRECT

The LLM boundary table in AI_PIPELINE.md correctly restricts the LLM. **No changes recommended.** The hybrid architecture is the project's strongest design decision.

### Missing: Retry and fallback model strategy

The abstraction layer defines `extract_event()` and `generate_explanation()` but doesn't define what happens when the call fails. Should add:
- `max_retries: int = 2`
- `fallback_provider: Optional[LLMProvider]` — a cheaper/faster model that can be tried if the primary fails
- `timeout_seconds: int = 15`

**Recommendation:** CHANGE — Add retry/timeout/fallback configuration to the LLM provider interface.

---

## 9. ML Risks

### XGBoost Phase 2 Assessment

| Concern | Assessment |
|---|---|
| **Features meaningful?** | YES — ACLED event counts, sanctions changes, price volatility, country risk are all reasonable signals |
| **Target variable well-defined?** | PARTIALLY — "Did a disruption actually occur?" needs a precise definition (what counts as a disruption? supply drop of >5%? price spike of >10%?) |
| **Can historical data create labels?** | UNCERTAIN — EIA supply disruption records exist but are sparse. Labeling ACLED events as disruption=1/0 requires manual annotation or a proxy metric |
| **Data leakage risk?** | YES — using price change as both a feature and a proxy for disruption labels creates leakage. Must separate feature windows from label windows |
| **Enough data?** | MARGINAL — "hundreds to low thousands of samples" is workable for XGBoost but will have wide confidence intervals |
| **XGBoost vs logistic regression?** | XGBoost is fine. Logistic regression should be a baseline comparison |
| **SHAP appropriate?** | YES — standard and well-supported for tree models |
| **Model outputs used appropriately?** | YES (as documented) — probability output fed into risk engine, not used directly for decisions |

### Phase 1 ML Risk

The Phase 1 approach (weighted rule-based scoring) is **correct and defensible.** The research reports converge on this. No changes needed.

### What would make a judge say "this isn't credible ML"?

1. Claiming XGBoost accuracy without showing evaluation methodology
2. Using SHAP plots from a model trained on 50 samples
3. Claiming "AI-powered" when the AI is just one LLM extraction call
4. Not being able to explain what the rule-based weights represent

**Recommendation:** KEEP Phase 1 as rule-based. If time permits on Day 4, train a minimal XGBoost on whatever ACLED/EIA historical data is available. **Do not claim ML unless the evaluation is documented.**

---

## 10. Database Risks

### Schema Issues Summary

| Issue | Severity | Action |
|---|---|---|
| No `corridors` table | CRITICAL | CHANGE |
| No `chokepoints` table | MEDIUM | Can be folded into `corridors` |
| No `crude_grades` reference table | HIGH | CHANGE |
| No `refinery_supply_mix` table | HIGH | CHANGE |
| `events.country_id` single-value | HIGH | CHANGE to array |
| `events.affected_route_ids` mismatches LLM output | CRITICAL | CHANGE |
| `price_history` GENERATED column assumes synchronized data | CRITICAL | CHANGE |
| `strategic_reserves.days_coverage` hardcodes constant | HIGH | CHANGE |
| `procurement_options.scenario_id` missing FK | MEDIUM | CHANGE |
| No `updated_at` on most tables | MEDIUM | CHANGE |
| `crude_prices` / `price_history` overlap | MEDIUM | CHANGE |
| Indexes commented out | LOW | KEEP (uncomment during implementation) |

### Redis Assessment

Redis is listed as SHOULD HAVE. For a hackathon demo:
- API responses are fast enough from PostgreSQL at demo data volumes
- No rate limiting needed
- No session management needed

**Recommendation:** DEFER — Do not implement Redis in Phase 1 unless API response times are measurably slow (they won't be at 20 refineries, 50 routes, 200 events). Eliminate Redis from docker-compose to simplify deployment.

### Technology Exclusion — CONFIRMED CORRECT

The exclusion of Neo4j, MongoDB, Kafka, Elasticsearch, ClickHouse, TimescaleDB is correct. No changes.

---

## 11. Scenario Engine Risks

| Issue | Severity | Assessment |
|---|---|---|
| **Fixed share percentages** | MEDIUM | The `hormuz_share = 0.42` constant should come from the seed database (sum of supplier shares routed through Hormuz), not hardcoded. Otherwise changing seed data doesn't change scenario results |
| **No refinery-supplier mapping** | HIGH | Addressed in HIGH-6. Without this, "refinery impact" is guesswork |
| **Price impact assumptions** | MEDIUM | The $15/bbl Hormuz closure figure is an assumption. Document as ASSUMPTION with EIA historical source |
| **Freight multiplier source** | MEDIUM | 3.2x Cape vs Hormuz needs citation. Acceptable as ASSUMPTION if labeled |
| **SPR drawdown rate limit** | LOW | Physical drawdown rate is not modeled (SPR can't release all 5.33 MMT in one day). Acceptable simplification for Phase 1 |
| **Linear scaling assumption** | LOW | 50% disruption = 50% gap is a simplification. Real disruptions have non-linear effects. Acceptable for Phase 1 |
| **Inventory burn formula** | MEDIUM | `days_to_minimum = current_inventory / (normal_intake - disrupted_intake)` — but `current_inventory` is not in any table. Refineries table has throughput but not inventory |

### Key Unverifiable Numbers

A judge will challenge:
- "$15/bbl price impact for Hormuz closure" — defensible if calibrated against Gulf War II data
- "3.2x freight multiplier" — defensible if distance ratio is documented
- "42% Hormuz share" — defensible from PPAC data
- "9.5 days SPR coverage" — defensible: 5.33 / 0.56

**Recommendation:** KEEP the engine design. CHANGE the hardcoded constants to config/database-driven values. Add a `scenario_assumptions` table or config file.

---

## 12. Optimization Risks

| Issue | Severity | Assessment |
|---|---|---|
| **LP formulation is mathematically valid** | — | The objective function (minimize cost + risk penalty) and constraints (capacity, sanctions, compatibility, risk ceiling) are well-formed |
| **Missing constraint: minimum order quantity** | LOW | Real crude procurement has minimum lot sizes (~500K barrels). Acceptable omission for Phase 1 |
| **Infeasible LP** | MEDIUM | If all suppliers are sanctioned or all routes disrupted, the LP has no feasible solution. The ranking fallback handles this, but the code must detect infeasibility gracefully |
| **`linprog` vs PuLP** | LOW | Either works. `scipy.optimize.linprog` is simpler (no extra dependency). PuLP adds modeling flexibility but is an extra install |
| **Compatibility is a hard constraint but stored as soft score** | MEDIUM | The compatibility matrix uses HIGH/MEDIUM/LOW scores, but the LP treats incompatible grades as excluded. The boundary between "MEDIUM compatibility" and "incompatible" needs a threshold |
| **Risk penalty formula uses multiplicative interaction** | LOW | `risk_penalty = λ × route_risk × price_cif` — this means risk penalty scales with price, which may not be intended. Consider additive penalty instead |

### LLM must NOT generate recommendations — CONFIRMED

The optimization engine is fully algorithmic. No changes needed to this boundary.

**Recommendation:** KEEP the LP design. Implement ranking first, LP second. Ensure infeasibility is caught.

---

## 13. Backend Risks

| Issue | Severity | Assessment |
|---|---|---|
| **30+ endpoints** | HIGH | Addressed in HIGH-1. Reduce to ~12 for MVP |
| **APScheduler embedded in FastAPI process** | MEDIUM | If the FastAPI server restarts, all scheduled jobs restart. Acceptable for demo. For robustness, use APScheduler's PostgreSQL jobstore |
| **No background task for scenario computation** | MEDIUM | `POST /scenarios/run` may take 1–5 seconds. Should return immediately with a scenario_id and let the frontend poll for results, OR compute synchronously if fast enough |
| **No pagination on GET /events** | LOW | Query params include limit/offset, which is fine |
| **CORS configuration** | LOW | Documented correctly (allow frontend origin) |
| **No input validation on scenario parameters** | MEDIUM | The API spec shows `capacity_reduction_pct: 50` but doesn't define valid ranges. Must validate: 0 ≤ pct ≤ 100, 1 ≤ duration ≤ 365 |

**Recommendation:** KEEP FastAPI. Reduce endpoint count. Add Pydantic request models with validation for all POST endpoints.

---

## 14. Frontend Risks

| Issue | Severity | Assessment |
|---|---|---|
| **5 pages/panels is ambitious** | MEDIUM | For one developer, 3–4 pages max. Combine Procurement + SPR into the Scenario results view |
| **Leaflet map with 20+ markers, routes, risk overlays** | MEDIUM | Leaflet itself is straightforward. Risk-colored route lines require GeoJSON data that doesn't currently exist in the schema |
| **Evidence drawer** | HIGH (demo value) | This is the strongest UX differentiator. Must be implemented. A slide-out panel with the tree view shown in UI_UX.md is achievable |
| **Data classification badges on every element** | LOW | Simple CSS badges. Low effort, high credibility impact |
| **CSS framework undecided** | MEDIUM | Must be decided Day 1. Vanilla CSS is viable but slower; a utility framework speeds development |
| **Recharts for price history** | LOW | Nice to have. Only implement if EIA historical data is successfully loaded |
| **Export/share** | LOW | Addressed in MED-11. Defer |
| **Demo mode banner** | LOW | Simple conditional banner. Must be implemented |

### What's visually impressive but technically unnecessary?

- 3D globe / Three.js — correctly excluded
- Animated tanker movements — correctly excluded
- Real-time WebSocket event feed — unnecessary; polling every 30s is sufficient

### What's the minimum viable frontend?

1. Risk overview page (corridor cards + event feed + quick stats)
2. Map page (Leaflet with markers and route lines)
3. Scenario + Procurement page (combined — run scenario → see results + recommendations)
4. Evidence drawer (accessible from any page)

**Recommendation:** CHANGE — Combine Scenario Simulator and Procurement into one page. The user flow is: select scenario → see impact → see procurement alternatives. Splitting them across pages adds navigation overhead.

---

## 15. Security Risks

| Risk | Severity | Phase 1 Mitigation |
|---|---|---|
| **API keys in .env file** | LOW | .gitignore correctly excludes .env. .env.example has placeholder values. Acceptable |
| **No authentication** | LOW | Correct for hackathon. No user data to protect |
| **Prompt injection from news articles** | MEDIUM | News article text goes directly into LLM prompts. A malicious article could contain prompt injection. Mitigation: strip HTML, truncate to 2000 chars, use system prompt separation |
| **SQL injection** | LOW | SQLAlchemy ORM prevents this. No raw SQL in application code (planned) |
| **Scenario parameter manipulation** | LOW | Pydantic validation on POST /scenarios/run prevents absurd values (e.g., duration = 999999) |
| **CORS misconfiguration** | LOW | Restrict to `http://localhost:3000` only |
| **Debug endpoints exposed** | LOW | FastAPI's `/docs` and `/redoc` are useful during demo. Acceptable |
| **Secrets in docker-compose.yml** | LOW | docker-compose.yml uses `${POSTGRES_PASSWORD}` env var substitution. Acceptable |

**Recommendation:** KEEP security posture as-is. Add input truncation for LLM prompts (max 2000 chars of article text).

---

## 16. Failure-Mode Analysis

| Component | Failure | Impact | Fallback | Status |
|---|---|---|---|---|
| **GDELT** | API unavailable | No new events | Pre-loaded fixture events + "DEMO MODE" banner | DOCUMENTED |
| **ACLED** | Registration not approved | No conflict data | Skip; GDELT provides sufficient coverage | NOT DOCUMENTED |
| **EIA** | API key invalid or rate-limited | No price data | Hardcoded recent Brent price with HISTORICAL label | DOCUMENTED |
| **RBI** | API unavailable | No FX rate | Hardcoded recent USD/INR rate | NOT DOCUMENTED |
| **LLM provider** | API unavailable or timeout | No event extraction | Pre-parsed seed events; disable extraction button | DOCUMENTED |
| **LLM** | Malformed JSON response | Event not extracted | Retry once; if still malformed, skip article and log | NOT DOCUMENTED |
| **LLM** | Hallucinated entity/corridor | Wrong risk attribution | Post-extraction validation against entity whitelist | NOT DOCUMENTED |
| **PostgreSQL** | Connection failure | Nothing works | Fatal — no recovery. Ensure DB is up before demo | DOCUMENTED (SQLite fallback mentioned but unrealistic) |
| **Scenario engine** | Division by zero (0% disruption) | Crash | Guard clause: if disruption_pct == 0, return baseline | NOT DOCUMENTED |
| **LP optimizer** | Infeasible problem | No recommendations | Deterministic ranking fallback | DOCUMENTED |
| **LP optimizer** | Numerical instability | Wrong results | Validate: all allocations ≥ 0, total = target | NOT DOCUMENTED |
| **Leaflet tiles** | Tile server unavailable | Blank map | Use cached tiles or static fallback image | DOCUMENTED |
| **Frontend** | API timeout (>5s) | Loading spinner forever | Set 10s timeout, show "Service unavailable" | NOT DOCUMENTED |
| **Redis** | Unavailable | Slower API | Direct DB queries (documented) | DOCUMENTED |

**Missing fallbacks that need documentation:** LLM retry, hallucination validation, RBI fallback, scenario edge cases, frontend timeout handling.

---

## 17. Hackathon Judge Attack

### "What would make me think this is fake?"

1. **Static risk scores that never change** — If Hormuz is always 78 regardless of events, it's hardcoded
2. **Scenario results identical regardless of parameters** — Change duration from 30 to 60 days and the gap doesn't change? Fake
3. **No evidence drill-down** — A score of 78 with no explanation = hardcoded
4. **"Real-time" labels on obviously static data** — Claiming LIVE on PPAC annual data is immediately detectable
5. **Procurement recommendations that don't change** — If the top result is always Arab Light regardless of scenario, the optimizer isn't running

### "What would make me think the AI is just an API wrapper?"

1. The LLM call returns structured data → that's exactly what it should do. The defense is: "The LLM handles extraction. Risk scoring is deterministic formula. Scenario simulation is parametric. Procurement is LP optimization. The hybrid approach is more reliable."
2. **Missing:** The system should log and display which model was used, input/output tokens, and latency for each extraction. This proves the LLM is actually being called.

### "What number would I challenge?"

1. **$15/bbl price impact** — "Where does this number come from?" → Answer: EIA historical data from Gulf War II, Houthi disruption
2. **3.2x freight multiplier** — "Why 3.2?" → Answer: Cape route is ~3x longer than Hormuz route in nautical miles
3. **42% Hormuz dependency** — "Source?" → Answer: PPAC import-by-source data FY2024-25
4. **9.5 days SPR coverage** — "How?" → Answer: 5.33 MMT / 0.56 MMT per day

### "What feature is unnecessary?"

1. **GDP impact estimate** — Remove it. Un-defensible without macroeconomic modeling
2. **Price history charts** — Nice but not part of the core chain. Build last
3. **Weather overlay** — SHOULD HAVE, build only if everything else works

### "What is the strongest technical differentiator?"

The **evidence trail** — being able to click any score and drill down through: source article → extracted event → risk contribution → scenario assumptions → recommendation. No competitor does this for India-specific refinery-level analysis.

### "What single failure could destroy the demo?"

**PostgreSQL not starting.** Everything depends on it. Test database connection first, before anything else.

Second most likely: **LLM provider rate-limited mid-demo.** Mitigation: pre-populate several extracted events so the demo can proceed even if the LLM is unavailable during the presentation.

---

## 18. Buildability Assessment

| Component | Complexity | Debug Complexity | Data Availability | Dependencies | Time Estimate | Feasibility |
|---|---|---|---|---|---|---|
| PostgreSQL schema + seed data | LOW | LOW | HIGH | None | 2–3 hours | ✅ |
| GDELT poller + parser | MEDIUM | MEDIUM | HIGH | httpx, APScheduler | 3–4 hours | ✅ |
| LLM extraction pipeline | MEDIUM | HIGH | HIGH | LLM provider API | 4–6 hours | ✅ |
| Risk scoring engine | LOW | LOW | HIGH | None (pure Python) | 2–3 hours | ✅ |
| Scenario engine | MEDIUM | MEDIUM | HIGH | None (pure Python) | 4–5 hours | ✅ |
| Procurement ranker | MEDIUM | MEDIUM | MEDIUM | scipy (optional) | 3–4 hours | ✅ |
| SPR engine | LOW | LOW | HIGH | None | 1–2 hours | ✅ |
| FastAPI endpoints (12 MVP) | MEDIUM | LOW | N/A | FastAPI, SQLAlchemy | 4–6 hours | ✅ |
| React risk dashboard | MEDIUM | MEDIUM | N/A | React | 4–6 hours | ✅ |
| Leaflet map | MEDIUM | HIGH | MEDIUM (GeoJSON needed) | react-leaflet | 4–6 hours | ⚠️ |
| Evidence drawer | MEDIUM | MEDIUM | N/A | React | 3–4 hours | ✅ |
| EIA price integration | LOW | LOW | HIGH | httpx | 1–2 hours | ✅ |
| OFAC sanctions check | LOW | LOW | HIGH | httpx | 1–2 hours | ✅ |
| LP optimization (PuLP) | HIGH | HIGH | MEDIUM | PuLP/scipy | 3–5 hours | ⚠️ |
| NetworkX supply graph | MEDIUM | MEDIUM | MEDIUM | NetworkX | 3–4 hours | ⚠️ |
| XGBoost model (Phase 2) | VERY HIGH | VERY HIGH | LOW | XGBoost, SHAP, training data | 8+ hours | ❌ Phase 2 |
| Docker deployment | LOW | MEDIUM | N/A | Docker | 1–2 hours | ✅ |

**Total estimated hours (MVP):** ~40–55 hours of focused work

**Available time (4 days, 10-12 hrs/day):** ~40–48 hours

**Assessment:** Tight but feasible if the developer stays disciplined. The LP optimization and NetworkX graph are the highest-risk items and should be built last (ranking fallback is sufficient for the demo).

---

## 19. Specific Recommended Changes

| # | Change | Classification | Priority | Effort |
|---|---|---|---|---|
| 1 | Add `corridors` table to schema | CHANGE | P0 — CRITICAL | 30 min |
| 2 | Change `events.country_id` to `affected_country_ids INT[]` | CHANGE | P0 — CRITICAL | 15 min |
| 3 | Add `affected_corridor_ids` column to events table | CHANGE | P0 — CRITICAL | 15 min |
| 4 | Fix `price_history` GENERATED column issue | CHANGE | P0 — CRITICAL | 30 min |
| 5 | Add `crude_grades` reference table | CHANGE | P1 — HIGH | 20 min |
| 6 | Add `refinery_supply_mix` table | CHANGE | P1 — HIGH | 30 min |
| 7 | Remove `strategic_reserves.days_coverage` GENERATED column | CHANGE | P1 — HIGH | 10 min |
| 8 | Reduce API to ~12 MVP endpoints | CHANGE | P1 — HIGH | 0 (planning) |
| 9 | Freeze risk score scale: 0–100 display, 0.0–1.0 internal | CHANGE | P1 — HIGH | 0 (decision) |
| 10 | Remove `gdp_impact_estimate_usd_bn` from scenario_results | REMOVE | P1 — HIGH | 5 min |
| 11 | Add `procurement_options.scenario_id` FK | CHANGE | P2 — MEDIUM | 5 min |
| 12 | Add `updated_at` to all reference tables | CHANGE | P2 — MEDIUM | 15 min |
| 13 | Merge `crude_prices` and `price_history` tables | CHANGE | P2 — MEDIUM | 20 min |
| 14 | Standardize on httpx (remove aiohttp) | CHANGE | P2 — MEDIUM | 0 (decision) |
| 15 | Combine Scenario + Procurement into one frontend page | CHANGE | P2 — MEDIUM | 0 (planning) |
| 16 | Add LLM retry/timeout/fallback to provider interface | CHANGE | P2 — MEDIUM | 0 (design) |
| 17 | Document demo mode architecture | CHANGE | P2 — MEDIUM | 30 min |
| 18 | Drop Redis from Phase 1 docker-compose | REMOVE | P3 — LOW | 5 min |
| 19 | Drop PostGIS from Phase 1 | REMOVE | P3 — LOW | 0 (decision) |
| 20 | Update README hackathon reference | CHANGE | P3 — LOW | 5 min |

---

## 20. Decisions That Should Be Frozen Before Step 2

These decisions **must** be locked before coding begins:

| # | Decision | Recommended Resolution |
|---|---|---|
| 1 | Risk score display scale | **0–100** for all user-facing scores |
| 2 | Internal severity/weight scale | **0.0–1.0** for all internal computations |
| 3 | HTTP client library | **httpx** |
| 4 | LP library | **scipy.optimize.linprog** (no extra dependency beyond scipy) |
| 5 | CSS framework | **Ask user** — Vanilla CSS or Tailwind (per user's system rules) |
| 6 | Number of demo pages | **4** — Risk Overview, Map, Scenario+Procurement, Evidence (drawer) |
| 7 | API endpoint count (MVP) | **~12** as listed in HIGH-1 |
| 8 | Phase 1 ML approach | **Rule-based weighted scoring only** |
| 9 | Redis in Phase 1 | **NO** — remove from docker-compose |
| 10 | PostGIS in Phase 1 | **NO** — use plain lat/lon |

---

## 21. Decisions That Should Deliberately Remain Flexible

| # | Decision | Why Keep Flexible |
|---|---|---|
| 1 | Application LLM provider/model | Must benchmark before selecting |
| 2 | Risk weight values | Should be tunable via config; will be adjusted during testing |
| 3 | Scenario parameters (price impact, freight multiplier) | Should be calibrated against EIA historical data |
| 4 | LP vs ranking for procurement | Implement ranking first; LP is an upgrade |
| 5 | NetworkX vs SQL joins for graph queries | Depends on actual query patterns during implementation |
| 6 | Number of preset scenarios (4 or 5) | Depends on implementation stability |
| 7 | Compatibility threshold (what score = "incompatible"?) | Needs domain testing |
| 8 | Event confidence threshold (currently 0.6) | May need adjustment based on LLM quality |

---

## 22. Questions That Cannot Yet Be Answered Without Data or Experiments

| # | Question | Why Unanswerable Now | When Answerable |
|---|---|---|---|
| 1 | Which LLM extracts INDRA events most reliably? | No benchmark dataset exists yet | After pipeline is built and 50 test articles are curated |
| 2 | What risk weights produce historically-calibrated scores? | No historical disruption labels exist | After EIA historical price spike data is loaded |
| 3 | Does ACLED API approval arrive in time? | Depends on ACLED team response time | Day 1–2 |
| 4 | Does the RBI API actually work for USD/INR? | No one has tested it | Day 1 |
| 5 | Is the LP optimizer numerically stable with INDRA's data? | Depends on actual constraint matrix dimensions | After seed data is loaded |
| 6 | How noisy is GDELT for energy-specific events? | Depends on keyword filter quality | After first GDELT poll |
| 7 | Can the full chain run in <5 seconds? | Depends on LLM latency + DB query time | After E2E integration |
| 8 | Are the refinery compatibility scores defensible? | No verified public source for refinery crude specifications | Requires PPAC/company report verification |

---

## Final Summary

**A. Files created:** `docs/02-architecture/ARCHITECTURE_REVIEW.md` (this file)

**B. Files modified:** None

**C. Architecture issues discovered:** 3 critical blockers + 7 high-risk + 12 medium-risk + 5 low-risk = **27 total**

**D. Top 10 changes recommended before coding:**

1. Add `corridors` table to database schema
2. Add `affected_corridor_ids` to events table (replace/supplement `affected_route_ids`)
3. Change `events.country_id` to `affected_country_ids INT[]`
4. Fix `price_history` GENERATED column / merge price tables
5. Add `crude_grades` reference table
6. Add `refinery_supply_mix` relationship table
7. Freeze risk score scale at 0–100 display / 0.0–1.0 internal
8. Reduce API to ~12 MVP endpoints
9. Remove `gdp_impact_estimate_usd_bn` from scenario results
10. Remove `days_coverage` GENERATED column from strategic_reserves

**E. Unresolved questions:** 8 items requiring data or experiments (see §22)

**F. Confirmation: No datasets were downloaded.**

**G. Confirmation: No APIs were connected.**

**H. Confirmation: No application feature code was written.**

---

*Review complete. Do not proceed to Step 2 until the critical blockers are addressed.*
