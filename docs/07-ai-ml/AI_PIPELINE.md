# INDRA — AI Pipeline

> Source: PETRAS Analysis §10, §11; INDRA Master Report §5
>
> **Revision:** Post-review corrections. Added explicit entity resolution layer, provenance tracking, and risk scale convention.

---

## Pipeline Overview

INDRA uses a **hybrid AI architecture** where the LLM handles what it is good at (unstructured text processing) and deterministic systems handle what they are good at (numerical computation, optimization, scenario propagation).

```
NEWS ARTICLE (GDELT, ACLED, NewsAPI, RSS)
        ↓
LLM CALL (abstracted provider)
        ↓
STRUCTURED EVENT OBJECT (JSON — human-readable names, NOT database IDs)
        ↓
POST-LLM VALIDATION (enum, range, schema)
        ↓
ENTITY RESOLUTION (names → internal IDs via entity_aliases + RapidFuzz)
        ↓
DATABASE INSERTION (with provenance evidence record)
        ↓
RISK SCORE UPDATE (deterministic formula, 0.0–1.0 internal)
        ↓
ALERT (if risk_delta > threshold)
        ↓
SCENARIO ENGINE (parametric, deterministic)
        ↓
OPTIMIZATION (scipy LP or ranking)
        ↓
RECOMMENDATION GENERATION (optional LLM for natural language explanation)
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
- severity: [1–10 integer]
- country_names: [list of country names]
- corridor_names: [HORMUZ | RED_SEA | SUEZ | MALACCA | RUSSIA | NONE]
- entity_names: [list of organizations, companies, groups]
- confidence: [0.0–1.0]

Return JSON only.
```

> **CRITICAL: The LLM must NOT produce database IDs.** It outputs human-readable names and codes. The entity resolution layer (Step 2) maps these to internal IDs.

### Expected LLM Output

```json
{
  "event_type": "SANCTION",
  "severity": 6,
  "country_names": ["Iran"],
  "corridor_names": ["HORMUZ"],
  "entity_names": ["OFAC", "Iranian tanker fleet"],
  "confidence": 0.91
}
```

> **Severity convention:** The LLM outputs severity as a 1–10 integer for reliability. The entity resolution layer normalizes this to 0.0–1.0 internal scale: `internal_severity = llm_severity / 10.0`.

### Post-LLM Validation Rules

After the LLM returns structured output, apply these deterministic validation rules:

1. Is the JSON well-formed and matches the Pydantic schema?
2. Is `event_type` one of the allowed enum values?
3. Is `severity` within 1–10 range?
4. Is `confidence` within 0.0–1.0 range?
5. Is the event within the last 30 days? (reject stale events)
6. Is `confidence > 0.6`? (reject low-confidence extractions)

Events that fail validation are logged but NOT inserted into the risk calculation.

### LLM Call Configuration

- **Temperature:** 0 (or as close to 0 as the provider allows) — structured extraction requires determinism
- **Max tokens:** ~200 (structured JSON is compact)
- **System prompt:** Define role as "geopolitical event extractor for India energy supply chain"
- **Response format:** JSON mode where supported by the provider
- **Timeout:** 15 seconds. Skip article on timeout.
- **Retries:** Max 2 retries on malformed JSON. If still malformed after retries, skip and log.

---

## Step 2: Entity Resolution

### Purpose
Map LLM-output human-readable names to internal database entity IDs.

### Data Flow

```
LLM output (human-readable)           Entity resolution              Database (internal IDs)
─────────────────────────           ──────────────────             ──────────────────────

"country_names": ["Iran"]      →   entity_aliases lookup      →   affected_country_ids: [7]
"corridor_names": ["HORMUZ"]   →   entity_aliases lookup      →   affected_corridor_ids: [1]
"entity_names": ["Aramco"]     →   RapidFuzz fuzzy match      →   supplier_id: 3
```

### Resolution Process

1. **Exact match** against `entity_aliases` table (alias → canonical_entity_type + canonical_entity_id)
2. **Fuzzy match** via RapidFuzz (threshold ≥ 85% similarity) against entity_aliases if no exact match
3. **Corridor code match** — corridor_names like "HORMUZ" matched against `corridors.code`
4. **Unresolved fallback** — log unresolved entity; do NOT insert unresolved references into foreign key columns. The event is still stored but with the unresolved entity name in a `raw_entities` field for later review.

### Phase 1 Scope

- Pre-populate ~50–100 aliases in `entity_aliases` table covering key entities:
  - ~30 country name variants
  - ~10 corridor/chokepoint name variants
  - ~15 supplier/company name variants
  - ~10 crude grade name variants
- Deterministic mapping first; fuzzy matching as fallback
- No embeddings or vector databases

### Provenance

Every entity resolution step creates an `evidence_records` entry:
```json
{
  "evidence_type": "ENTITY_RESOLUTION",
  "input_summary": {"raw_name": "Saudi Aramco", "match_type": "FUZZY", "score": 0.92},
  "output_summary": {"canonical_type": "supplier", "canonical_id": 3, "canonical_name": "Saudi Arabian Oil Company"},
  "data_semantic": "DERIVED"
}
```

---

## Step 3: Risk Score Update

### Method
Deterministic weighted formula. **NOT an LLM output.** All scores computed on 0.0–1.0 internal scale.

See [ML_MODEL.md](ML_MODEL.md) for risk engine details.

### Provenance

Every risk score update creates an `evidence_records` entry:
```json
{
  "evidence_type": "RISK_CALCULATION",
  "model_or_method": "weighted_rule_v1",
  "input_summary": {"corridor": "HORMUZ", "contributing_events": [42, 43], "weights": {...}},
  "output_summary": {"score": 0.78, "risk_level": "CRITICAL"},
  "data_semantic": "DERIVED"
}
```

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
  "risk_score_display": 78,
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

> "Hormuz exposure has raised the route risk to CRITICAL (78/100). BPCL Kochi is projected to face a supply shortfall within 22 days. The system ranks Arab Light from Saudi Arabia via Cape of Good Hope first because it meets compatibility constraints, avoids the affected corridor, and has the lowest estimated landed-cost penalty at +$3.50/bbl. SPR at Padur can bridge approximately 5.7 days of the projected gap."

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
| Produce database IDs | ❌ NO | Entity resolution layer |

---

## Application LLM Abstraction Requirement

INDRA must NOT hard-code any specific LLM provider. The LLM integration must use a provider abstraction layer:

```python
# Conceptual interface — not implemented yet
class LLMProvider(ABC):
    @abstractmethod
    async def extract_event(self, article_text: str) -> StructuredEvent:
        """Extract structured event from news article text.
        Returns human-readable names, NOT database IDs."""
        pass

    @abstractmethod
    async def generate_explanation(self, structured_results: dict) -> str:
        """Generate natural language explanation from computed results."""
        pass

    @abstractmethod
    def get_model_info(self) -> dict:
        """Return model name, provider, version for evidence trail."""
        pass
```

**Required configuration:**
- `max_retries: int = 2` — retry on malformed JSON
- `timeout_seconds: int = 15` — skip article on timeout
- `fallback_provider: Optional[LLMProvider]` — cheaper/faster model if primary fails

Concrete implementations would exist for:
- OpenAI (GPT-4o-mini, etc.)
- Anthropic (Claude Haiku, etc.)
- Google (Gemini Flash, etc.)
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
