# INDRA — Testing Strategy

> **STATUS: FROZEN FOR PHASE 1 IMPLEMENTATION.** Step 3 verified the local foundation manually; feature test cases below remain planned until their corresponding implementation steps.
>
> This document defines the testing contract for INDRA. Tests should be written alongside Step 3 implementation, not before.

---

## Testing Principles

1. **Test the chain, not just components** — The most important test is the full event→recommendation pipeline
2. **Test computation correctness** — Risk scores, scenario results, and optimizer outputs must be deterministic and verifiable
3. **Test data integrity** — Every data classification tag must be accurate
4. **Test gracefully degradation** — External API failures should not crash the system
5. **No fabricated test results** — Report actual test outcomes

## Step 3 Foundation Checks

Implemented scope is deliberately limited to the FastAPI startup foundation, `GET /health`, PostgreSQL connectivity reporting, and the React/Vite startup shell. Run the commands in the backend and frontend development setup documents to verify them independently.

`GET /health` must respond successfully whether PostgreSQL is connected or temporarily unavailable; its `database` field communicates the dependency state without leaking credentials. Full schema, business API, engine, and UI tests below are planned for later steps.

---

## Unit Tests

### Risk Engine Tests

| Test | Description | Expected |
|---|---|---|
| `test_risk_score_within_range` | Internal score 0.0–1.0; display 0–100 | Pass |
| `test_risk_score_deterministic` | Same inputs → same output | Pass |
| `test_risk_components_sum_correctly` | Component weights sum to 1.0 | Pass |
| `test_risk_level_classification` | Score 78 → CRITICAL | Pass |
| `test_risk_evidence_populated` | Every score has contributing events | Pass |
| `test_no_events_returns_baseline` | No recent events → base country risk only | Pass |

### Scenario Engine Tests

| Test | Description | Expected |
|---|---|---|
| `test_hormuz_full_closure_gap` | 100% Hormuz closure × 30 days → supply gap ≈ 7.06 MMT | Pass (within tolerance) |
| `test_hormuz_partial_scales_linearly` | 50% → half the gap of 100% | Pass |
| `test_russia_loss_affects_correct_share` | Russia loss uses ~37% share | Pass |
| `test_spr_bridge_calculation` | SPR bridge days = SPR / daily gap | Pass |
| `test_scenario_output_labeled_derived` | All outputs have `data_semantic: DERIVED` | Pass |
| `test_zero_duration_returns_no_gap` | 0-day disruption → 0 supply gap | Pass |

### Procurement Engine Tests

| Test | Description | Expected |
|---|---|---|
| `test_sanctioned_supplier_excluded` | Sanctioned supplier never appears in recommendations | Pass |
| `test_disrupted_route_excluded` | Route marked disrupted → not recommended | Pass |
| `test_compatibility_filter` | Grade with compatibility_score < 0.5 excluded | Pass |
| `test_ranking_changes_with_scenario` | Different scenario → different ranking | Pass |
| `test_risk_aversion_changes_ranking` | Higher λ → safer (but costlier) options ranked higher | Pass |
| `test_top_recommendation_has_evidence` | Top result includes scoring breakdown | Pass |

### Entity Resolution Tests

| Test | Description | Expected |
|---|---|---|
| `test_fuzzy_match_aramco` | "Saudi Aramco" → "Saudi Arabian Oil Company" | Pass |
| `test_fuzzy_match_hormuz` | "Strait of Hurmuz" → "Strait of Hormuz" | Pass |
| `test_exact_match_country` | "Iraq" → Iraq entity | Pass |

---

## Integration Tests

### Data Ingestion Pipeline

| Test | Description |
|---|---|
| `test_gdelt_poller_returns_events` | GDELT API call returns parseable data |
| `test_acled_poller_returns_events` | ACLED API call returns conflict events |
| `test_eia_poller_returns_prices` | EIA API returns crude price data |
| `test_rbi_poller_returns_fx` | RBI API returns USD/INR rate |
| `test_ofac_poller_returns_sanctions` | OFAC data parseable |
| `test_event_stored_in_database` | Parsed event correctly inserted into PostgreSQL |
| `test_duplicate_event_rejected` | Same event from two sources → single record |

### LLM Structured-Output Validation

| Test | Description |
|---|---|
| `test_llm_extraction_returns_valid_json` | LLM output parses as valid JSON |
| `test_llm_extraction_matches_schema` | Output matches Pydantic StructuredEvent schema |
| `test_llm_extraction_no_database_ids` | Output contains names/codes only, never integer entity IDs |
| `test_llm_extraction_event_type_valid` | event_type is one of allowed enum values |
| `test_llm_extraction_severity_in_range` | severity is within valid range |
| `test_llm_confidence_threshold` | Events with confidence < 0.6 excluded from risk update |
| `test_llm_fallback_on_api_error` | LLM API timeout → graceful fallback |

### Database Tests

| Test | Description |
|---|---|
| `test_schema_tables_exist` | All 20 conceptual tables created |
| `test_corridor_fk_integrity` | Events reference valid corridor IDs after resolution |
| `test_entity_alias_lookup` | Alias resolves to canonical entity |
| `test_commodity_fx_separate` | No synchronized INR generated column |

### Ingestion Tests

## API Tests

| Test | Description |
|---|---|
| `test_get_events_returns_200` | GET /api/v1/events returns 200 with event list |
| `test_get_risk_corridors_returns_200` | GET /api/v1/risk/corridors returns risk scores |
| `test_post_scenario_returns_results` | POST /api/v1/scenarios/run returns scenario results |
| `test_get_recommendations_returns_ranked` | GET /api/v1/recommendations/{id} returns ranked options |
| `test_get_reserves_returns_spr_data` | GET /api/v1/reserves returns SPR locations |
| `test_get_prices_returns_current` | GET /api/v1/prices/current returns price data |
| `test_health_check` | GET /api/v1/health returns 200 |
| `test_invalid_scenario_returns_422` | Invalid scenario parameters → 422 validation error |
| `test_cors_headers_present` | CORS headers allow frontend origin |

---

## ML Tests (Phase 2)

| Test | Description |
|---|---|
| `test_xgboost_model_loads` | Saved model file loads without error |
| `test_xgboost_prediction_in_range` | Prediction output is probability [0, 1] |
| `test_xgboost_deterministic` | Same features → same prediction |
| `test_shap_values_computed` | SHAP explanation generated for prediction |
| `test_model_evaluation_metrics_recorded` | Evaluation produces accuracy, F1, confusion matrix |

---

## Scenario Tests

| Test | Description |
|---|---|
| `test_all_preset_scenarios_run` | Each preset scenario completes without error |
| `test_scenario_results_internally_consistent` | supply_gap + spr_bridge + uncovered_gap = total_gap |
| `test_scenario_results_reasonable_magnitude` | 30-day Hormuz closure gap is in single-digit MMT range (not billions) |
| `test_scenario_cost_impact_reasonable` | Additional cost for 30-day disruption is $1–10B range for India |

---

## Optimizer Tests

| Test | Description |
|---|---|
| `test_lp_feasible_solution` | LP solver finds a feasible solution |
| `test_lp_respects_capacity_constraints` | No supplier allocated more than capacity |
| `test_lp_excludes_sanctioned` | Sanctioned suppliers have 0 allocation |
| `test_lp_meets_target_volume` | Total allocated volume ≥ target |
| `test_ranking_fallback_works` | If LP fails, deterministic ranking produces results |

---

## Frontend Tests

| Test | Description |
|---|---|
| `test_risk_dashboard_renders` | Risk overview page loads with corridor cards |
| `test_map_renders_india` | Leaflet map shows India with markers |
| `test_scenario_form_submits` | Scenario form sends request to backend |
| `test_recommendation_table_renders` | Procurement table shows ranked results |
| `test_evidence_drawer_opens` | Clicking risk score opens evidence panel |
| `test_data_semantic_badges_visible` | OBSERVED/DERIVED/HISTORICAL_CALIBRATED/ASSUMED/SIMULATED badges displayed |
| `test_stale_data_banner` | Stale feed shows last-updated banner |
| `test_demo_mode_banner` | Demo mode shows distinct banner when fixtures active |

---

## End-to-End Pipeline Test

**The most important test.** Verifies the complete chain works:

```
1. Insert a test event (or trigger ingestion of a known article)
2. Verify LLM extracts structured event
3. Verify event is stored in database
4. Verify risk score recalculates for affected corridor
5. Run a scenario using the affected corridor
6. Verify supply gap is calculated
7. Verify procurement alternatives are ranked
8. Verify SPR bridge is calculated
9. Verify evidence trail links event → risk → scenario → recommendation
10. Verify API returns all data correctly
11. Verify frontend renders the results
```

This test should be runnable as a single command for demo preparation.

---

## Data Source Validation

| Test | Description |
|---|---|
| `test_seed_refineries_count` | Database has ~20 Indian refineries |
| `test_seed_spr_locations` | Database has exactly 3 SPR locations |
| `test_seed_routes_exist` | Database has ≥15 supply routes |
| `test_refinery_coordinates_in_india` | All refinery lat/lon are within India bounds |
| `test_spr_capacity_matches_official` | Total SPR = 5.33 MMT |

---

## Model Output Validation

| Test | Description |
|---|---|
| `test_risk_score_has_evidence` | No risk score without component breakdown |
| `test_scenario_output_has_assumptions` | Every scenario result lists its assumptions |
| `test_recommendation_has_scoring` | Every procurement option has scoring details |
| `test_simulated_data_labeled` | Demo fixtures have `is_simulated: true` |

---

## Test Frameworks

| Layer | Framework |
|---|---|
| Backend unit tests | pytest |
| API tests | pytest + httpx (TestClient) |
| Frontend tests | Jest + React Testing Library |
| E2E tests | pytest (scripted) or Playwright |
### Step 6B verification

Run `python -m pytest backend/tests -q`. The suite covers structured-event validation, provider retry/validation behavior, deterministic risk/scenario/optimizer calculations, and Step-6A resolution integration. No external APIs or datasets are required.

Step 6C frontend verification: `npm run build` completes successfully. The browser flow uses the live FastAPI endpoints and renders unavailable/empty states when optional data is absent.
