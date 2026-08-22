# INDRA — XGBoost Phase-2 Candidate Evaluation

**Status:** NOT STARTED — planning/data-gap assessment only; no model training or integration was performed.  
**Audit date:** 22 August 2026  
**Production baseline:** Phase-1 weighted deterministic risk engine

## Decision

No XGBoost model was trained. The repository does not contain an independent,
time-indexed disruption outcome series that can support a defensible target,
temporal split, or comparison against the deterministic risk engine. Training
on seed data, scenario outputs, parser fixtures, or the extraction benchmark
would fabricate or circularly derive labels and is prohibited.

## Dataset gap report

| Available material | What it represents | Suitable as outcome labels? |
|---|---|---:|
| `data/seed/*.csv` and `db/seed.sql` | Reference entities, calibrated parameters, routes, capacities, and assumptions | No |
| `geopolitical_events` seed state | No validated historical event/outcome panel | No |
| `data/eval/extraction_benchmark.json` | Synthetic paraphrase examples for LLM extraction quality | No |
| Ingestion fixtures | Adapter/parser contract fixtures, not historical outcomes | No |
| OFAC raw/processed data | Sanctions reference snapshot | No, by itself |
| RBI sample FX file | Three observations; not a disruption target | No |
| Scenario and risk outputs | Derived or simulated INDRA outputs | No; circular/leaky |
| ACLED/GDELT historical events | Not acquired; deferred or credential-gated | Missing |
| EIA historical prices/supply observations | Not acquired; registration required | Missing |

The reported 1,677 historical/reference records are primarily OFAC reference
rows plus a three-row RBI sample. They are not a labeled corridor-disruption
panel. No model, metrics, feature-importance artifact, or ML prediction has
been produced.

## Proposed target definition

Use one observation per corridor-day (or a predefined event cluster and
corridor) at a documented feature cut-off time. For a horizon of 7, 14, or 30
days, define `disruption = 1` only when an independent observed source records
a measurable disruption to supply, production, imports, route availability,
or transit capacity during the horizon. Define `disruption = 0` only when the
same source coverage confirms no qualifying disruption. Ambiguous or
unobserved windows remain unknown, never forced to zero.

The target must not be calculated from the Phase-1 risk score, scenario engine,
procurement output, or any feature observed after the cut-off.

## Exact additional data required

1. Timestamped ACLED (or equivalent licensed event) records for at least
   2019–2025, with event type, location, actors, source, and provenance.
2. Timestamped GDELT/news observations or another event source for event
   clusters and corroboration, without post-horizon information.
3. EIA, IEA, PPAC, or equivalent observed production, import, supply, route,
   or refinery disruption time series with source and publication timestamps.
4. Dated OFAC/EU/UN sanctions snapshots and supplier/country mappings.
5. Versioned corridor, route, supplier, and refinery mappings for the period.
6. Sufficient negative windows, consistent coverage, and license/provenance
   records for every label.

## Proposed features and leakage controls

Candidate pre-cutoff features are event counts and severity history over 7/30
days, earlier-window disruption frequency, corridor and supplier concentration,
India dependency, dated sanctions indicators, route exposure, and lagged
market/seasonal variables whose source timestamp precedes the cutoff. Future
reports, post-disruption prices, future-event risk scores, scenario results,
and outcome-derived fields are prohibited. Feature generation must assert that
every feature timestamp is at or before its observation cutoff.

## Proposed experiment (not run)

- Temporal split: train 2019–2023, validation 2024, test 2025, adjusted only
  after actual coverage is inspected.
- Model: small XGBoost binary classifier, fixed preprocessing, seed 42, and a
  documented model version; no broad hyperparameter search.
- Metrics: ROC-AUC, PR-AUC, precision, recall, F1, Brier/calibration score,
  confusion matrix, and stability across temporal test slices.
- Baseline: evaluate the existing deterministic score against the same
  independent labels; report differences, calibration, and failure modes.
- Explainability: feature importance or SHAP only after a real model exists;
  importance is not causation.

## Recommendation

**Decision C — INSUFFICIENT DATA FOR VALID EVALUATION.** Keep the weighted
deterministic engine as the production baseline. Complete the acquisition and
label-validation work above before adding XGBoost dependencies or generating
ML artifacts. Step 8E is COMPLETE; Step 10 remains NOT STARTED.
