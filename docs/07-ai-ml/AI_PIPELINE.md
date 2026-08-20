# INDRA — AI Pipeline

> Source: PETRAS Analysis §10, §11; INDRA Master Report §5

---

## Pipeline Overview

INDRA uses a **hybrid AI architecture** where the LLM handles what it is good at (unstructured text processing) and deterministic systems handle what they are good at (numerical computation, optimization, scenario propagation).

```
NEWS ARTICLE (GDELT, ACLED, NewsAPI, RSS)
        ↓
LLM CALL (abstracted provider)
        ↓
STRUCTURED EVENT OBJECT (JSON)
        ↓
RULE-BASED VALIDATION
        ↓
DATABASE INSERTION
        ↓
RISK SCORE UPDATE (deterministic formula)
        ↓
ALERT (if risk_delta > threshold)
        ↓
SCENARIO ENGINE (parametric, deterministic)
        ↓
OPTIMIZATION (scipy LP or ranking)
        ↓
RECOMMENDATION GENERATION (LLM for natural language explanation)
        ↓
DASHBOARD UPDATE
```

---

## Step 1: LLM Event Extraction

### Purpose
Convert unstructured news article text into structured event data.

### Input
Raw text from a news article, RSS feed item, or GDELT event description.

### LLM Prompt Structure (Conceptual)

```
Extract from this news article:
- event_type: [SANCTION | MILITARY | PORT_CLOSURE | ATTACK | DIPLOMATIC | OTHER]
- severity: [0.0–1.0]
- affected_countries: [list of country names]
- affected_chokepoints: [HORMUZ | RED_SEA | SUEZ | MALACCA | NONE]
- affected_companies: [list]
- confidence: [0.0–1.0]

Return JSON only.
```

> **NOTE on severity scale:** PETRAS report uses 0.0–1.0 float. INDRA Master report examples show integer severity (e.g., `"severity": 4`). This conflict is unresolved. The implementing agent should choose one scale and use it consistently. The prompt template will be finalized during implementation.

### Expected Output

```json
{
  "event_type": "SANCTION",
  "severity": 0.6,
  "affected_countries": ["Iran"],
  "affected_chokepoints": ["HORMUZ"],
  "affected_companies": ["OFAC", "Iranian tanker fleet"],
  "confidence": 0.91
}
```

### Validation Rules (Post-LLM)

After the LLM returns structured output, apply these deterministic validation rules:

1. Is the event within the last 30 days? (reject stale events)
2. Is confidence > 0.6? (reject low-confidence extractions)
3. Is the affected country in INDRA's tracked country list?
4. Is the event_type one of the allowed enum values?
5. Is severity within the valid range?
6. Does the JSON conform to the Pydantic schema?

Events that fail validation are logged but NOT inserted into the risk calculation.

### LLM Call Configuration

- **Temperature:** 0 (or as close to 0 as the provider allows) — structured extraction requires determinism
- **Max tokens:** ~200 (structured JSON is compact)
- **System prompt:** Define role as "geopolitical event extractor for India energy supply chain"
- **Response format:** JSON mode where supported by the provider

---

## Step 2: Entity Normalization

### Purpose
Resolve entity variants to canonical forms.

### Method
Phase 1: Rule-based lookup table + RapidFuzz for fuzzy matching.

| Input Variant | Canonical Entity |
|---|---|
| "Saudi Aramco" | Saudi Arabian Oil Company |
| "Saudi Arabian Oil Co." | Saudi Arabian Oil Company |
| "Aramco" | Saudi Arabian Oil Company |
| "IRGC" | Islamic Revolutionary Guard Corps (Iran) |
| "Hormuz" | Strait of Hormuz |
| "Strait of Hurmuz" | Strait of Hormuz |

> **PETRAS report recommendation:** Pre-build a static knowledge base of ~50 key entities rather than attempting dynamic entity resolution. Full entity resolution is a months-long engineering effort.

---

## Step 3: Risk Score Update

### Method
Deterministic weighted formula. **NOT an LLM output.**

See [ML_MODEL.md](ML_MODEL.md) for risk engine details.

---

## Step 4: Recommendation Explanation (Second LLM Call)

### Purpose
After all calculations are complete, generate a human-readable action brief.

### Input to LLM
Only structured, validated results from the scenario engine and procurement optimizer:

```json
{
  "corridor": "Hormuz",
  "risk_level": "CRITICAL",
  "scenario": "50% closure, 30 days",
  "supply_gap_mmt": 7.06,
  "most_exposed_refinery": "BPCL Kochi",
  "top_alternative": {
    "grade": "Arab Light",
    "origin": "Saudi Arabia",
    "route": "Cape of Good Hope",
    "cost_premium": "+$3.50/bbl"
  },
  "spr_bridge_days": 5.7
}
```

### Expected LLM Output

> "Hormuz exposure has raised the route risk to CRITICAL. BPCL Kochi is projected to face a supply shortfall within 22 days. The system ranks Arab Light from Saudi Arabia via Cape of Good Hope first because it meets compatibility constraints, avoids the affected corridor, and has the lowest estimated landed-cost penalty at +$3.50/bbl. SPR at Padur can bridge approximately 5.7 days of the projected gap."

### Critical Constraint

The LLM must **NOT invent** prices, transit times, stock levels, optimization results, or any numerical values. It receives only pre-computed results and turns them into prose.

---

## LLM Boundaries — What the LLM Must NOT Do

| Task | LLM Allowed? | Correct Approach |
|---|---|---|
| Extract event structure from news text | ✅ YES | LLM with structured output |
| Generate natural language explanation | ✅ YES | LLM with pre-computed inputs only |
| Compute risk scores | ❌ NO | Deterministic weighted formula |
| Make procurement decisions | ❌ NO | LP optimization / ranking algorithm |
| Calculate supply gaps | ❌ NO | Parametric arithmetic |
| Simulate disruption scenarios | ❌ NO | Deterministic propagation engine |
| Generate crude oil prices | ❌ NO | EIA API data |
| Predict future events | ❌ NO | Not reliable; hallucination risk |
| Assess sanctions compliance | ❌ NO | Rule-based OFAC lookup |
| Calculate freight/insurance costs | ❌ NO | Parametric formulas with historical calibration |

---

## Application LLM Abstraction Requirement

INDRA must NOT hard-code any specific LLM provider. The LLM integration must use a provider abstraction layer:

```python
# Conceptual interface — not implemented yet
class LLMProvider:
    def extract_event(self, article_text: str) -> StructuredEvent:
        """Extract structured event from news article text."""
        raise NotImplementedError

    def generate_explanation(self, structured_results: dict) -> str:
        """Generate natural language explanation from computed results."""
        raise NotImplementedError
```

Concrete implementations would exist for:
- OpenAI (GPT-4o-mini, etc.)
- Anthropic (Claude Haiku, etc.)
- Google (Gemini, etc.)
- Local models
- Others as evaluated

The actual application LLM will be selected through a controlled benchmark. See [AI_MODEL_STRATEGY.md](AI_MODEL_STRATEGY.md).

---

## Cost Estimate for Demo

| Metric | Value |
|---|---|
| Average article | ~500 tokens in, ~100 tokens out |
| Cost per article (GPT-4o-mini tier) | ~$0.0002 |
| 1,000 articles total | ~$0.20 |
| Explanation generation | ~$0.001 per explanation |

Essentially free for demo purposes with any major provider.
