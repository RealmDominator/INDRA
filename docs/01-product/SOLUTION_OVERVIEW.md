# INDRA — Solution Overview

## Problem Statement

India's crude oil supply chain faces three structural vulnerabilities:

1. **Structural import dependency:** India imports ~88% of crude oil requirements. In FY2024-25, India imported approximately 232 million metric tonnes of crude (source: PPAC, ppac.gov.in).

2. **Geographic concentration:** 40–45% of India's crude imports transit the Strait of Hormuz. Middle Eastern suppliers (Saudi Arabia, Iraq, UAE, Kuwait) collectively supply 50–60% of India's crude. This creates a single-point-of-failure corridor.

3. **Reserve inadequacy:** India's Strategic Petroleum Reserves (SPR) at Visakhapatnam (1.33 MMT), Mangalore (1.5 MMT), and Padur (2.5 MMT) total ~5.33 MMT. At ~5 MMBbl/day consumption, this provides approximately 9.5 days of coverage against the IEA-recommended 90 days.

### Current Operational Reality

- Procurement teams at IOC, BPCL, HPCL manually track news via Bloomberg terminals and Reuters Eikon
- Risk signals are fragmented across analyst reports, news terminals, and internal briefings
- Rerouting decisions are made in committee with 48–72 hour lag
- No integrated system connects geopolitical news → shipping risk → refinery impact → reserve drawdown → procurement decision
- Trade desks operate on Excel models for supply gap estimation
- Strategic reserve drawdown decisions involve inter-ministerial committees with significant political considerations

## Target Users

| User | Organization | Decision Type |
|---|---|---|
| Crude procurement analysts | IOC, BPCL, HPCL | Monthly/quarterly procurement tenders |
| Refinery supply-chain teams | IOC, BPCL, HPCL, Reliance, MRPL | Emergency rerouting (ad hoc) |
| Policy/crisis-monitoring teams | MoPNG | Strategic planning, crisis coordination |
| Reserve planning teams | ISPRL | Reserve drawdown timing |
| Regulatory oversight | DGH | Sector-wide risk monitoring |

## Solution

INDRA (India Disruption Response Architecture) is an **India-specific energy supply-chain risk and procurement decision-support system** that converts geopolitical events into actionable procurement intelligence through a complete, explainable decision chain.

## Core Workflow

```
GEOPOLITICAL EVENT (e.g., IRGC seizes tanker near Hormuz)
        ↓
EVENT INGESTION (GDELT, ACLED, RSS, OFAC)
        ↓
LLM STRUCTURED EVENT EXTRACTION
        ↓
ENTITY RESOLUTION (rule-based + fuzzy matching)
        ↓
RISK CALCULATION (weighted explainable formula)
        ↓
SUPPLY-CHAIN IMPACT (graph propagation via NetworkX)
        ↓
SCENARIO SIMULATION (deterministic parametric engine)
        ↓
PROCUREMENT OPTIMIZATION (SciPy LP + deterministic ranking fallback)
        ↓
EVIDENCE TRAIL (source → event → risk → impact → recommendation)
        ↓
DASHBOARD (React + network visualization)
```

The dashboard is only the interface around this chain. The chain IS the product.

### Current implementation boundary

The Phase-1 chain is implemented and verified against seeded PostgreSQL. Risk,
scenario, and procurement calculations are deterministic; NetworkX performs
graph traversal and impact analysis only. The LLM provider is bounded to
structured extraction and is unavailable until credentials are configured, with
an explicit deterministic fallback. External ingestion adapters are present
but Step 8B remains PARTIAL because EIA/ACLED credentials and some live-source
completion are unavailable. XGBoost is a NOT STARTED Phase-2 candidate.

## Value Proposition

INDRA answers the question that existing global commodity platforms do not:

> **"Given this disruption, which Indian refinery is exposed, how large is the supply gap, which compatible crude alternatives are available, what is the estimated route/cost impact, and how much can the SPR bridge?"**

## Key Differentiators

### Real Gaps vs Global Platforms (Kpler, Vortexa, Windward)

| Differentiator | Why It Matters |
|---|---|
| **India-specific downstream propagation** | Global platforms track crude flows TO India but do not model which refinery is affected → which products are impacted → which reserves must compensate → what procurement gap exists |
| **Refinery-specific crude compatibility matrix** | Indian refineries are configured for specific crude grades (Jamnagar handles heavy sour; Panipat handles medium). No commercial platform models whether a substitute crude can actually be processed at a specific Indian refinery |
| **Indian public dataset integration** | PPAC, ISPRL, RBI, PPAC data integrated into a unified risk picture — no commercial platform does this |
| **Russian crude trade modeling** | India is the second-largest buyer of Russian Urals crude (~36-38% of imports). The discount structure and shadow fleet logistics create a unique India-specific risk profile |
| **Rupee/crude compound risk** | India's effective import cost = Brent × USD/INR. Simultaneous price spike + rupee depreciation creates compound risk that standard commodity tools ignore |

### Weak Differentiators (NOT used)

- "Indian UI" — not a real gap
- "Cheaper" — temporary, not defensible
- "Better AI" — unverifiable claim

## MVP Scope

See [MVP_SCOPE.md](MVP_SCOPE.md) for the complete feature classification.

**Summary:** The Phase-1 MVP must demonstrate one complete event → risk → scenario → procurement → evidence chain with real or clearly-labeled data sources.

## Out of Scope (Phase 1)

- Real-time AIS vessel tracking
- Satellite imagery analysis
- 3D digital twin visualization
- Kafka / Kubernetes / microservice complexity
- Neo4j graph database
- LSTM/Transformer price forecasting
- Reinforcement learning
- Large custom ML training pipeline
- Enterprise authentication / SAP integration
- Mobile application
- Paid commercial data feeds

These are documented in the roadmap as Phase 2/3 capabilities only.

## Success Criteria

INDRA Phase-1 is successful if the team can demonstrate ALL of the following:

1. A real geopolitical event is ingested (or a transparent demo fixture is activated)
2. The event becomes structured data via LLM extraction
3. The affected corridor risk score changes
4. The user can inspect WHY (evidence panel)
5. A scenario changes supply conditions
6. Refinery-level impact changes accordingly
7. Procurement alternatives are re-ranked
8. SPR support changes according to the scenario
9. Every important output is labeled with its data semantic: OBSERVED / DERIVED / HISTORICAL_CALIBRATED / ASSUMED / SIMULATED
10. The entire chain runs without manual hardcoding during the demo

> A successful demo is NOT measured by the number of technologies used.
>
> — INDRA Final Realistic Master Report, §27
