# INDRA — ML Model Strategy

> Source: PETRAS Analysis §10; INDRA Master Report §5, §18, §19

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

The risk engine calculates a composite score from observable features using a deterministic weighted formula.

> **CONFLICT: Two different weight schemes exist in the research reports.**
>
> **PETRAS Report (§10):**
> ```
> risk = 0.35×country_risk + 0.25×event_impact + 0.20×sanctions + 0.10×weather + 0.10×chokepoint
> ```
>
> **INDRA Master Report (§5.2):**
> ```
> risk = 0.25×event_severity + 0.20×event_recency + 0.20×chokepoint_exposure
>      + 0.15×conflict_sanctions + 0.10×historical_rate + 0.10×india_dependency
> ```
>
> **Resolution:** Both are reasonable starting points. The implementing agent should choose one, document it, and calibrate against historical disruption data. The architecture must allow weight adjustment without code changes (configuration-driven weights).

### Phase 1 Risk Classification

```
0–29   LOW
30–49  MODERATE
50–69  HIGH
70–84  CRITICAL
85–100 EXTREME
```

### Evidence Requirement

Every risk score must expose its component breakdown:

```json
{
  "corridor": "Hormuz",
  "risk_score": 78,
  "risk_level": "CRITICAL",
  "components": [
    {"factor": "event_severity", "value": 82, "weight": 0.25},
    {"factor": "chokepoint_exposure", "value": 90, "weight": 0.20},
    {"factor": "india_dependency", "value": 42, "weight": 0.10}
  ],
  "confidence": 0.72
}
```

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
country_risk        — Base risk for origin country
recent_events_7d    — ACLED/GDELT event count in corridor
active_sanctions    — Sanctions changes affecting corridor suppliers
weather_alert       — Active weather warnings on route
chokepoint_factor   — Chokepoint proximity and dependency
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
