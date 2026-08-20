# INDRA — MVP Scope Classification

> This document classifies every feature into MUST HAVE, SHOULD HAVE, NICE TO HAVE, or DO NOT BUILD for the Phase-1 hackathon MVP.
>
> Source: PETRAS Analysis §19, INDRA Master Report §9
>
> **Revision:** Post-review corrections. Updated data labels to semantic classification. Corridors, crude_grades, refinery_supply_mix, and entity resolution are now MUST HAVE.

---

## MUST HAVE

These features are required for a credible Phase-1 demo. Without any one of these, the core event→recommendation chain is broken.

| # | Feature | Reason |
|---|---|---|
| M1 | **Geopolitical Event Monitor** — Ingest events from GDELT/RSS, filter energy/geopolitical keywords, extract event structure with LLM, store source URL and timestamp | Core AI component; demonstrates real data ingestion |
| M2 | **India Risk Dashboard** — Display risk scores (0–100 display scale) for corridors (Hormuz, Red Sea, Russia, Suez) as first-class entities. Each card shows: risk score, risk level, trend, top contributing events, last update, confidence/data quality | Core value proposition; explainable risk |
| M3 | **India Supply Network Map** — Interactive Leaflet map showing major Indian ports, selected refineries, SPR locations, chokepoints, supply routes with risk color overlays | India-specific differentiation; visual impact |
| M4 | **Scenario Simulator** — Minimum 3–4 preset scenarios: Hormuz 50% disruption, Hormuz 100% closure, Russia supply reduction, Red Sea disruption. Calculate national gap, affected refineries, days-to-minimum-stock, SPR bridge requirement | Demo impact; proves the system is computational |
| M5 | **Procurement Alternative Ranker** — For a selected refinery, display top alternatives with crude grade, origin, compatibility, route, transit time, estimated landed-cost premium, route risk, compliance flags, overall score | Real technical depth; strongest differentiator |
| M6 | **SPR Decision Support** — Display estimated supply gap, reserve bridge requirement, estimated days covered, suggested drawdown amount under scenario | India-specific; high relevance |
| M7 | **Evidence Chain / Explainability** — Every recommendation traceable via provenance model: source article → LLM extraction → entity resolution → risk contribution → scenario assumptions → supply impact → recommendation. Uses `evidence_records` and `evidence_links` tables | Credibility differentiator; what makes judges believe it's real |
| M8 | **Crude Price Feed** — Integrate EIA API for real crude price data (Brent, WTI) | Easy, free, real data |
| M9 | **OFAC Sanctions Integration** — Check suppliers/entities against OFAC sanctions list | Easy, free, real compliance data |
| M10 | **FastAPI Backend** — REST API serving all data endpoints | Foundation |
| M11 | **React Frontend** — Component-based UI rendering dashboard, map, scenario, procurement, evidence | Foundation |
| M12 | **PostgreSQL Database** — Single database with full entity schema | Foundation |
| M13 | **India Seed Data** — Refineries (~20), ports (~10), routes (~15+), corridors (~6), suppliers (~8), SPR locations (3), crude grades (~10–15 via `crude_grades` table), refinery-grade compatibility (`refinery_supply_mix` table), entity aliases (~50–100) | India-specific data model |
| M14 | **Risk Scoring Engine** — Weighted explainable formula (not LLM-generated scores) | Core; deterministic, reproducible |
| M15 | **LLM Event Extraction** — Structured JSON extraction from news articles via abstracted LLM provider, followed by entity resolution layer (alias lookup + RapidFuzz) to map names → internal IDs | Core AI component |
| M16 | **Data Semantic Labels** — Every data point in UI tagged as OBSERVED / DERIVED / HISTORICAL_CALIBRATED / ASSUMED / SIMULATED | Non-negotiable transparency contract |

## SHOULD HAVE

These features significantly strengthen the demo but can be partially descoped without breaking the core chain.

| # | Feature | Reason |
|---|---|---|
| S1 | **Russian Crude Risk Model** — Explicit modeling of Russia supply risk given India's ~37% dependency, shadow fleet logistics, sanctions exposure | Strong India differentiator |
| S2 | **Weather Disruption Overlay** — IMD/NOAA weather data affecting maritime routes | Easy to add; real data |
| S3 | **Historical Scenario Calibration** — Calibrate scenario parameters using historical EIA data from Gulf War II, Houthi disruptions, 2020 events | Makes numbers defensible to judges |
| S4 | **Redis API Cache** — Cache dashboard API responses for performance | Low complexity; improves UX |
| S5 | **USD/INR FX Integration** — RBI daily exchange rate data for compound cost modeling | Free, real; adds India-specific value |
| S6 | **Price Charts** — Historical crude price charts using Recharts | Visual enrichment; real data |
| S7 | **ACLED Conflict Events** — Structured conflict data for risk scoring | Authoritative; free for research |
| S8 | **Docker Deployment** — Containerized deployment for environment consistency | Simplifies demo setup |
| S9 | **LP Procurement Optimizer** — Full linear programming via scipy/PuLP instead of simple ranking | Upgrades M5 from ranking to real optimization |

## NICE TO HAVE

These add polish but are last-priority. Build only if all MUST HAVE and SHOULD HAVE items are stable.

| # | Feature | Reason |
|---|---|---|
| N1 | **XGBoost Disruption Classifier** — Binary classification model trained on ACLED + EIA historical data | Adds ML credibility; but Phase 1 risk engine is rule-based |
| N2 | **SHAP Explanations** — SHAP feature importance for XGBoost model outputs | Only relevant if N1 is implemented |
| N3 | **News Deduplication** — Pre-trained sentence transformer for detecting duplicate events across sources | Reduces noise; not critical for demo |
| N4 | **Crude Price Spike Scenario** — Additional scenario type for Brent +15% shock | Extends M4 |
| N5 | **LLM Recommendation Summary** — Natural language action brief generated after all calculations complete | Polish; impressive but not essential |
| N6 | **Interactive Scenario Parameters** — User-adjustable disruption percentage and duration sliders | UX improvement for M4 |

## DO NOT BUILD

These are explicitly excluded from Phase 1. Implementing any of these will waste time and/or damage credibility.

| # | Feature | Why Not |
|---|---|---|
| X1 | **Real-time AIS Vessel Tracking** | Costs $5K+/month. Claiming live AIS without paid access is immediately detectable by knowledgeable judges |
| X2 | **3D Supply Chain Visualization** (Three.js globe) | Cosmetic, no functional value, wastes 2+ days |
| X3 | **Mobile Application** | No time; not in scope |
| X4 | **Multi-user Authentication** | Phase 2; no demo value |
| X5 | **Full Enterprise Entity Resolution Engine** | Months of engineering work; Phase 1 uses controlled alias tables + RapidFuzz fuzzy matching instead |
| X6 | **True Discrete-Event Simulation** | Months of work; parametric scenarios are sufficient |
| X7 | **Kafka Event Streaming** | Zero streaming volume; APScheduler is adequate |
| X8 | **Neo4j Graph Database** | Overkill; NetworkX handles all graph needs |
| X9 | **LSTM / Temporal Fusion Transformer** | Not enough time to train properly |
| X10 | **Reinforcement Learning** | Needs simulation environment that doesn't exist |
| X11 | **Graph Neural Networks** | No training data; Neo4j dependency |
| X12 | **GPU-Heavy Custom Transformer Training** | Out of scope for a 4-day hackathon |
| X13 | **Kubernetes Orchestration** | Cloud-managed container or local demo is sufficient |
| X14 | **Blockchain** | Absolutely not |
| X15 | **Enterprise Authentication / SSO / SAP** | Phase 3; no demo value |
| X16 | **Paid Commercial Data Feeds** (Bloomberg, Reuters, Spire) | Cost-prohibitive; free alternatives exist |
| X17 | **MongoDB / ClickHouse / Elasticsearch** | PostgreSQL JSONB handles all semi-structured data needs |
| X18 | **dbt / Airflow** | APScheduler + Python scripts are sufficient |
| X19 | **Multi-database Architecture** | Single PostgreSQL is sufficient for Phase 1 data volumes |
| X20 | **Microservices Decomposition** | Monolith is correct for a 4-day build |

---

## Scope Decision Matrix

```
BUILD NOW  ←→  BUILD LATER  ←→  NEVER BUILD (for hackathon)

MUST HAVE (M1–M16)     → Build in Days 1–3
SHOULD HAVE (S1–S9)    → Build in Days 2–4 if MUST items are stable
NICE TO HAVE (N1–N6)   → Build on Day 4 evening only if everything else works
DO NOT BUILD (X1–X20)  → Do not build. Do not mention as implemented.
```
