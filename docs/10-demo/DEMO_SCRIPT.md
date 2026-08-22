# INDRA — Demo Script

> **STATUS: FROZEN FOR PHASE 1 IMPLEMENTATION**
>
> Demonstration structure for Phase 1 submission. Do not fabricate final numerical results — numbers come from the running system at demo time.

> **Step 8C status:** COMPLETE. The event submission path now runs the persisted event pipeline and maps returned risk, scenario, procurement, and evidence stages into the existing dashboard. Step 8B remains PARTIAL; do not claim unavailable live source access.

> **Step 10A freeze:** The demo uses the verified root-path FastAPI contract,
> seeded PostgreSQL, deterministic Phase-1 engines, and explicit semantic /
> unavailable states. Step 8D-B is NOT STARTED.

> **Step 10C support:** See [PRESENTATION_STORY.md](PRESENTATION_STORY.md) for
> the judge-facing narrative and [TECHNICAL_EVIDENCE.md](TECHNICAL_EVIDENCE.md)
> for verified implementation/test claims.

---

## Demo Objective

Demonstrate one complete, traceable decision loop:

**Event → Risk → Scenario → Procurement → SPR → Evidence**

in 3–5 minutes. Everything must be explainable and traceable to a data source.

## Primary Reproducible Scenario — Hormuz Disruption

Use the existing seeded PostgreSQL database and the verified E2E event payload.
This is a controlled demonstration input, not a claim about a live event:

```json
{
  "title": "Houthi attack on Red Sea shipping",
  "event_type": "ATTACK",
  "severity": 7,
  "country_names": ["India", "Iraq", "Atlantis"],
  "corridor_names": ["Strait of Hurmuz", "Red Sea"],
  "route_names": [],
  "confidence": 0.85
}
```

The payload deliberately includes the verified fuzzy-resolvable spelling
`Strait of Hurmuz` and the unresolved control value `Atlantis`. The event is
submitted through the existing `POST /events` contract in Swagger at
`http://localhost:8000/docs`; it is not presented as live external news.

The dashboard then visualizes the same decision context using the existing
seeded corridor, network, scenario, reserve, and procurement panels. The
dashboard's **Ingest & Process** control may also be shown with a local manual
description, but without an LLM credential its extraction stage is explicitly
skipped; do not describe that fallback as live LLM extraction.

### Reproducible setup

```powershell
docker compose up -d postgres
$env:DATABASE_URL = "postgresql+asyncpg://indra_user:<development_password>@localhost:5432/indra_db"
python scripts/db/reset_db.py --confirm
python scripts/db/check_db.py
```

Start the backend and frontend using `docs/DEPLOYMENT.md`, then open:

- Swagger: `http://localhost:8000/docs`
- Dashboard: `http://localhost:3000`

No EIA, ACLED, or live LLM credential is required for this walkthrough.

### Semantic labels used in the walkthrough

| Stage | Label | Meaning in this demo |
|---|---|---|
| Controlled event payload | `SIMULATED` | Demonstration input; not a live external alert |
| Seeded corridor/reference records | `OBSERVED` | Persisted reference observations as exposed by the API |
| Structured contract and entity resolution | `DERIVED` | Schema validation and name-to-entity mapping |
| Risk, network impact, procurement, evidence path | `DERIVED` | Deterministic calculations and provenance assembly |
| Scenario duration/reduction inputs | `ASSUMED` | User-selected modeling assumptions |
| Scenario result | `DERIVED` | Reproducible output from the assumptions and seeded parameters |

Do not relabel the controlled event as `OBSERVED`, and do not describe the
scenario result as a measured future event.

### Exact judge walkthrough actions

1. Open the dashboard and confirm API status is connected.
2. Open Swagger `/docs`, execute `POST /events` with the JSON payload above.
3. Show the resolved countries/corridors, unresolved `Atlantis`, and evidence stages.
4. Return to the dashboard and refresh; show corridor risk, recent events, reserve availability, and the reference network panel.
5. In the scenario simulator, leave Horizon at **30 days** and Disruption at **100%**, then click **Run demo scenario**.
6. Point to the **7.056 MMT** derived supply gap and its semantic label.
7. Point to the procurement panel's feasible target and `DERIVED` label.
8. In Swagger, optionally execute `GET /corridors/1/impact` and `POST /recommendations` to show detailed network/procurement payloads.
9. Close on the evidence trail and explain which values are simulated input, assumptions, observed seed data, and derived output.

---

## Target Duration: 4 Minutes

### [00:00–00:30] Problem Context

**What to say:**

> "India imports 88% of its crude oil. 42% transits the Strait of Hormuz. Strategic petroleum reserves last approximately 9.5 days — the IEA recommends 90. When geopolitical events disrupt these routes, India's oil companies and government have no integrated system to detect the risk, model the downstream impact on specific refineries, and generate actionable procurement alternatives. This is INDRA — India Disruption Response Architecture."

**What to show:**
- INDRA landing page / risk overview dashboard
- Corridor risk cards visible

---

### [00:30–01:15] Controlled Event Submission and Resolution

**What to say:**

> "For this reproducible demo I am submitting a controlled event payload through INDRA's validated structured-event contract. It is not a live external alert. The system resolves known names, fuzzy-matches the Hormuz spelling, and retains the unknown entity instead of fabricating a match."

**What to show:**
- Swagger `POST /events` response
- Dashboard recent-event panel after refresh
- Resolution and evidence fields in the response

**What to prove:**
- Structured event schema is validated
- `India` and `Iraq` resolve as countries
- `Strait of Hurmuz` fuzzy-resolves to Strait of Hormuz
- `Red Sea` resolves as a corridor
- `Atlantis` remains unresolved
- Evidence includes source and extraction/structured-event stages

**Step 8C verified event-submission path:** The dashboard's **Ingest & Process** action accepts an event description of at least 20 characters and persists a local manual event. With a configured provider it runs extraction; without one it returns an explicit no-provider stage. The structured `POST /events` walkthrough above is the credential-free proof of entity resolution and evidence-contract behavior.

For a no-key demo, use the explicit fallback path and describe extraction as unavailable rather than pretending an external LLM response occurred. The deterministic engines and evidence output remain testable.

---

### [01:15–01:45] Corridor and Network Impact

**What to say:**

> "The dashboard shows the seeded India supply-network topology. NetworkX is used for traversal and impact analysis; it is not a live tanker map and it does not replace PostgreSQL."

**What to show:**
- India supply network reference panel
- Supplier → route → port → refinery counts
- `GET /corridors/1/impact` in Swagger to show affected routes/refineries
- Corridor risk panel showing Hormuz at 60/100, HIGH, OBSERVED

**What NOT to say:**
- Do not claim "live tanker tracking" unless real AIS data is available

---

### [01:45–02:45] Deterministic Scenario Simulation

**What to say:**

> "Now I will run the seeded Hormuz full-closure scenario for 30 days with a 100% reduction assumption."

[Click Run Scenario]

> "The deterministic scenario engine calculates a 7.056 MMT modeled supply gap. The result is DERIVED; the 100% disruption and 30-day duration are explicit scenario assumptions. Reserve fill level is not fabricated when it is unavailable."

**What to show:**
- Scenario simulator with parameter inputs
- Results panel with modeled supply gap and semantic label
- "All modeled values are DERIVED with ASSUMED / HISTORICAL_CALIBRATED inputs" label visible

**What to prove:**
- Numbers change when parameters change (demonstrate by adjusting severity)
- Results are deterministic and use the documented seed/calibration assumptions; EIA live data is not required
- Calculation is deterministic (not LLM-generated)

---

### [02:45–03:30] Procurement Recommendation

**What to say:**

> "The procurement engine uses SciPy LP when candidate identity and numerical constraints are complete, with deterministic ranking fallback. The dashboard's seeded demo candidate is compatible, operational, and unsanctioned, so the 1 MMT target is feasible."

**What to show:**
- Procurement recommendation panel
- Feasible target, unmet volume, and DERIVED semantic label
- Optional Swagger `POST /recommendations` response for full allocation details

> "The recommendation is a modeled decision output, not a live quote. Sanctioned, disrupted, non-operational, or incompatible candidates are excluded when those fields are present."

**What to prove:**
- Recommendation feasibility responds to target/candidate constraints
- Sanctions-blocked suppliers are excluded
- Incompatible crude grades are filtered out
- Scoring breakdown is visible for each option

---

### [03:30–04:00] Evidence Trail + Close

**What to say:**

> "Every recommendation in INDRA is traceable. This demo input is controlled, not a live alert. The event contract shows resolution evidence; the risk score is calculated from visible weighted components; the supply impact is modeled; and procurement is algorithmic."

**What to show:**
- Evidence drawer showing: source article → extracted event → risk contribution → scenario assumptions → recommendation

The event-processing result also exposes the machine-readable stages `source`, `extraction` (when a provider is configured), `entity_resolution`, `risk`, `scenario`, and `optimization` where their corresponding output exists. Do not present an omitted extraction stage as a live LLM result.

**Closing statement:**

> "INDRA combines optional external ingestion with India's seeded refinery and corridor network. In this credential-free walkthrough, the input is controlled and the output semantics are explicit. The system uses bounded LLM extraction when configured, a weighted deterministic risk engine, NetworkX impact traversal, SciPy LP with ranking fallback, and a parametric scenario engine."

---

## Demo Data Strategy

| Data Element | Source | Data Semantic |
|---|---|---|
| Geopolitical events | GDELT / ACLED adapters when available; seeded/manual fixtures otherwise | OBSERVED or SIMULATED |
| Crude prices | EIA adapter; unavailable without credentials | OBSERVED when ingested; otherwise unavailable |
| FX rates | RBI processed fallback path | OBSERVED or HISTORICAL_CALIBRATED |
| Sanctions | OFAC adapter/reference data | OBSERVED when ingested; otherwise unavailable |
| India refineries | PPAC historical seed | HISTORICAL_CALIBRATED |
| SPR capacity | ISPRL public | OBSERVED / HISTORICAL_CALIBRATED |
| Route risk scores | Weighted risk engine | DERIVED |
| Scenario results | Parametric scenario engine | DERIVED (assumptions tagged ASSUMED/HISTORICAL_CALIBRATED) |
| Procurement result | SciPy LP / deterministic ranking fallback | DERIVED |
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
| "Did you train any model?" | "No. Phase 1 uses a weighted deterministic risk engine. Step 8D-B is NOT STARTED because defensible historical disruption labels are unavailable." |
| "The AI is just calling an LLM?" | "When configured, the LLM handles bounded event extraction. Risk scoring uses deterministic formulas, procurement uses SciPy LP with deterministic ranking fallback, and scenarios use parametric models." |
| "How is this different from Bloomberg?" | "Bloomberg provides raw data and news. INDRA connects geopolitical disruption to India-specific refinery constraints and procurement actions — the compatibility matrix, SPR integration, and procurement optimization layer don't exist in Bloomberg." |
| "Are these numbers real?" | "The dashboard identifies whether inputs are observed, historical-calibrated, simulated, or unavailable. Risk scores, supply gaps, and procurement results are calculated and labeled DERIVED; scenario parameters retain ASSUMED or HISTORICAL_CALIBRATED provenance." |
### Step 6C MVP demo path

Open the Vite console, confirm backend status, review corridor risk and recent-event availability, click **Run demo flow**, then inspect the derived risk score, 30-day Hormuz scenario supply gap, procurement feasibility, and evidence chain. Values are fetched from FastAPI; missing observations are explicitly labeled.

### Step 7A readiness

The scripted API verification has completed successfully against the real seeded PostgreSQL database. The demo path is regression-checked; Step 7B presentation polish is complete and Step 7C is not started.

### Step 7B presentation notes

Use the polished console in a desktop/laptop viewport. Start by confirming the API status badge, scan the corridor risk bars, then adjust the scenario horizon/disruption controls before clicking **Run demo scenario**. Point out the semantic labels and numbered evidence trail; loading, empty, and retry states are intentionally visible when data is unavailable.

### Step 7C demo freeze

The release candidate has been verified from a clean PostgreSQL reset/seed through FastAPI and Vite startup. The reproducible command sequence is: `docker compose up -d postgres`; set `DATABASE_URL`; `python scripts/db/reset_db.py --confirm`; `python scripts/db/check_db.py`; start FastAPI on port 8000; start Vite on port 3000; open the console; confirm API status; run the scenario; inspect risk, supply gap, procurement, and evidence. At that historical release-checkpoint, Step 8 had not started; Step 8C is now complete and Step 8B remains partial.
