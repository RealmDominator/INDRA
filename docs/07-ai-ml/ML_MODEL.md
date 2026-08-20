# INDRA — ML Model Strategy

> Source: PETRAS Analysis §10; INDRA Master Report §5, §18, §19
>
> **Revision:** Post-review corrections. Risk scale frozen to 0.0–1.0 internal / 0–100 display. Weight conflict resolved.
>
> **Phase boundary (frozen):**
> - **Phase 1:** Weighted deterministic risk engine — explainable, no training required
> - **Phase 2 candidate:** XGBoost disruption-probability model — NOT implemented in Phase 1

---

## Phase 1 ML Reality

A meaningful ML model cannot be trained from scratch in 4 days while also building a full-stack application. The research reports converge on this conclusion:

- **PETRAS:** Lists XGBoost disruption classifier as "NICE TO HAVE" — only if time permits, very last priority
- **INDRA Master:** Explicitly defers custom ML to Phase 2; states that "four-day Phase-1 development does not provide enough reliable labels to justify custom ML training"

**Phase 1 decision: Weighted rule-based scoring. Architecture must be ML-ready.**

---

## Risk Model

### Objective
Score corridors, routes, and suppliers on a risk scale so that procurement decisions can account for geopolitical risk.

### Phase 1: Weighted Rule-Based Engine

The risk engine calculates a composite score from observable features using a deterministic weighted formula. All component inputs and the output score are on the **0.0–1.0 internal scale**.

> **RESOLVED CONFLICT: Two weight schemes in research reports.**
>
> **Default weights (derived from INDRA Master Report §5.2):**
> ```
> risk = 0.25×event_severity + 0.20×event_recency + 0.20×chokepoint_exposure
>      + 0.15×conflict_sanctions + 0.10×historical_rate + 0.10×india_dependency
> ```
>
> **Alternative weights (from PETRAS Report §10):**
> ```
> risk = 0.35×country_risk + 0.25×event_impact + 0.20×sanctions + 0.10×weather + 0.10×chokepoint
> ```
>
> **Resolution:** The INDRA Master Report weights are the default because they include India-specific factors (india_dependency, chokepoint_exposure). All weights must be **configuration-driven** (stored in a config file or database table, not hardcoded). The implementing agent may calibrate against historical disruption data. Changing weights must not require code changes.

### Risk Scale Convention

> **FROZEN:** Internal = 0.0–1.0. Display = 0–100. Conversion: `display_score = internal_score × 100`.

### Phase 1 Risk Classification (on internal 0.0–1.0 scale)

```
0.00–0.29   LOW
0.30–0.49   MODERATE
0.50–0.69   HIGH
0.70–0.84   CRITICAL
0.85–1.00   EXTREME
```

### Evidence Requirement

Every risk score must expose its component breakdown:

```json
{
  "corridor_code": "HORMUZ",
  "corridor_name": "Strait of Hormuz",
  "risk_score": 0.78,
  "risk_level": "CRITICAL",
  "components": [
    {"factor": "event_severity", "value": 0.82, "weight": 0.25},
    {"factor": "chokepoint_exposure", "value": 0.90, "weight": 0.20},
    {"factor": "india_dependency", "value": 0.42, "weight": 0.10}
  ],
  "confidence": 0.72,
  "data_semantic": "DERIVED"
}
```

> **Note:** All values above are on the internal 0.0–1.0 scale. The API layer converts to 0–100 for display.

A risk score without explanation is meaningless and will be dismissed by judges.

---

## Phase 2: XGBoost Disruption Probability Model

### Objective
Binary classification: Did a disruption actually occur? (disruption = 1, no disruption = 0)

### Candidate Features

| Feature | Source | Type |
|---|---|---|
| ACLED event count in corridor (7-day window) | ACLED API | Numeric |
| ACLED event count (30-day window) | ACLED API | Numeric |
| GDELT tone/sentiment for corridor | GDELT | Numeric |
| Active sanctions count on corridor suppliers | OFAC | Numeric |
| Brent price 7-day change | EIA | Numeric |
| Historical disruption frequency (5-year) | Derived | Numeric |
| Country base risk score | Static reference | Numeric |
| Season / monsoon indicator | Derived | Categorical |

### Training Data Strategy

1. Use ACLED historical data (2019–2025) for Middle East / Horn of Africa regions
2. Label disruption events using EIA supply disruption records
3. Create binary labels: was there a measurable supply disruption within 7/14/30 days of the event cluster?
4. Expected dataset size: hundreds to low thousands of samples
5. Cross-validate with temporal splits (not random splits — time series data)

### Expected Performance

| Metric | Realistic Expectation |
|---|---|
| Accuracy | 65–75% on historical holdout |
| False positive rate | Moderate (many events don't cause disruptions) |
| False negative rate | Lower (real disruptions tend to have event signals) |

> **WARNING:** Do not overclaim accuracy. Do not fabricate evaluation metrics. Report actual evaluation results with confidence intervals.

### XGBoost Role

- Binary classifier with interpretable feature importances
- Fast training and inference
- Works with small datasets
- Handles mixed feature types

### SHAP Role

- Post-hoc explanation of XGBoost predictions
- Feature importance visualization
- Individual prediction explanation
- Only relevant when XGBoost model exists (Phase 2)

---

## ML-Ready Architecture

The risk engine must be implemented behind an interface that can accept either rules or a trained model:

```python
# Conceptual — not implemented
class RiskEngine:
    def score(self, corridor: str, features: dict) -> RiskResult:
        raise NotImplementedError

class WeightedRuleRiskEngine(RiskEngine):
    """Phase 1 implementation — deterministic weighted formula"""
    pass

class XGBoostRiskEngine(RiskEngine):
    """Phase 2 implementation — trained model with SHAP"""
    pass
```

This avoids architectural rework when transitioning from rules to ML.

---

## Route Risk Scoring

### Input Features
```
country_risk        — Base risk for origin country (0.0–1.0)
recent_events_7d    — ACLED/GDELT event count in corridor (normalized to 0.0–1.0)
active_sanctions    — Sanctions changes affecting corridor suppliers (0.0–1.0)
weather_alert       — Active weather warnings on route (0.0–1.0)
chokepoint_factor   — Chokepoint proximity and dependency (0.0–1.0, from corridors.india_dependency_share)
```

### Why Not ML for Route Risk?
No labeled ground truth for "route disruption = 1" exists at sufficient volume. The weighted formula is more defensible for Phase 1 because every component is visible and explainable to judges.

---

## Supply Gap Calculation

### Model
Deterministic arithmetic. No ML needed.

### Formula
```
supply_gap = (normal_import_rate × disruption_days × disruption_pct) - available_alternative_volume
```

This is transparent arithmetic — better for judges than a black-box prediction.

---

## Evaluation Requirements (for any ML model)

Before claiming any ML model result:

1. **Define evaluation dataset** — source, size, temporal range, label distribution
2. **Document evaluation methodology** — train/test split strategy, cross-validation approach
3. **Report actual metrics** — accuracy, precision, recall, F1 with confidence intervals
4. **Show confusion matrix** — not just a single accuracy number
5. **Show feature importance** — SHAP or XGBoost native importance
6. **Document failure cases** — what does the model get wrong?

---

## Fallback Strategy

| Component | Primary Approach | Fallback |
|---|---|---|
| Risk scoring | Weighted formula | Simple lookup table by corridor |
| Disruption probability | Rule-based threshold (Phase 1) | Static risk levels from historical data |
| Procurement ranking | LP optimization (scipy/PuLP) | Deterministic weighted ranking |
| Event extraction | LLM API call | Pre-parsed structured events from seed data |

---

## No Fabricated Metrics

The following claims require actual evidence:
- "87% accuracy" → show confusion matrix, dataset, evaluation code
- "Real-time prediction" → show actual latency measurements
- "AI-powered risk scoring" → show what the AI actually does vs what's deterministic
- "Trained on millions of samples" → show dataset provenance

Never fabricate ML evaluation metrics. Judges will ask probing questions.
