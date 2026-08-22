# INDRA — Phase-2 XGBoost Data-Sufficiency Audit

> **Status:** Step 11B evaluation complete — **INSUFFICIENT DATA**
>
> **Decision:** No XGBoost training, evaluation metrics, model artifacts, or
> integration were produced. The Phase-1 weighted deterministic risk engine
> remains authoritative.
>
> **Audit date:** 22 August 2026

## Decision Basis

The current repository cannot define a defensible prediction target. A valid
Phase-2 target would be an **independently observed corridor disruption outcome
within a fixed future horizon**. The repository has no time-indexed outcome
series, no independent negative windows, and no historical feature panel that
precedes such outcomes.

Training on the existing materials would be invalid because the apparent
labels would either be simulated, calibrated reference values, or outputs of
the same deterministic calculations intended as the baseline.

## Actual Data Inventory

| Material | Observed audit result | Why it cannot support training |
|---|---|---|
| `geopolitical_events` | 2 persisted GDELT events; same observed timestamp window | No historical target/outcome horizon or negative control windows |
| `risk_scores` | 0 rows | No target or baseline-score history |
| `commodity_prices` | 0 rows | No observed price series or timestamped supply outcome |
| `fx_rates` | 3 RBI fallback observations | Too few rows and unrelated to disruption outcome labels |
| Seed CSVs / `db/seed.sql` | Curated reference entities and calibrated/assumed parameters | Not a historical event-outcome panel; scenario/risk values would be circular labels |
| `data/eval/extraction_benchmark.json` | 25 synthetic LLM extraction examples | Evaluates extraction schema/fields, not physical supply disruption |
| OFAC snapshot | Reference snapshot/processed extract | No dated supplier/corridor outcome labels by itself |
| Ingestion fixtures | Parser/normalization tests | Fixtures are not real historical observations |
| ACLED/GDELT/EIA historical panels | Not acquired in the repository | Required independent time-series data is missing |

## Target Audit

| Requirement | Result |
|---|---|
| Target definition | Proposed only; not observed in current data |
| Target timestamp | Missing |
| Prediction horizon | Proposed only; 7, 14, or 30 days requires future outcomes |
| Sample size | Insufficient: no corridor-day/event-cluster panel |
| Independent labels | Missing |
| Circular-label check | Fails if Phase-1 risk, scenario output, or seed calibration is used |
| Temporal split | Impossible without a dated panel |

## Required Future Dataset

Build one row per corridor-day (or a predeclared event cluster and corridor)
with a recorded feature cutoff timestamp. For each row, independently label a
disruption observed **after** the cutoff over a fixed 7-, 14-, or 30-day
horizon. Unknown-coverage windows must remain unknown, not become negatives.

Required, versioned inputs:

1. Historical ACLED or equivalent licensed conflict/event records from at
   least 2019–2025, including publication/event timestamps and provenance.
2. Historical GDELT/news event observations for corroboration and pre-cutoff
   event features.
3. Independent observed supply, import, production, route-availability, or
   transit-capacity outcomes from EIA, IEA, PPAC, or an equivalent source.
4. Dated sanctions snapshots and versioned supplier/corridor/route mappings.
5. Enough covered non-disruption windows to estimate false positives and
   calibration, not merely disruption cases.

## Future Evaluation Protocol (Not Run)

1. Freeze target and feature specifications before inspecting the test period.
2. Enforce `feature_timestamp <= cutoff_timestamp` for every feature; exclude
   post-event prices, later reports, scenario results, and Phase-1 risk output.
3. Deduplicate source observations and keep source/publication timestamps.
4. Use a temporal split such as train 2019–2023, validation 2024, test 2025,
   adjusted only after documented coverage review.
5. Train a restrained, seeded XGBoost classifier and compare it against the
   existing deterministic score on the **same independent labels**.
6. Report ROC-AUC, PR-AUC, precision, recall, F1, Brier/calibration,
   confusion matrix, temporal stability, and documented failure cases.

## Outcome

**INSUFFICIENT DATA FOR VALID EVALUATION.** No model selection, feature
importance, SHAP analysis, or production change is justified. Step 8D-B
remains **NOT STARTED** because its deliverable—an implemented Phase-2
candidate—does not exist.

See [XGBOOST_EVALUATION.md](XGBOOST_EVALUATION.md) for the earlier planning
assessment; this document is the Step 11B audit record.
