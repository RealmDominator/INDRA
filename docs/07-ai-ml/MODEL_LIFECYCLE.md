# INDRA Data, LLM, and Model Lifecycle

## Guardrails

The Phase-1 weighted deterministic risk engine is authoritative. The runtime LLM is limited to structured extraction; it does not calculate risk, scenario, or procurement values and does not emit database IDs. The provisional OpenRouter model is not a benchmark winner. XGBoost remains unimplemented because `XGBOOST_DATA_GAP.md` found insufficient valid training data.

## LLM provider governance

Any candidate runtime model must be evaluated with the same versioned INDRA extraction dataset and prompt. The live benchmark must report:

- structured-output validity and schema rejection rate;
- event-type/severity extraction accuracy;
- country/corridor entity-recognition quality after resolution;
- hallucination rate, including database-ID violations;
- latency, access/cost assumptions, retry count, and failure rate.

Run the offline contract check with:

```powershell
python scripts/benchmark/run_llm_benchmark.py --offline
```

Run the live comparison only with a configured `OPENROUTER_API_KEY` and record the exact dataset, prompt, candidate models, timestamp, failures, and cost assumptions. A model change requires a documented comparison against the current provisional model, approval under the release gates below, and mocked provider/E2E regression tests. Configuration alone must not be treated as selection evidence.

## Prompt versioning

The extraction prompt in `backend/app/providers/openrouter.py` is versioned as `indra-event-extraction/v1`. Provider metadata records this version alongside provider/model, timeout, retry count, and extraction latency. The benchmark harness sends the same prompt contract.

Any prompt change must increment the prompt version, preserve the `StructuredEvent` names/codes-only schema, rerun the offline benchmark and provider tests, and record expected compatibility or behavior changes. Prompt changes must not silently alter benchmark comparability.

## Phase-2 XGBoost governance

The future path is strictly:

```text
deterministic baseline → versioned historical dataset → independent target
→ feature-cutoff/leakage audit → temporal split → XGBoost candidate
→ same-label comparison → approval decision
```

The target must be an independently observed future corridor-disruption outcome. Features must be available before the cutoff. Derived risk/scenario values, seed assumptions, synthetic fixtures, and post-outcome data cannot become labels or features. The future report must include temporal train/validation/test periods, seed/parameters, metrics (ROC-AUC, PR-AUC, precision, recall, F1, Brier/calibration, confusion matrix), stability, failure modes, and comparison against the deterministic baseline on identical labels.

Possible decisions are: candidate better than baseline, candidate not better, or insufficient data. Even a better candidate does not replace Phase 1 without an explicit future integration decision.

## Release gates

| Change | Required approval evidence |
|---|---|
| Dataset/source | Versioned manifest, checksum, schema/semantic/FK/provenance validation, duplicate and rollback review. |
| Provider/model | Same benchmark/prompt/dataset comparison, failure/latency/access results, safe fallback tested. |
| Prompt | New prompt version, structured-output regression, offline benchmark comparison, entity-resolution review. |
| ML model | Defensible target, leakage audit, temporal split, baseline comparison, reproducibility artifact, explicit approval. |
| Risk weights | Versioned weights, component/provenance tests, deterministic regression and domain approval. |
| Scenario formula | Versioned assumptions, known-output regression, semantic/provenance review. |
| Optimizer | Constraint/feasibility/fallback regression, deterministic repeatability, provenance review. |

No gate may be satisfied with fabricated data, unavailable-source claims, or unrecorded manual changes. Normal CI uses fixtures/mocks and never requires external credentials.
