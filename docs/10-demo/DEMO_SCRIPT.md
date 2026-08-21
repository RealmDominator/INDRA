# INDRA — Demo Script

> **STATUS: FROZEN FOR PHASE 1 IMPLEMENTATION**
>
> Demonstration structure for Phase 1 submission. Do not fabricate final numerical results — numbers come from the running system at demo time.

---

## Demo Objective

Demonstrate one complete, traceable decision loop:

**Event → Risk → Scenario → Procurement → SPR → Evidence**

in 3–5 minutes. Everything must be explainable and traceable to a data source.

---

## Target Duration: 4 Minutes

### [00:00–00:30] Problem Context

**What to say:**

> "India imports 88% of its crude oil. 42% transits the Strait of Hormuz. Strategic petroleum reserves last approximately 9.5 days — the IEA recommends 90. When geopolitical events disrupt these routes, India's oil companies and government have no integrated system to detect the risk, model the downstream impact on specific refineries, and generate actionable procurement alternatives. This is INDRA — India Disruption Response Architecture."

**What to show:**
- INDRA landing page / risk overview dashboard
- Corridor risk cards visible

---

### [00:30–01:15] Live Event Detection

**What to say:**

> "INDRA monitors GDELT, ACLED, and other free geopolitical data sources. Here — the system detected this event [X minutes ago], classified it as a [EVENT_TYPE] event near [LOCATION] with severity [X], and automatically updated the corridor risk score."

**What to show:**
- Event feed panel with recent classified events
- Risk score changing on the risk dashboard
- Click one event → show LLM-extracted structured data

**What to prove:**
- Events come from real data sources (show source URL)
- Classification is LLM-powered but validated
- Risk update is immediate and explainable

---

### [01:15–01:45] India Supply Network Map

**What to say:**

> "This map shows India's crude oil supply network — [N] refineries, major ports, 3 strategic reserve locations, chokepoints, and supply routes. Routes are colored by current risk. Click on any element for details."

**What to show:**
- Leaflet map with India supply network
- Refineries, ports, SPR markers
- Route lines colored by risk (green→red gradient)
- Click a route → show risk score + evidence

**What NOT to say:**
- Do not claim "live tanker tracking" unless real AIS data is available

---

### [01:45–02:45] Scenario Simulation

**What to say:**

> "Now I'll run a disruption scenario: Hormuz [50% / 100%] closure for 30 days."

[Click Run Scenario]

> "Within seconds, INDRA calculates: India loses approximately [X] MMT of crude over 30 days. Current SPR covers [X] days. After day [X], affected refineries fall below optimal feed rate. The estimated additional import cost is $[X] billion. Freight costs spike [X]x on Cape of Good Hope rerouting."

**What to show:**
- Scenario simulator with parameter inputs
- Results panel with supply gap, days-to-critical, cost impact, affected refineries
- "All values are ESTIMATED / DERIVED" label visible

**What to prove:**
- Numbers change when parameters change (demonstrate by adjusting severity)
- Results are derived from real PPAC/EIA-calibrated data
- Calculation is deterministic (not LLM-generated)

---

### [02:45–03:30] Procurement Recommendations

**What to say:**

> "For [Refinery Name], the optimization engine ranks alternative crude procurement options based on compatibility, route risk, transit time, cost, and sanctions compliance."

**What to show:**
- Procurement recommendation table for a specific refinery
- Ranked alternatives with all scoring factors visible

> "Notice: [Example — Russian Urals ranked lower because Cape-routed freight adds $X/barrel and shadow fleet risk is elevated. Arab Light via Cape is ranked higher — higher base price but lower total risk and cost premium.]"

**What to prove:**
- Recommendations change when scenario changes (demonstrate)
- Sanctions-blocked suppliers are excluded
- Incompatible crude grades are filtered out
- Scoring breakdown is visible for each option

---

### [03:30–04:00] Evidence Trail + Close

**What to say:**

> "Every recommendation in INDRA is traceable. The event is real — here is the source. The risk score is calculated — here are the components and weights. The supply impact is modelled — here are the assumptions. The procurement ranking is algorithmic — here is the scoring."

**What to show:**
- Evidence drawer showing: source article → extracted event → risk contribution → scenario assumptions → recommendation

**Closing statement:**

> "INDRA integrates real geopolitical intelligence from GDELT, ACLED, and OFAC with India's actual refinery network, PPAC import data, and ISPRL strategic reserves. It uses LLM-based extraction for news intelligence, [optimization method] for procurement optimization, and a parametric scenario engine calibrated on historical disruption data. Every recommendation is traceable to a source event."

---

## Demo Data Strategy

| Data Element | Source | Data Semantic |
|---|---|---|
| Geopolitical events | GDELT / ACLED (when available) | OBSERVED |
| Crude prices | EIA API | OBSERVED |
| FX rates | RBI (or fallback) | OBSERVED / HISTORICAL_CALIBRATED |
| Sanctions | OFAC | OBSERVED |
| India refineries | PPAC historical seed | HISTORICAL_CALIBRATED |
| SPR capacity | ISPRL public | OBSERVED / HISTORICAL_CALIBRATED |
| Route risk scores | Weighted risk engine | DERIVED |
| Scenario results | Parametric scenario engine | DERIVED (assumptions tagged ASSUMED/HISTORICAL_CALIBRATED) |
| Procurement ranking | LP / deterministic ranking | DERIVED |
| Demo fixtures | Pre-loaded events | SIMULATED |

---

## Fallback Plan

If live data sources fail during demo:

1. **Activate demo mode** — Pre-loaded fixture events that demonstrate the full chain
2. **Show "DEMO MODE" banner** — Never hide that fixture data is being used
3. **All calculations still run on fixture data** — The chain is real even if the input event is pre-loaded

---

## Questions Judges May Ask

| Question | Honest Answer |
|---|---|
| "Is this real-time AIS data?" | "No. We use historical route baselines and are explicit about this in the UI." |
| "Did you train any model?" | "Phase 1 uses a weighted deterministic risk engine — every component is visible and explainable. Training a custom ML model from scratch in 4 days would not produce reliable enough labels to be defensible. The architecture is ML-ready: a Phase 2 XGBoost disruption-probability model is the documented next step, using ACLED/EIA historical data." |
| "The AI is just calling an LLM?" | "The LLM handles event extraction from unstructured text — what it's good at. Risk scoring uses deterministic formulas, procurement uses LP optimization, scenarios use parametric models. The hybrid approach is more reliable than 'LLM does everything.'" |
| "How is this different from Bloomberg?" | "Bloomberg provides raw data and news. INDRA connects geopolitical disruption to India-specific refinery constraints and procurement actions — the compatibility matrix, SPR integration, and procurement optimization layer don't exist in Bloomberg." |
| "Are these numbers real?" | "Events come from GDELT/ACLED/OFAC. Refinery data from PPAC. SPR data from ISPRL. Risk scores, supply gaps, and procurement rankings are calculated — labeled as DERIVED. Scenario impacts are modelled — labeled as ESTIMATED." |
### Step 6C MVP demo path

Open the Vite console, confirm backend status, review corridor risk and recent-event availability, click **Run demo flow**, then inspect the derived risk score, 30-day Hormuz scenario supply gap, procurement feasibility, and evidence chain. Values are fetched from FastAPI; missing observations are explicitly labeled.
