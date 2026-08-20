# INDIA ENERGY SUPPLY CHAIN RESILIENCE — BRUTALLY HONEST TECHNICAL ANALYSIS

> **PETRAS — Petroleum Trade Resilience & Advisory System**
> Hackathon Technical Research Report | Phase 1 Deadline: 23 August 2026, 4:00 PM IST

---

## ONE-PARAGRAPH VERDICT

This problem statement is **genuinely worth pursuing** — it is grounded in real, documented Indian energy dependency data, describes actual decision-making failures, and has commercial relevance. However, the official illustrative directions (Geopolitical Risk Intelligence Agent + Disruption Scenario Modeller + Adaptive Procurement Orchestrator + Strategic Reserve Optimisation Agent + Supply Chain Digital Twin) collectively describe a $50M enterprise system. **A student team has approximately 4 days.** The gap is enormous. What saves this project is that the core value proposition — giving India-specific, explainable procurement risk intelligence — can be demonstrated with a disciplined subset: a news-driven geopolitical risk scorer, a parametric scenario engine, and an optimization-based rerouting recommender, all anchored to real Indian refinery/port/supplier data. If you chase all five illustrative directions, you will deliver a flashy dashboard with fake numbers and no judges will believe any of it. If you build one tight, honest, explainable pipeline that actually runs — you will stand out from 90% of teams who will submit "AI-powered dashboards" with hardcoded data.

---

## TABLE OF CONTENTS

1. [Executive Verdict](#1-executive-verdict)
2. [Problem Deconstruction](#2-problem-deconstruction)
3. [Real-World Enterprise System Architecture](#3-real-world-enterprise-system-architecture)
4. [Global Market Landscape](#4-global-market-landscape)
5. [Competitor Gap Analysis](#5-competitor-gap-analysis)
6. [India-Specific Ecosystem](#6-india-specific-ecosystem)
7. [Real-Time Data Strategy](#7-real-time-data-strategy)
8. [Data Architecture](#8-data-architecture)
9. [Database Architecture](#9-database-architecture)
10. [ML Model Strategy](#10-ml-model-strategy)
11. [AI/LLM Strategy](#11-aillm-strategy)
12. [Digital Twin](#12-digital-twin)
13. [Scenario Engine](#13-scenario-engine)
14. [Procurement Optimization](#14-procurement-optimization)
15. [Risk & Explainability](#15-risk--explainability)
16. [Final System Architecture](#16-final-system-architecture)
17. [Technology Stack](#17-technology-stack)
18. [Cost Analysis](#18-cost-analysis)
19. [MVP Scope](#19-mvp-scope)
20. [Development Plan](#20-development-plan)
21. [Demo Strategy](#21-demo-strategy)
22. [Data vs Simulation Honesty](#22-data-vs-simulation-honesty)
23. [Commercial Viability](#23-commercial-viability)
24. [Hackathon Judge Assessment](#24-hackathon-judge-assessment)
25. [Red Flags to Avoid](#25-red-flags-to-avoid)
26. [Build vs Don't Build Table](#26-build-vs-dont-build-table)
27. [Final CTO Recommendation](#27-final-cto-recommendation)
28. [Final Answer in One Page](#final-answer-in-one-page)

---

## 1. Executive Verdict

| Dimension | Assessment |
|---|---|
| Problem reality | ✅ Real and well-documented |
| Commercial relevance | ✅ IOC, BPCL, HPCL, MoPNG are real customers |
| Student buildability (4 days) | ⚠️ Feasible only with brutal scope discipline |
| Differentiation vs global players | ✅ India-specificity is a real gap |
| AI credibility risk | 🔴 HIGH — most teams will fake this |
| Data availability | ⚠️ Mixed — some real, some must be historical/synthetic |
| Demo viability | ✅ Achievable with right design |

---

## 2. Problem Deconstruction

### What Problem is India Actually Facing?

India's crude oil security has three structural vulnerabilities that compound each other:

**Structural dependency:** India imports ~88% of crude oil requirements. In FY2024-25, India imported approximately 232 million metric tonnes of crude. The Ministry of Petroleum & Natural Gas (MoPNG) publishes this data via PPAC (Petroleum Planning & Analysis Cell, ppac.gov.in).

**Geographic concentration:** 40–45% of India's crude imports transit the Strait of Hormuz. Middle Eastern suppliers (Saudi Arabia, Iraq, UAE, Kuwait) collectively supply 50–60% of India's crude. This creates a single-point-of-failure. Any Hormuz disruption simultaneously affects multiple suppliers.

**Reserve inadequacy:** India's Strategic Petroleum Reserves (SPR) at Visakhapatnam (1.33 MMT), Mangalore (1.5 MMT), and Padur (2.5 MMT) total ~5.33 MMT. At ~5 MMBbl/day consumption, this is roughly 9.5 days. The IEA recommends 90 days. India is at ~10% of recommended buffer.

### What Is Currently Done Manually

- Procurement teams at Indian Oil Corporation, Bharat Petroleum, Hindustan Petroleum manually track news
- Risk signals come from Bloomberg terminals, Reuters Eikon (expensive), internal analyst reports
- Rerouting decisions are made in committee with 48–72 hour lag
- No integrated system connects geopolitical news → shipping risk → refinery impact → reserve drawdown → procurement decision
- Trade desks at IOC/BPCL operate on Excel models for supply gap estimation
- Strategic reserve drawdown decisions are made by an inter-ministerial committee with significant political considerations

### Who Makes These Decisions

- IOC, BPCL, HPCL procurement teams (commercial crude buyers)
- Directorate General of Hydrocarbons (DGH)
- Ministry of Petroleum and Natural Gas (MoPNG)
- Indian Strategic Petroleum Reserves Ltd (ISPRL)
- Oil Coordination Committee (when active)

### Decision Frequency

| Decision | Frequency |
|---|---|
| Crude procurement tenders | Monthly to quarterly |
| Emergency rerouting | Ad hoc, triggered by events |
| Reserve drawdown | Ministerial decision, very infrequent |
| Route risk assessment | Ideally daily; currently weekly at best |

### The Propagation Chain (Real-World)

```
GEOPOLITICAL EVENT (e.g., IRGC seizes tanker in Hormuz)
         ↓
RISK SIGNAL (news, OSINT, shipping alerts, diplomatic cables)
         ↓ [24–48hr lag in current system]
MARITIME IMPACT (vessels re-route, insurers issue war-risk surcharges)
         ↓
FREIGHT RATE SPIKE (Baltic Dirty Tanker Index, BDTI rises 15–40%)
         ↓
INSURANCE COST INCREASE (war-risk premium 0.1–0.5% cargo value/voyage)
         ↓
EFFECTIVE CRUDE COST INCREASE (freight + insurance embedded in CIF price)
         ↓
REFINERY SCHEDULING DISRUPTION (wrong crude grade arrives, wrong timing)
         ↓
CRUDE AVAILABILITY SHORTFALL (refineries below optimal feed rate)
         ↓
PRODUCT YIELD IMPACT (petrol, diesel, LPG output reduced)
         ↓
INVENTORY DRAWDOWN (refinery product tanks deplete faster)
         ↓
STRATEGIC RESERVE PRESSURE (government considers releasing SPR)
         ↓
IMPORT COST INCREASE (INR/USD exposure amplifies if rupee weakens)
         ↓
INFLATION SIGNAL (transport fuel prices feed into CPI)
         ↓
PROCUREMENT EMERGENCY (IOC/BPCL forced to buy spot at premium)
         ↓
FOREX PRESSURE (higher oil import bill widens CAD)
```

### Where AI Genuinely Adds Value vs Deterministic Systems

| Task | AI/ML Value | Deterministic/Rule Value |
|---|---|---|
| News event detection | ✅ NLP classification | ❌ Too many edge cases |
| Entity disambiguation (IRGC = Iran) | ✅ NER + knowledge graph | ⚠️ Rules cover 70% |
| Route risk scoring | ⚠️ Hybrid | ✅ Rules + historical |
| Disruption probability | ✅ Time-series + classification | ❌ Can't handle novel events |
| Freight rate forecasting | ✅ ARIMA/ML | ❌ Too volatile for rules |
| Reserve drawdown optimization | ✅ LP/MIP | ✅ Both work |
| Procurement ranking | ✅ Multi-criteria optimization | ✅ Both work |
| Scenario simulation | ❌ Rule-based is better | ✅ Deterministic propagation |
| Regulatory/compliance checking | ❌ Avoid | ✅ Rule-based |

---

## 3. Real-World Enterprise System Architecture

### What a Real Enterprise System (like Kpler or Vortexa) Actually Does

**Data ingestion layer:** Ingests AIS signals from satellites and terrestrial receivers (400M+ messages/day), global news from 100K+ sources, commodity price ticks, sanctions databases (OFAC, EU, UN), weather data (ECMWF), port call data, cargo manifests.

**Entity resolution:** "Saudi Aramco", "Saudi Arabian Oil Company", "Aramco" must resolve to the same entity. Vessel identity requires IMO number + MMSI reconciliation because vessels spoof AIS. Port identity requires UN/LOCODE normalization. Route identity requires spatial clustering of AIS trajectories.

> **Hackathon approach:** Pre-build a static knowledge base of 50 key entities rather than attempting dynamic entity resolution.

**Event detection:** Real systems use:
- Named entity recognition to extract organizations, locations, vessels from news
- Event classification (sanction, military action, port closure, weather)
- Severity scoring (0–1) using sentence context
- Deduplication (same event in 50 news sources = 1 event)
- Temporal anchoring (when did this happen vs when was it reported)

**Risk scoring:** Real systems use combination of:
- Base country risk (from IAEA, political risk indices)
- Dynamic event contribution (recent incidents decay over time)
- Route-specific factors (chokepoint proximity, insurance zone status)
- Vessel-specific factors (flag state, owner sanctions exposure)

---

## 4. Global Market Landscape

### Kpler
- **Target:** Energy traders, refiners, governments, hedge funds
- **Core data:** Real-time AIS-derived vessel tracking, cargo flow estimation, storage level estimation from satellite
- **What they do extremely well:** Actual cargo flow data with vessel-level granularity; India crude import tracking
- **What they lack:** India-specific downstream impact modeling, procurement decision support, reserve optimization
- **Cost for students:** Enterprise pricing — starts at tens of thousands USD/year. **UNAVAILABLE for student prototype**
- **What you can replicate:** Their India crude import flow visualizations using public PPAC data

### Vortexa
- **Target:** Energy traders, refiners, commodity desks
- **Core data:** AIS + port call data + cargo inference
- **Gap:** No scenario modeling, no procurement optimization, no reserve management
- **Cost for students:** Paid. **Likely UNAVAILABLE for free prototype.** Check for academic access.

### Windward
- **Target:** Banks, insurers, commodity traders, governments
- **Core focus:** AIS-based vessel risk scoring, sanctions compliance, dark vessel detection
- **Gap:** No downstream energy impact modeling, no refinery impact, no reserve optimization
- **Cost:** Enterprise. **UNAVAILABLE for student use.**

### S&P Global Commodity Insights (formerly Platts)
- **Target:** Refiners, traders, governments, banks
- **Relevance:** India uses Platts prices for contract pricing with Middle East suppliers
- **Free tier:** Some data available on public S&P website; full feed is expensive

### LSEG / Refinitiv
- **Target:** Financial institutions, energy traders
- **Cost:** Terminal starts at $20K+/year. **UNAVAILABLE for student use.**

### Palantir
- **Target:** Governments, defense, large enterprises
- **Gap:** Not designed for energy procurement optimization — general platform
- **Cost:** Enterprise. **Not relevant for hackathon.**

### Project44 / FourKites / Everstream
- **Relevance:** LOW — they track road/ocean container freight, not crude oil tankers

### ✅ ACLED (Armed Conflict Location & Event Data) — USE THIS
- **URL:** acleddata.com
- **Cost:** FREE for research and non-commercial use
- **API:** YES — acleddata.com/data-export-tool/
- **Update frequency:** Weekly, near-real-time for some regions
- **Coverage:** Excellent for Middle East

### ✅ GDELT Project — USE THIS
- **URL:** gdeltproject.org
- **Cost:** FREE
- **API/Data:** BigQuery (Google), direct download
- **Update:** 15-minute updates
- **Coverage:** Global news event database

---

## 5. Competitor Gap Analysis

### "Why does this need to exist if Kpler/Vortexa already exist?"

#### Weak Gaps (Do NOT Use as Differentiators)
- "Indian UI" — not a real gap
- "Cheaper" — temporary, not defensible
- "Better AI" — unverifiable claim

#### Real Gaps

**Gap 1: India-specific downstream propagation modeling**
Kpler/Vortexa track crude flows TO India. They do not model the downstream cascade: which Indian refinery is affected → which product streams are impacted → which geographic distribution network loses supply → which strategic reserve needs to compensate → what is the exact procurement gap for IOC's Panipat refinery given a Hormuz disruption.

**Gap 2: Indian refinery-specific crude compatibility matrix**
Indian refineries are configured for specific crude grades. Reliance Jamnagar can handle ultra-heavy sour crude from Venezuela. IOC Panipat is configured for a different crude slate. Kpler shows cargo flows but does not model whether a substitute crude can actually be processed at a specific refinery.

**Gap 3: Integration of Indian public datasets**
PPAC (ppac.gov.in) publishes detailed India import data. ISPRL publishes reserve data. Ministry of Ports publishes vessel traffic data. No commercial platform integrates these Indian government sources into a unified risk picture.

**Gap 4: Russian crude trade modeling for India**
Since 2022, India has become the second-largest buyer of Russian Urals crude. The discount (previously $25–30/barrel) and shadow fleet logistics create a unique risk profile that Western platforms do not model well.

**Gap 5: Rupee/crude price joint risk modeling**
India's effective crude import cost is a function of (Brent price) × (USD/INR exchange rate). A simultaneous crude price spike AND rupee depreciation creates compound risk that standard commodity tools ignore.

#### Gaps Already Solved
- Real-time vessel tracking — Kpler/Vortexa/Windward do this better than any student team can
- Global sanctions database — OFAC, EU, UN publish this free; commercial players just index it
- News sentiment — Bloomberg/Reuters do this at industrial scale

---

## 6. India-Specific Ecosystem

### Real Indian Data Sources

| Source | URL | Cost | Frequency | API | Phase 1 Action |
|---|---|---|---|---|---|
| PPAC | ppac.gov.in | FREE | Monthly | ❌ PDF/CSV | Download all historical files, parse, load into DB |
| Data.gov.in | data.gov.in | FREE | Varies | ✅ | Use API to pull petroleum datasets |
| ISPRL | isprl.gov.in | FREE | Annual | ❌ | Hardcode 3 SPR locations from public reports |
| RBI | rbi.org.in/statistics | FREE | Daily | ✅ | USE THIS — free, authoritative, daily FX data |
| EIA | api.eia.gov | FREE | Daily/weekly | ✅ | USE THIS — free API, excellent data |
| ACLED | acleddata.com | FREE | Weekly | ✅ | USE THIS — register and pull |
| GDELT | gdeltproject.org | FREE | 15-min | ✅ BigQuery | USE THIS — free, real-time |
| NewsAPI | newsapi.org | FREE tier (delayed) | 24hr delay | ✅ | Use free tier; be honest about 24hr delay |
| OFAC | sanctionslist.treasury.gov | FREE | Multiple/day | ✅ | USE THIS — free, authoritative |
| World Bank | worldbank.org/commodities | FREE | Monthly | ✅ | Good for historical training data |

### Indian Refineries (Real Data for Hardcoding)

| Refinery | Owner | Location | Capacity (MMTPA) | Crude Slate |
|---|---|---|---|---|
| Jamnagar DTA | Reliance | Gujarat | 35.8 | Complex, heavy sour |
| Jamnagar SEZ | Reliance | Gujarat | 22.8 | Complex, heavy sour |
| Paradip | IOC | Odisha | 15.0 | Medium sour |
| Koyali (Vadodara) | IOC | Gujarat | 13.7 | Light-medium |
| Panipat | IOC | Haryana | 15.0 | Medium |
| Mathura | IOC | UP | 8.0 | Light |
| Bongaigaon | IOC | Assam | 2.7 | Light |
| Barauni | IOC | Bihar | 6.0 | Medium |
| Haldia | IOC | WB | 7.5 | Medium |
| Guwahati | IOC | Assam | 1.0 | Light |
| Mumbai | BPCL | Maharashtra | 12.0 | Light |
| Kochi | BPCL | Kerala | 15.5 | Heavy sour |
| Bina | BPCL | MP | 7.8 | Medium |
| Visakhapatnam | HPCL | AP | 8.3 | Light-medium |
| Mumbai (HPCL) | HPCL | Maharashtra | 7.5 | Light |
| Bathinda | HPCL-Mittal | Punjab | 11.25 | Medium sour |
| Mangalore | MRPL | Karnataka | 15.0 | Heavy sour |
| Chennai | CPCL | Tamil Nadu | 10.5 | Medium |
| Numaligarh | NRL | Assam | 3.0 | Light |
| Tatipaka | ONGC | AP | 0.067 | Light |

*Source: PPAC Annual Report 2024-25, company annual reports*

### Indian Crude Import Sources (~FY2025)

| Country | Share | Grade | Risk Profile |
|---|---|---|---|
| Russia | ~36–38% | Urals, ESPO | Sanctions risk (secondary), shadow fleet |
| Iraq | ~20–22% | Basrah Light/Heavy | Hormuz risk |
| Saudi Arabia | ~14–16% | Arab Light/Extra Light | Hormuz risk |
| UAE | ~5–6% | Murban | Hormuz risk |
| USA | ~5–6% | WTI, Eagle Ford | No transit risk |
| Kuwait | ~3–4% | Kuwait Export | Hormuz risk |
| Nigeria | ~2–3% | Bonny Light | Atlantic route |
| Others | ~8–10% | Various | Varies |

*Source: PPAC monthly import data, approximate FY2025*

### Indian SPR Locations (Real)

| Location | Operator | State | Capacity (MMT) |
|---|---|---|---|
| Visakhapatnam | ISPRL | Andhra Pradesh | 1.33 |
| Mangalore | ISPRL | Karnataka | 1.50 |
| Padur | ISPRL | Karnataka | 2.50 |
| **Total** | | | **5.33** |

*Source: ISPRL official website, MoPNG reports*

---

## 7. Real-Time Data Strategy

### Classification of Every Data Source

| Data | Source | Cost | Frequency | Phase 1 Strategy |
|---|---|---|---|---|
| Geopolitical events | GDELT | FREE | 15-min | ✅ USE LIVE |
| Conflict events | ACLED | FREE | Weekly | ✅ USE + poll daily |
| Sanctions list | OFAC | FREE | Real-time | ✅ USE LIVE |
| Crude oil prices | EIA API | FREE | Daily/weekly | ✅ USE LIVE |
| USD/INR FX | RBI API | FREE | Daily | ✅ USE LIVE |
| India import data | PPAC | FREE | Monthly | ✅ USE HISTORICAL |
| Vessel tracking (AIS) | MarineTraffic | PAID | Real-time | ❌ USE HISTORICAL |
| Vessel tracking (AIS) | VesselFinder | FREEMIUM | Delayed | ⚠️ Demo only |
| AIS open data | Marine Cadastre (US) | FREE | Historical | ✅ USE HISTORICAL |
| Port data | PPAC/Major Ports | FREE | Monthly | ✅ USE HISTORICAL |
| News | NewsAPI | FREE (delayed) | 24hr delay | ✅ USE with caveat |
| News | RSS feeds | FREE | Minutes | ✅ USE LIVE |
| BDTI (freight index) | Baltic Exchange | PAID | Daily | ❌ |
| Freight rates | Clarksons | PAID | Daily | ❌ |
| Weather/Cyclone | IMD, NOAA | FREE | Daily | ✅ USE LIVE |
| Supply gap estimate | Derived/Calculated | — | — | ✅ CALCULATE |

### ⚠️ CRITICAL: AIS Data Reality

**DO NOT CLAIM REAL-TIME AIS.** The truth:

- Real-time AIS (global, high quality) costs **$5,000–$50,000/month** from Spire, ExactEarth, or similar
- MarineTraffic API: paid, starts at ~$500/month for commercial use

**What you CAN use honestly:**
- Historical AIS route data for Hormuz/Red Sea corridor (pre-loaded)
- Marine Cadastre (marinecadastre.gov): FREE historical AIS data for US waters
- AIS Hub (aishub.net): Community AIS feed, some historical data available free

**Demo strategy for AIS:** Pre-load historical tanker route data for major India-bound crude corridors. When running a scenario ("Hormuz closed"), animate route changes on pre-computed alternate paths. Label it clearly as "scenario simulation on historical route data." This is honest and still impressive.

---

## 8. Data Architecture

### Recommended Architecture (Phase 1 Realistic)

```
DATA SOURCES
├── GDELT API (15-min geopolitical events)
├── ACLED API (conflict events)
├── OFAC API (sanctions)
├── EIA API (crude prices)
├── RBI API (FX rates)
├── NewsAPI / RSS (news articles)
├── PPAC CSV (India import history — static)
├── Historical AIS (static route data)
└── IMD/NOAA (weather)
         ↓
INGESTION LAYER (Python scheduler — APScheduler/cron)
├── GDELT poller (15-min)
├── ACLED poller (daily)
├── Price/FX poller (daily)
├── News poller (hourly)
└── Static data loader (one-time)
         ↓
PROCESSING LAYER (Python)
├── Deduplication
├── Entity normalization (rule-based + LLM)
├── Event classification (LLM-assisted)
├── Severity scoring
└── Feature extraction
         ↓
STORAGE
├── PostgreSQL (main DB — all structured data)
│   ├── events, entities, risk_scores, shipments
│   ├── refineries, ports, routes, suppliers
│   └── scenarios, recommendations
└── Redis (cache for dashboard API responses)
         ↓
AI/ML LAYER
├── Risk scoring engine (rule-based + weighted formula)
├── Disruption probability (XGBoost/LightGBM on historical)
├── Scenario propagation (parametric model)
└── Procurement optimizer (LP via PuLP/scipy)
         ↓
API LAYER (FastAPI)
├── /events  /risk  /scenario  /recommend  /prices  /reserve
         ↓
FRONTEND (React + Leaflet)
├── Map (routes, risk overlays, vessel positions)
├── Risk dashboard (current scores)
├── Scenario simulator (interactive)
├── Recommendation panel
└── Evidence/explanation panel
```

### Technology Selection — Justified

| Technology | Use? | Reason |
|---|---|---|
| PostgreSQL | ✅ YES | Single database for Phase 1. PostGIS + TimescaleDB extensions cover all needs. |
| Redis | ✅ YES | Cache only. Dashboard speed. |
| Neo4j | ❌ **DO NOT BUILD** | Overkill. NetworkX in Python handles graph pathfinding. Setup complexity not worth it. |
| Kafka/Redpanda | ❌ **DO NOT BUILD** | Zero streaming volume. APScheduler + PostgreSQL adequate. |
| MongoDB | ❌ **DO NOT BUILD** | PostgreSQL JSONB handles semi-structured data. |
| Elasticsearch | ❌ **DO NOT BUILD** | News search volume doesn't require this. |
| dbt/Airflow | ❌ **DO NOT BUILD** | APScheduler + Python scripts + PostgreSQL is sufficient. |
| DuckDB | ⚠️ Optional | Useful for parsing historical PPAC CSVs during setup only. |

---

## 9. Database Architecture

### Minimum Practical Schema (PostgreSQL)

```sql
-- Core entities
CREATE TABLE countries (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    iso3 CHAR(3) UNIQUE,
    base_risk_score DECIMAL(5,3),
    region VARCHAR(50),
    is_hormuz_dependent BOOLEAN DEFAULT FALSE,
    is_red_sea_dependent BOOLEAN DEFAULT FALSE
);

CREATE TABLE suppliers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    country_id INT REFERENCES countries(id),
    crude_grades TEXT[],
    annual_supply_capacity_mmtpa DECIMAL(8,2),
    current_sanctions_risk DECIMAL(5,3),
    is_sanctioned BOOLEAN DEFAULT FALSE,
    sanction_source VARCHAR(50)
);

CREATE TABLE refineries (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    owner VARCHAR(100),
    state VARCHAR(100),
    port_id INT,
    capacity_mmtpa DECIMAL(8,2),
    throughput_current_mmtpa DECIMAL(8,2),
    compatible_crude_grades TEXT[],
    latitude DECIMAL(9,6),
    longitude DECIMAL(9,6)
);

CREATE TABLE ports (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    un_locode VARCHAR(10),
    country_id INT REFERENCES countries(id),
    is_indian BOOLEAN DEFAULT FALSE,
    latitude DECIMAL(9,6),
    longitude DECIMAL(9,6),
    annual_crude_throughput_mmtpa DECIMAL(8,2),
    current_operational_status VARCHAR(20)
);

CREATE TABLE routes (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    origin_port_id INT REFERENCES ports(id),
    dest_port_id INT REFERENCES ports(id),
    distance_nm INT,
    avg_transit_days DECIMAL(5,2),
    passes_through_hormuz BOOLEAN DEFAULT FALSE,
    passes_through_red_sea BOOLEAN DEFAULT FALSE,
    passes_through_malacca BOOLEAN DEFAULT FALSE,
    passes_through_cape BOOLEAN DEFAULT FALSE,
    base_freight_rate_per_mt DECIMAL(8,2),
    current_risk_score DECIMAL(5,3),
    is_operational BOOLEAN DEFAULT TRUE
);

CREATE TABLE geopolitical_events (
    id SERIAL PRIMARY KEY,
    event_type VARCHAR(50),
    title TEXT NOT NULL,
    description TEXT,
    source_url TEXT,
    source_name VARCHAR(100),
    country_id INT REFERENCES countries(id),
    affected_route_ids INT[],
    severity DECIMAL(5,3),
    occurred_at TIMESTAMP,
    detected_at TIMESTAMP DEFAULT NOW(),
    is_verified BOOLEAN DEFAULT FALSE,
    raw_text TEXT
);

CREATE TABLE risk_scores (
    id SERIAL PRIMARY KEY,
    entity_type VARCHAR(20),
    entity_id INT NOT NULL,
    score DECIMAL(5,3) NOT NULL,
    component_scores JSONB,
    contributing_event_ids INT[],
    calculated_at TIMESTAMP DEFAULT NOW(),
    valid_until TIMESTAMP
);

CREATE TABLE crude_prices (
    id SERIAL PRIMARY KEY,
    grade_name VARCHAR(100),
    price_usd_per_barrel DECIMAL(10,4),
    recorded_at TIMESTAMP,
    source VARCHAR(50)
);

CREATE TABLE price_history (
    time TIMESTAMP NOT NULL,
    grade_name VARCHAR(100),
    price_usd_per_barrel DECIMAL(10,4),
    usd_inr_rate DECIMAL(10,4),
    price_inr_per_barrel DECIMAL(12,4)
        GENERATED ALWAYS AS (price_usd_per_barrel * usd_inr_rate) STORED
);

CREATE TABLE scenarios (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    scenario_type VARCHAR(50),
    parameters JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(100)
);

CREATE TABLE scenario_results (
    id SERIAL PRIMARY KEY,
    scenario_id INT REFERENCES scenarios(id),
    affected_routes JSONB,
    supply_gap_mmt DECIMAL(8,3),
    price_impact_usd_per_barrel DECIMAL(8,4),
    reserve_drawdown_days DECIMAL(8,2),
    gdp_impact_estimate_usd_bn DECIMAL(10,3),
    freight_cost_increase_pct DECIMAL(8,2),
    recommendations JSONB,
    calculated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE procurement_options (
    id SERIAL PRIMARY KEY,
    supplier_id INT REFERENCES suppliers(id),
    route_id INT REFERENCES routes(id),
    crude_grade VARCHAR(100),
    volume_available_mmt DECIMAL(8,3),
    price_cif_usd_per_barrel DECIMAL(10,4),
    transit_days DECIMAL(5,2),
    risk_score DECIMAL(5,3),
    compatible_refineries INT[],
    is_sanctioned BOOLEAN DEFAULT FALSE,
    ranking_score DECIMAL(10,6),
    last_updated TIMESTAMP DEFAULT NOW()
);

CREATE TABLE strategic_reserves (
    id SERIAL PRIMARY KEY,
    location_name VARCHAR(200),
    operator VARCHAR(100),
    state VARCHAR(100),
    capacity_mmt DECIMAL(8,3),
    current_level_mmt DECIMAL(8,3),
    -- India consumes ~0.56 MMT/day crude equivalent
    days_coverage DECIMAL(8,2)
        GENERATED ALWAYS AS (current_level_mmt / 0.56) STORED,
    last_updated TIMESTAMP DEFAULT NOW(),
    latitude DECIMAL(9,6),
    longitude DECIMAL(9,6)
);
```

> **Why single PostgreSQL is sufficient for Phase 1:** You have at most hundreds of events, 20 refineries, 50 routes, 200 procurement options. PostgreSQL JSONB handles semi-structured scenario parameters. PostGIS handles geospatial queries. TimescaleDB (drop-in extension) handles time-series price data. A 5-database architecture would be pure overengineering.

---

## 10. ML Model Strategy

### The Brutal Truth

You cannot train a meaningful ML model from scratch in 4 days when you're also building a full-stack application. Here is what you CAN do:

### Module 1: Geopolitical Event Classification
| | |
|---|---|
| **Input** | News article text |
| **Model** | LLM via API (Claude/GPT-4o) with structured prompt |
| **Output** | JSON: `{event_type, severity, affected_entities, affected_routes}` |
| **Why LLM** | Zero training data needed. Directly classifies any news article. |
| **Risk** | Hallucination — mitigate with constrained output schema + validation rules |
| **Cost** | ~$0.001–0.005 per article. Free tier covers demo volumes. |

### Module 2: Route Risk Scoring
| | |
|---|---|
| **Input** | `{country_risk, recent_events_7d, active_sanctions, weather_alert, chokepoint_factor}` |
| **Model** | Weighted scoring formula (deterministic + data-driven weights) |
| **Formula** | `risk = 0.35×country_risk + 0.25×event_impact + 0.20×sanctions + 0.10×weather + 0.10×chokepoint` |
| **Why not ML** | No labeled ground truth for "route disruption = 1" |
| **Explainability** | ✅ Each component is visible to user |

### Module 3: Disruption Probability
| | |
|---|---|
| **Phase 1** | Rule-based threshold: if ACLED events in corridor > X in 7 days AND sanctions_change = True → elevated |
| **Phase 2** | XGBoost classification with binary label (disruption occurred = 1) using ACLED + EIA historical data |
| **Expected accuracy** | 65–75% on historical holdout (don't overclaim) |

### Module 4: Procurement Optimization
| | |
|---|---|
| **Input** | Available suppliers × routes × prices × risk scores × compatibility × volume constraints |
| **Model** | Linear programming — minimize cost + weighted risk |
| **Library** | `scipy.optimize.linprog` or `PuLP` — free, Python-native |
| **Output** | Ranked procurement options with cost/risk tradeoff |
| **Status** | ✅ This is real optimization, not fake AI |

### Module 5: Supply Gap Forecasting
| | |
|---|---|
| **Model** | Deterministic calculation |
| **Formula** | `supply_gap = (normal_import_rate × disruption_days × disruption_pct) - available_alternative_volume` |
| **Status** | ✅ Transparent arithmetic — better for judges than black-box |

### Model Verdict Summary

```
✅ DO USE:
   LLM API (Claude Haiku / GPT-4o-mini) for news classification
   Rule-based weighted scoring for risk (explainable)
   Linear programming for procurement optimization
   Historical EIA data for price impact calibration
   Parametric scenario model for downstream propagation

✅ BACKUP:
   XGBoost on ACLED+EIA historical data for disruption probability
   Pre-trained sentence transformer for news deduplication

❌ DO NOT USE:
   LLM for everything — hallucination risk + cost
   LSTM/Temporal Fusion Transformer — not enough time to train properly
   Reinforcement learning — needs simulation environment you don't have
   Graph neural networks — Neo4j dependency, no training data
   Random risk scores — judges will see through this immediately
```

---

## 11. AI/LLM Strategy

### Hybrid Architecture (Honest Version)

```
NEWS ARTICLE (Reuters, GDELT, NewsAPI)
         ↓
LLM CALL (Claude Haiku or GPT-4o-mini)
Prompt: "Extract from this news article:
- event_type: [SANCTION|MILITARY|PORT_CLOSURE|ATTACK|DIPLOMATIC|OTHER]
- severity: [0.0-1.0]
- affected_countries: [list]
- affected_chokepoints: [HORMUZ|RED_SEA|MALACCA|NONE]
- affected_companies: [list]
- confidence: [0.0-1.0]
Return JSON only."
         ↓
STRUCTURED EVENT OBJECT
         ↓
RULE-BASED VALIDATION
(Is event within last 30 days? Confidence > 0.6? Country in tracked list?)
         ↓
DATABASE INSERTION
         ↓
RISK SCORE UPDATE (deterministic formula)
         ↓
ALERT if risk_delta > threshold
         ↓
SCENARIO ENGINE (parametric)
         ↓
OPTIMIZATION (scipy LP)
         ↓
RECOMMENDATION GENERATION (LLM for natural language explanation)
         ↓
DASHBOARD UPDATE
```

### Why This Is Better Than "LLM Does Everything"

- **LLM** does what it's good at: extracting structure from unstructured text
- **Deterministic formulas** do what they're good at: transparent, auditable risk calculation
- **LP** does what it's good at: provably optimal procurement ranking
- **LLM** explains the result in plain English (second LLM call, cheap)
- Judges can trace every recommendation back to source events — this is real explainable AI

### LLM Cost Estimate for Demo

| Metric | Value |
|---|---|
| Claude Haiku input cost | ~$0.00025/1K tokens |
| Claude Haiku output cost | ~$0.00125/1K tokens |
| Average article | ~500 tokens in, ~100 tokens out |
| Cost per article | ~$0.0002 |
| 1,000 articles total | ~$0.20 |

Essentially free for demo purposes.

---

## 12. Digital Twin

### What "Digital Twin" Should Actually Mean Here

**DO NOT BUILD A FULL 3D SIMULATION FOR PHASE 1.**

A "Supply Chain Digital Twin" in this context should mean: a **live-updating graph model of India's energy supply network** where:

- **Nodes** = suppliers, ports, chokepoints, refineries, SPR locations, demand centers
- **Edges** = trade routes with attributes (distance, risk, freight cost, capacity)
- **State** = current inventory, current risk scores, active disruptions
- **Simulation** = parametric state changes when a node or edge is disrupted

### Minimum Valid Implementation

```python
class EnergySupplyTwin:
    def __init__(self, db_connection):
        self.nodes = self.load_entities()   # suppliers, ports, refineries, SPR
        self.edges = self.load_routes()     # route connections with attributes
        self.state = self.load_current_state()  # current risk scores, inventory

    def simulate_disruption(self, disrupted_entity_id, disruption_type, duration_days):
        # 1. Mark entity as disrupted
        # 2. Propagate through graph: which routes are affected?
        # 3. Which suppliers are unreachable?
        # 4. What volume is lost?
        # 5. Which refineries are affected?
        # 6. What is the inventory impact given current reserves?
        # 7. Return updated state
        pass

    def get_alternative_paths(self, origin, destination, excluded_entities):
        import networkx as nx
        G = self.build_graph(excluded=excluded_entities)
        return nx.all_simple_paths(G, origin, destination)
```

### Visualization

Render as an interactive Leaflet/Deck.gl map with:
- Lines between nodes (routes) colored by current risk (green→red gradient)
- Animated "disruption" that turns a route red and recalculates flows
- Sidebar showing affected nodes and recommended alternatives

### Do NOT Build for Phase 1

| Component | Why Not |
|---|---|
| 3D visualization (Three.js globe) | Cool, irrelevant, wastes 2 days |
| Discrete-event simulation engine | Overkill |
| Physics-based simulation | Nonsense for this problem |
| Purely cosmetic visualization | No underlying data model |

---

## 13. Scenario Engine

### Parametric Scenario Engine (Buildable in 1 Day)

```python
SCENARIO_PARAMETERS = {
    "HORMUZ_FULL_CLOSURE": {
        "capacity_reduction_pct": 100,
        "default_duration_days": 30,
        "affected_countries": ["IRAQ","IRAN","KUWAIT","SAUDI_ARABIA","UAE","QATAR","BAHRAIN"],
        "alternate_routes": ["CAPE_OF_GOOD_HOPE"],
        "freight_multiplier": 3.2,   # historical: Cape route ~3x longer
        "insurance_premium_increase_pct": 400,
        "typical_price_impact_per_barrel": 15.0,  # from historical Gulf War II data
    },
    "HORMUZ_30PCT_DISRUPTION": {
        "capacity_reduction_pct": 30,
        "freight_multiplier": 1.4,
        "price_impact_per_barrel": 5.0,
    },
    "RED_SEA_FULL_SUSPENSION": {
        "capacity_reduction_pct": 100,
        "alternate_routes": ["CAPE_OF_GOOD_HOPE"],
        "freight_multiplier": 2.8,
        "price_impact_per_barrel": 3.0,
    },
    "RUSSIA_SUPPLY_LOSS": {
        "affected_supplier": "RUSSIA",
        "volume_loss_pct": 100,      # India loses ~36% of crude supply
        "alternate_suppliers": ["SAUDI_ARABIA","IRAQ","USA","NIGERIA"],
        "price_impact_per_barrel": 10.0,
        "reachable_in_days": 30,
    },
    "CRUDE_PRICE_SPIKE_15PCT": {
        "brent_increase_pct": 15,
        "forex_pressure_estimate": "moderate",
    }
}

def run_scenario(scenario_type, duration_days, current_state):
    params = SCENARIO_PARAMETERS[scenario_type]
    india_daily_import_mmt = 0.56
    hormuz_dependent_share = 0.42

    if scenario_type.startswith("HORMUZ"):
        affected_volume_per_day = (
            india_daily_import_mmt
            * hormuz_dependent_share
            * (params["capacity_reduction_pct"] / 100)
        )
        total_supply_gap = affected_volume_per_day * duration_days
        current_reserve = current_state["spr_level_mmt"]
        days_until_critical = current_reserve / affected_volume_per_day

        price_impact = params["typical_price_impact_per_barrel"]
        additional_cost = price_impact * 365 * india_daily_import_mmt * 7.33 * (duration_days / 365)

        normal_freight = 2.5
        disrupted_freight = normal_freight * params["freight_multiplier"]
        additional_freight = (disrupted_freight - normal_freight) * affected_volume_per_day * duration_days * 7.33

        return {
            "supply_gap_mmt": round(total_supply_gap, 2),
            "days_until_critical": round(days_until_critical, 1),
            "price_impact_per_barrel": price_impact,
            "additional_import_cost_usd_bn": round(additional_cost, 2),
            "additional_freight_cost_usd_bn": round(additional_freight, 2),
            "alternative_routes": params.get("alternate_routes", []),
            "recommended_actions": generate_recommendations(scenario_type, total_supply_gap, current_state)
        }
```

> **Key:** Calibrate multipliers using historical EIA data from actual Gulf disruptions (1990, 2003, 2011, 2020). Show the calibration data to judges. This is the difference between a credible model and a "random numbers generator."

---

## 14. Procurement Optimization

### Real Linear Programming Formulation

**Objective:**
```
Minimize: Σ (price_cif[i,j] + risk_penalty[i,j]) × volume[i,j]

WHERE:
  i = supplier (Russia, Saudi Arabia, Iraq, USA, Nigeria, ...)
  j = route (Hormuz, Cape, Direct, ...)
```

**Constraints:**
1. `Σ volume[i,j] = target_volume` — meet India's import requirement
2. `volume[i,j] <= available_capacity[i,j]` — supplier capacity limits
3. `volume[i,j] = 0` if `is_sanctioned[i] = True` — sanctions compliance
4. `volume[i,j] = 0` if `is_route_disrupted[j] = True` — operational constraint
5. Refinery crude compatibility requirements met
6. `risk_score[i,j] <= max_risk_tolerance` — risk limit
7. `Σ volume[russia,j] <= russia_cap` — concentration limit

**Risk penalty:**
```
risk_penalty[i,j] = λ × route_risk[i,j] × price_cif[i,j]
```
where `λ` is a risk aversion parameter adjustable in the UI.

### Implementation

```python
from scipy.optimize import linprog
import numpy as np

def optimize_procurement(suppliers, routes, target_volume_mmt,
                          disrupted_routes, sanctioned_suppliers,
                          risk_tolerance=0.5):
    n = len(suppliers) * len(routes)

    c = []
    for s in suppliers:
        for r in routes:
            if s in sanctioned_suppliers or r in disrupted_routes:
                c.append(1e9)  # effectively exclude
            else:
                cost = s.price_cif + risk_tolerance * s.risk_score * r.risk_score * s.price_cif
                c.append(cost)

    A_eq = [[1] * n]
    b_eq = [target_volume_mmt]
    bounds = [(0, s.capacity * r.availability) for s in suppliers for r in routes]

    result = linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
    return parse_optimization_result(result, suppliers, routes)
```

This is real optimization. Judges who are technically strong will recognize it. This separates you from teams that just hardcode "Saudi Arabia: recommended."

---

## 15. Risk & Explainability

### Evidence Chain (Critical for Credibility)

Every risk score displayed must have a drilldown — **the UI must never show just a number.**

```
ROUTE RISK: Hormuz — Score: 0.78 (HIGH)  [Last updated: 10 min ago]
         ↓
WHY?
├── Geopolitical Component: 0.82
│   ├── [2026-08-19] "IRGC naval drills near Hormuz strait" — severity: 0.7
│   │   Source: Reuters | Classified by AI | Verified: No | Confidence: 0.75
│   ├── [2026-08-17] "US sanctions on 3 Iranian tankers" — severity: 0.6
│   │   Source: OFAC | Verified: Yes | Confidence: 1.0
│   └── Base country risk (Iran): 0.85
│
├── Logistics Component: 0.65
│   ├── Historical disruption frequency (last 5 years): 0.45
│   ├── Insurance war-risk zone: YES (Lloyd's JWC) — +0.20
│   └── Current vessel traffic anomaly: NOT DETECTED
│
└── Seasonal Component: 0.55
    ├── Monsoon season effect on Arabian Sea: Low
    └── Historical August disruption frequency: 0.35

CONFIDENCE: 0.72
DATA FRESHNESS: Geopolitical (10 min ago), Prices (today), AIS (historical baseline)
```

A risk score of 0.78 with no explanation is meaningless and will be dismissed by judges. An evidence chain that drills to source articles, timestamps, and verified sources is genuinely impressive and practically useful.

---

## 16. Final System Architecture

### Version A — Hackathon MVP (Build This)

```
┌─────────────────────────────────────────────────────────────┐
│                     REACT FRONTEND                          │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐│
│  │  Risk Map    │ │  Scenario    │ │  Procurement         ││
│  │  (Leaflet)   │ │  Engine UI   │ │  Recommendations     ││
│  │  Route risk  │ │  Parameters  │ │  with evidence chain ││
│  └──────────────┘ └──────────────┘ └──────────────────────┘│
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐│
│  │  Event Feed  │ │  Price       │ │  SPR Dashboard       ││
│  │  (live news) │ │  Dashboard   │ │  3 locations +       ││
│  │  classified  │ │  Brent/Dubai │ │  drawdown schedule   ││
│  └──────────────┘ └──────────────┘ └──────────────────────┘│
└────────────────────────┬────────────────────────────────────┘
                         │ HTTPS REST API
┌────────────────────────▼────────────────────────────────────┐
│                  FASTAPI BACKEND                             │
│  /events  /risk  /scenario  /recommend  /prices  /reserve   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │             BACKGROUND SCHEDULERS (APScheduler)     │   │
│  │  GDELT(15min) | ACLED(daily) | EIA/RBI(daily)      │   │
│  │  NewsAPI(hourly) | OFAC(daily)                      │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                   AI PIPELINE                       │   │
│  │  LLM Extraction → Validation → Risk Update → Alert │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │               ENGINES                               │   │
│  │  Risk Engine | Scenario Engine | LP Optimizer      │   │
│  └─────────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│         PostgreSQL + PostGIS + TimescaleDB                  │
│   entities | events | risk_scores | prices | scenarios      │
│   routes | refineries | suppliers | recommendations         │
└─────────────────────────────────────────────────────────────┘
                         +
┌─────────────────────────────────────────────────────────────┐
│           Redis Cache (risk scores, API responses)          │
└─────────────────────────────────────────────────────────────┘
```

### Version B — Stronger Pilot (Post-Hackathon)

Add: Real AIS data feed (Spire/ExactEarth), proper entity resolution, GDELT + commercial news, XGBoost disruption model trained on 5 years of data, multi-user auth, API for enterprise integration, proper monitoring.

### Version C — Production Enterprise

Add: Full graph database (Neo4j) for entity resolution, multi-source AIS with satellite coverage, Kafka for event streaming, ML model monitoring/retraining pipeline, SOC 2 compliance, multi-tenant architecture, integrations with SAP/Oracle ERP.

---

## 17. Technology Stack

### Final Minimal Stack

| Technology | Purpose | Why Selected | Free? | Phase 1? |
|---|---|---|---|---|
| Python 3.11 | Backend | Universal, fast | ✅ | MUST |
| FastAPI | REST API | Fast, auto-docs, async | ✅ | MUST |
| PostgreSQL 16 | Primary DB | PostGIS + TimescaleDB | ✅ | MUST |
| PostGIS | Geospatial queries | Route proximity, map queries | ✅ | MUST |
| Redis 7 | API cache | Fast response, rate limiting | ✅ | SHOULD |
| React 18 | Frontend | Component-based, ecosystem | ✅ | MUST |
| Leaflet.js | Map viz | Lightweight, free tiles | ✅ | MUST |
| Recharts | Charts | React-native charting | ✅ | SHOULD |
| APScheduler | Background jobs | Python-native scheduler | ✅ | MUST |
| NetworkX | Graph algorithms | Route pathfinding | ✅ | MUST |
| Anthropic API | News classification | Best extraction quality | ~Free | MUST |
| scipy/PuLP | LP optimization | Real optimization | ✅ | MUST |
| pandas | Data processing | PPAC CSV parsing | ✅ | MUST |
| GDELT | Geopolitical events | Free, real-time, structured | ✅ | MUST |
| ACLED API | Conflict events | Free, authoritative | ✅ | MUST |
| EIA API | Crude prices | Free, authoritative | ✅ | MUST |
| OFAC API | Sanctions data | Free, official | ✅ | MUST |
| RBI API | FX rates | Free, authoritative | ✅ | MUST |
| Docker | Deployment | Containerization | ✅ | SHOULD |
| Render/Railway | Cloud hosting | Free tier, easy deploy | ✅ Free tier | SHOULD |

### ❌ Do NOT Add

- Kafka — overkill, APScheduler is sufficient
- MongoDB — PostgreSQL JSONB handles it
- Neo4j — NetworkX in Python handles graph pathfinding
- ClickHouse — unnecessary at this data volume
- Kubernetes — cloud-managed container is sufficient
- dbt/Airflow — Python scripts are fine
- Blockchain — absolutely not

---

## 18. Cost Analysis

### Phase 1 Prototype (Hackathon)

| Component | Service | Cost |
|---|---|---|
| Database | Supabase free tier (PostgreSQL) | $0 |
| Backend hosting | Render.com free tier | $0 |
| Frontend hosting | Vercel free tier | $0 |
| LLM API | Anthropic free credits / Claude API | ~$2–5 total |
| News | NewsAPI free tier + RSS | $0 |
| GDELT | Free | $0 |
| ACLED | Free (academic) | $0 |
| EIA API | Free | $0 |
| Map tiles | OpenStreetMap (Leaflet default) | $0 |
| AIS data | Historical only (free sources) | $0 |
| **TOTAL** | | **~$5** |

### Phase 2 Pilot (Enterprise Proof-of-Concept)

| Component | Cost/Month |
|---|---|
| PostgreSQL (managed) | $50–200 |
| API server (2 vCPU, 4GB) | $40–100 |
| LLM API (production volume) | $200–500 |
| NewsAPI production | $449 |
| AIS data (cheapest tier) | $500–2,000 |
| **TOTAL** | **~$1,200–3,300/month** |

### Enterprise Production

| Component | Cost/Month |
|---|---|
| AIS full feed (Spire/ExactEarth) | $5,000–50,000 |
| Bloomberg/Reuters integration | $20,000+ |
| Commodity price feeds | $5,000–20,000 |
| Infrastructure | $5,000–20,000 |
| ML compute | $2,000–10,000 |
| **TOTAL** | **$37,000–100,000+/month** |

---

## 19. MVP Scope

### Feature Classification

| Feature | Classification | Reason |
|---|---|---|
| Real-time news classification (LLM) | ✅ MUST HAVE | Core AI component, cheap, fast to build |
| Route risk scoring (explainable) | ✅ MUST HAVE | Core value proposition |
| India refinery/port/supplier map | ✅ MUST HAVE | India-specific differentiation |
| Scenario engine (5 preset scenarios) | ✅ MUST HAVE | Demo impact |
| Procurement LP optimization | ✅ MUST HAVE | Real technical depth |
| SPR dashboard | ✅ MUST HAVE | India-specific, high relevance |
| Evidence chain / explainability | ✅ MUST HAVE | Credibility differentiator |
| Crude price feed (EIA) | ✅ MUST HAVE | Easy, free, real data |
| OFAC sanctions integration | ✅ MUST HAVE | Easy, free, real data |
| Russian crude risk model | ⚠️ SHOULD HAVE | Strong India differentiator |
| Weather disruption overlay | ⚠️ SHOULD HAVE | IMD data, easy to add |
| Historical scenario calibration | ⚠️ SHOULD HAVE | Makes numbers defensible |
| XGBoost disruption classifier | 💡 NICE TO HAVE | Only if time permits (very last) |
| Real-time AIS vessel tracking | ❌ DO NOT BUILD | Paid, time-consuming, fakeable |
| 3D supply chain visualization | ❌ DO NOT BUILD | Cosmetic, not functional |
| Mobile app | ❌ DO NOT BUILD | No time |
| Multi-user auth | ❌ DO NOT BUILD | Phase 2 |
| Full entity resolution engine | ❌ DO NOT BUILD | Months of work |
| True discrete-event simulation | ❌ DO NOT BUILD | Months of work |
| Kafka streaming | ❌ DO NOT BUILD | Overkill |

---

## 20. Development Plan

### Day-by-Day Plan (Aug 19 Evening → Aug 23, 4:00 PM IST)

---

#### 🗓️ Day 1 — August 19 (Evening, ~4 hours)
**Goal: Foundation running**

| Task | Hours | Risk | Fallback |
|---|---|---|---|
| Initialize Git repo, Python venv, FastAPI skeleton | 0.5 | Low | — |
| Set up PostgreSQL (local Docker or Supabase) | 0.5 | Low | SQLite if Supabase fails |
| Run full schema DDL | 0.5 | Low | — |
| Seed India data: 20 refineries, 10 ports, 50 routes, 8 suppliers | 1.5 | Low | Start with 5 of each |
| Register for ACLED API, EIA API, NewsAPI | 0.5 | Low | GDELT only as fallback |
| Test GDELT API call | 0.5 | Medium | Use NewsAPI only |

---

#### 🗓️ Day 2 — August 20 (Full day, ~10 hours)
**Goal: Data pipeline + LLM classification running**

| Task | Hours | Risk | Fallback |
|---|---|---|---|
| Write GDELT poller (15-min, Middle East events) | 1.5 | Medium | Daily batch |
| Write ACLED poller (daily fetch, filter by region) | 1.0 | Low | — |
| Write EIA crude price poller | 1.0 | Low | Static prices |
| Write RBI FX poller | 0.5 | Low | Static rate |
| Write OFAC sanctions checker | 1.0 | Low | — |
| Write LLM extraction service (Anthropic API) | 1.5 | Medium | Rule-based fallback |
| Test: news article → classified event → DB | 1.0 | High | Hardcoded test events |
| Implement risk scoring engine (weighted formula) | 2.0 | Medium | Simple lookup table |

> **Checkpoint:** By end of Day 2, the backend should be ingesting real news, classifying events with LLM, and calculating route risk scores.

---

#### 🗓️ Day 3 — August 21 (Full day, ~10 hours)
**Goal: Scenario engine + Optimization + Frontend core**

| Task | Hours | Risk | Fallback |
|---|---|---|---|
| Build scenario engine (5 preset scenarios) | 2.0 | Medium | 2 scenarios only |
| Build LP procurement optimizer (scipy) | 2.0 | High | Simple ranking algorithm |
| Test scenario → supply gap → recommendations pipeline | 1.0 | Medium | Hardcode one scenario |
| Set up React + Leaflet map | 1.5 | Low | — |
| Plot India map: refineries, ports, routes, SPR | 1.0 | Low | — |
| Add risk color coding to routes | 0.5 | Low | — |
| Build event feed component | 0.5 | Low | — |
| Build risk score display with evidence drilldown | 1.5 | Medium | Simple table |

> **Checkpoint:** By end of Day 3, scenario simulation should work end-to-end and map should show India's network with risk overlays.

---

#### 🗓️ Day 4 — August 22 (Full day, ~10 hours)
**Goal: Polish, integrate, deploy, test**

| Task | Hours | Risk | Fallback |
|---|---|---|---|
| Build procurement recommendation panel | 1.5 | Medium | Simple ranked list |
| Build SPR dashboard | 1.0 | Low | — |
| Add crude price chart (EIA data) | 1.0 | Low | Static historical |
| Evidence chain UI (click risk score → see why) | 1.5 | Medium | Tooltip |
| Deploy backend (Render.com or Railway) | 1.0 | Medium | Local ngrok for demo |
| Deploy frontend (Vercel) | 0.5 | Low | — |
| End-to-end integration testing | 1.0 | High | Fix highest-priority bugs |
| Write README.md | 1.0 | Low | — |
| Create architecture diagram (Excalidraw) | 0.5 | Low | — |
| Write solution overview document | 0.5 | Low | — |

> **Checkpoint:** By end of Day 4, deployed and running. All core features working.

---

#### 🗓️ Day 5 — August 23 (Morning, ~6 hours until 4:00 PM IST)
**Goal: Demo video + Final submission**

| Task | Hours | Risk | Fallback |
|---|---|---|---|
| Final bug fixes from overnight testing | 1.0 | Low | — |
| Record demo video (3–5 minutes) | 1.5 | Low | — |
| Edit demo video (simple cuts, titles, voiceover) | 1.0 | Low | No editing, raw recording |
| Final README review and push | 0.5 | Low | — |
| Submit on Unstop platform | 0.5 | Low | — |
| Buffer for unexpected issues | 1.5 | — | — |

---

## 21. Demo Strategy

### 3–5 Minute Demo Script

**[00:00–00:30] Context Setting**
> "India imports 88% of its crude oil. 42% transits the Strait of Hormuz. Strategic reserves last 9.5 days. When geopolitical events disrupt these routes, India's oil companies and government have no integrated system to detect the risk, model the impact, and act. This is PETRAS — Petroleum Trade Resilience and Advisory System."

**[00:30–01:15] Live Event Detection**
Show the event feed panel on screen.
> "Right now, the system is monitoring GDELT and ACLED for geopolitical signals. Here — the system detected this news item 15 minutes ago, classified it as a MILITARY_ACTION event near the Strait of Hormuz with severity 0.68, and automatically updated the route risk score."

Show the risk score changing on the map.

**[01:15–02:00] Risk Map**
> "On this map, you can see India's full crude oil supply network. Red routes are high-risk. Each route risk score is explained — click on Hormuz — you see the contributing events, their source, timestamp, and confidence. This is not a black box."

Show the evidence drilldown panel.

**[02:00–03:00] Scenario Simulation**
> "Now I'll run a scenario: Hormuz full closure for 30 days."

[Click "Run Scenario" button]

> "Within seconds, the system calculates: India loses 4.2 MMT of crude in 30 days. Current SPR covers 9.5 days. After day 9, refinery feed rates drop. The additional import cost is $3.8 billion. Freight costs spike 3x on Cape of Good Hope rerouting."

Show scenario results panel with numbers.

**[03:00–04:00] Procurement Recommendations**
> "The optimization engine runs linear programming across India's supplier and route options to find the minimum-cost, minimum-risk procurement mix that satisfies refinery requirements and avoids sanctioned entities."

Show recommendation panel: ranked suppliers with cost, risk, transit time, refinery compatibility.

> "Notice: Russian Urals is ranked 4th because the Cape-routed freight adds $4.20/barrel and shadow fleet risk is elevated. Saudi Arab Light via Cape route is ranked 1st — higher base price but lower total risk."

**[04:00–04:30] SPR Dashboard**
> "Finally, the system models optimal SPR drawdown schedule: release 0.5 MMT/day from Padur, maintain Visakhapatnam as emergency reserve, procure replacement cargo from USA within 14 days."

Show SPR dashboard with drawdown timeline.

**[04:30–05:00] Close**
> "PETRAS integrates real geopolitical intelligence from GDELT, ACLED, and OFAC with India's actual refinery network, SPR data, and crude supply routes. It uses LLM-based extraction for news intelligence, linear programming for procurement optimization, and a parametric scenario engine calibrated on historical Gulf disruption data. Every recommendation is traceable to a source event."

---

## 22. Data vs Simulation Honesty

### What is Real vs Simulated in the Demo

| Data Component | Type | Label in UI |
|---|---|---|
| GDELT/ACLED events | **REAL (live)** | "Live geopolitical feed" |
| EIA crude prices | **REAL (live, 1-day delay)** | "EIA daily prices" |
| RBI FX rates | **REAL (live)** | "RBI daily rate" |
| OFAC sanctions | **REAL (live)** | "OFAC sanctions database" |
| India refinery data | **REAL (historical PPAC)** | "PPAC verified data" |
| SPR location/capacity | **REAL (ISPRL public data)** | "ISPRL official data" |
| Vessel positions | **HISTORICAL BASELINE** | "Historical route baseline" |
| Route risk scores | **CALCULATED** | "AI risk model" |
| Scenario impacts | **PARAMETERIZED MODEL** | "Scenario simulation" |
| Procurement ranking | **REAL LP OPTIMIZATION** | "LP optimization" |
| Supply gap estimates | **CALCULATED from real inputs** | "Derived from PPAC data" |

> ⚠️ **NEVER say:** "Live vessel tracking showing 47 tankers in Hormuz right now" unless you have real AIS data.
>
> ✅ **DO say:** "Historical tanker traffic patterns show the Hormuz corridor typically handles X vessels/day — our scenario engine models impact on this baseline."

Judges respect honesty. Fake real-time claims are caught immediately.

---

## 23. Commercial Viability

### Who Would Actually Pay

**1. ISPRL (Indian Strategic Petroleum Reserves Limited)**
Government entity responsible for SPR management. Currently uses no real-time risk intelligence system. A decision-support tool for drawdown timing could be genuinely valuable.
- **Problem:** Government procurement is slow (3–5 year cycle), requires GEM portal listing, vendor certification.

**2. IOC / BPCL / HPCL Crude Trading Desks**
Most realistic early customers. They have Bloomberg terminals already, but an India-specific procurement optimization tool focused on their specific refinery network could complement it.
- **Price point:** ₹50–200 lakh/year for an enterprise tool is realistic.
- **Problem:** They will want deep integration with existing ERP systems (SAP). Sales cycle: 12–24 months.

**3. MoPNG (Ministry of Petroleum & Natural Gas)**
Policy-level tool for strategic planning.
- **Problem:** Government procurement, political considerations, tender process.

**4. Indian Energy Traders (Nayara, MRPL)**
Commercial interest in price risk and supply optimization.

### Business Model Options

| Model | Details |
|---|---|
| SaaS subscription | ₹25–50 lakh/year for Indian OMCs |
| Government contract | ₹2–5 crore for custom deployment |
| API licensing | Integration with existing tools |

### Verdict

> **This has commercial potential, but it is not a consumer product or a quick startup. It requires domain expertise, regulatory navigation, and long enterprise sales cycles. It is a govtech/B2B play. The hackathon prototype can serve as a compelling proof-of-concept for potential pilots.**

---

## 24. Hackathon Judge Assessment

### Projected Scores (if built as recommended)

| Criterion | Score | Reasoning |
|---|---|---|
| Problem relevance | 9/10 | India energy security is genuinely urgent |
| Innovation | 7/10 | Combination is novel; individual components exist |
| Technical depth | 8/10 | LP optimization + LLM extraction + real data sources |
| AI credibility | 8/10 | Hybrid model is more credible than "LLM does everything" |
| Data credibility | 8/10 | Real GDELT, ACLED, EIA, PPAC data is verifiable |
| India specificity | 9/10 | Refinery matrix, PPAC data, ISPRL, Russian crude model |
| Feasibility | 7/10 | Tight deadline but achievable with discipline |
| Demo quality | 8/10 | Scripted demo with real data is compelling |
| Scalability | 6/10 | Basic architecture; production path is clear but not built |
| Commercial potential | 7/10 | Real market but slow-moving |
| Differentiation | 8/10 | India-specific downstream modeling is genuinely absent elsewhere |
| Explainability | 9/10 | Evidence chain is explicitly built |

### Why a Judge Might Reject This

1. **"The scenario engine numbers look made up"** — Mitigate by showing calibration data from historical Gulf War II or Houthi disruptions
2. **"The AI is just calling ChatGPT"** — Mitigate by explaining the hybrid pipeline; LLM is one component, LP and rule engine are others
3. **"You don't have real AIS data"** — Honest answer: "We use historical route baselines and are explicit about this in the UI"
4. **"How is this different from a Bloomberg terminal with India data?"** — Procurement optimization + SPR drawdown modeling + India refinery compatibility matrix doesn't exist in Bloomberg
5. **"Did you actually train any model?"** — Have the XGBoost trained on ACLED+EIA data ready even if it's a backup; having it trained and evaluated (with accuracy metrics) adds credibility

---

## 25. Red Flags to Avoid

### Things That Will Make Your Project Look Fake

| Red Flag | Why It's a Problem |
|---|---|
| Claiming live AIS vessel tracking without paid subscription | Judges who know this space know it costs $5K+/month |
| Risk scores that never change | If your "live" dashboard shows the same numbers for 10 minutes, it's obviously hardcoded |
| "AI-predicted" numbers with no model evaluation metrics | "87% accuracy" with no confusion matrix and no dataset description |
| Using LLM for everything including risk scoring | LLM should NOT be computing route risk scores — that's what formulas are for |
| "Digital twin" that is just a static map | If you can't run a scenario that changes the network state, it's not a twin |
| Procurement recommendations that always say the same thing | The optimizer must produce different outputs for different scenarios |
| Economic impact numbers with wrong order of magnitude | India imports $100B+ crude/year; "$500M" or "$50T" for a 30-day disruption are implausible |
| Too many technologies in the stack that aren't used | If README says "Kafka, Neo4j, Kubernetes, Spark" and the code has none, judges notice |
| Claiming a "PPAC real-time API" | PPAC doesn't have a real-time API — claiming so is fabrication |
| Confidence intervals that are perfectly round numbers | "87% confidence" looks fake; "0.73 confidence with source" looks real |

---

## 26. Build vs Don't Build Table

| Component | Build Now? | Why | Complexity | Risk |
|---|---|---|---|---|
| PostgreSQL schema | ✅ YES | Foundation | Low | Low |
| India data seeding | ✅ YES | Core to India-specificity | Low | Low |
| GDELT poller | ✅ YES | Free, real-time geopolitical data | Medium | Medium |
| ACLED poller | ✅ YES | Free conflict events | Low | Low |
| EIA price poller | ✅ YES | Free crude prices | Low | Low |
| RBI FX poller | ✅ YES | Free, real | Low | Low |
| OFAC sanctions check | ✅ YES | Free, important for procurement | Low | Low |
| LLM news classifier | ✅ YES | Core AI component | Medium | Medium |
| Risk scoring engine | ✅ YES | Core value | Medium | Low |
| Scenario engine (5 scenarios) | ✅ YES | Demo impact | Medium | Medium |
| LP procurement optimizer | ✅ YES | Real technical depth | High | Medium |
| SPR dashboard | ✅ YES | India-specific | Low | Low |
| Evidence chain UI | ✅ YES | Credibility | Medium | Low |
| Leaflet map with risk overlays | ✅ YES | Visual impact | Medium | Low |
| FastAPI backend | ✅ YES | Foundation | Low | Low |
| React frontend | ✅ YES | Foundation | Medium | Low |
| Redis cache | ⚠️ SHOULD | Performance | Low | Low |
| XGBoost disruption model | 💡 OPTIONAL | Nice if time permits — Day 4 evening only | High | High |
| Real-time AIS tracking | ❌ NO | Costs $5K+/month to do honestly | Very High | Very High |
| Neo4j graph database | ❌ NO | Overkill, NetworkX sufficient | High | High |
| Kafka streaming | ❌ NO | APScheduler is enough | High | High |
| 3D visualization | ❌ NO | Cosmetic, no functional value | High | Medium |
| Mobile app | ❌ NO | No time | Very High | High |
| Multi-user auth | ❌ NO | Phase 2 | Medium | Low |
| Full entity resolution | ❌ NO | Months of work | Very High | Very High |

---

## 27. Final CTO Recommendation

### Final 10 Questions

| # | Question | Answer |
|---|---|---|
| 1 | Can a student team realistically build this before the deadline? | Yes, but ONLY with the exact scope defined above. Every feature beyond that list will cause you to miss the deadline. |
| 2 | What is the single hardest technical component? | The LP procurement optimizer with real constraints (sanctions, crude compatibility, capacity limits). Fallback: simple weighted ranking if LP fails. |
| 3 | What is the single biggest data problem? | Real-time AIS data is unavailable without payment. Be upfront about using historical route baselines. Do not fake live vessel tracking. |
| 4 | What is the single biggest market problem? | Indian government and PSU sales cycles are 12–24 months. Not a quick-to-monetize product. For the hackathon, it's fine — it's a genuine enterprise B2B opportunity. |
| 5 | What should you remove from the original idea? | Full 3D Digital Twin, real-time AIS, entity resolution engine, ML model training from scratch. Either fakes or impossible in 4 days. |
| 6 | What should you add? | Russian crude shadow fleet risk model — unique to India, defensible, not in any Western platform. Historical calibration data shown openly to judges. |
| 7 | What is your strongest differentiator? | India-specific refinery crude compatibility matrix combined with LP optimization that incorporates Indian import route structure, PPAC data, and ISPRL SPR levels. No other platform does this. |
| 8 | What is the minimum viable demo? | Live event detection → risk score change → one scenario run (Hormuz) → LP procurement recommendation with evidence chain → SPR drawdown schedule. 3 minutes, all real data. |
| 9 | What would make judges believe the product is real? | Evidence chain showing source article → extracted event → risk formula → recommendation. Real GDELT/ACLED events visible. PPAC data labeled clearly. LP output that changes meaningfully when scenario parameters change. Historical calibration numbers with sources cited. |
| 10 | What would make judges think it is just a flashy AI dashboard? | Risk scores that don't change. Procurement that always recommends Saudi Arabia. Economic impact numbers without derivation. "Live AIS tracking" without real AIS. "Trained ML model" without evaluation metrics. Too many technologies listed in README that don't appear in code. |

---

## Final Answer in One Page

**WHAT:**
PETRAS — Petroleum Trade Resilience & Advisory System. An India-specific energy supply chain risk intelligence and procurement optimization tool for Indian refiners and government energy agencies.

**TARGET USER:**
IOC/BPCL/HPCL crude procurement desks, ISPRL, MoPNG advisors.

**STACK:**
Python + FastAPI + PostgreSQL + PostGIS + Redis + React + Leaflet + Anthropic API + scipy LP + APScheduler.

**DATA:**
GDELT (live events, free) + ACLED (conflict events, free) + EIA API (crude prices, free) + RBI (FX, free) + OFAC (sanctions, free) + PPAC historical CSVs (India imports, free) + ISPRL public reports (SPR, hardcoded). **NO FAKE AIS.**

**AI APPROACH:**
1. LLM (Claude Haiku) extracts structured events from news
2. Rule-based weighted formula calculates explainable route/country/supplier risk
3. Parametric scenario engine propagates disruption impact (calibrated on Gulf War II + Houthi historical data from EIA)
4. Linear programming (scipy) optimizes procurement across available supplier-route combinations
5. LLM generates natural language recommendation explanation

Every output is traceable to a source.

**MVP FEATURES:**
- Live geopolitical event feed with LLM classification
- India supply network map (20 refineries, 8 major ports, 15 key routes, 3 SPR locations)
- Route risk scores with evidence drilldown
- 5-scenario simulation engine (Hormuz full/partial, Red Sea, Russia supply loss, price spike)
- LP procurement optimizer with sanctions/compatibility constraints
- SPR drawdown schedule
- Crude price + FX dashboard

**DIFFERENTIATORS:**
1. India refinery-specific crude compatibility matrix in procurement optimization — no Western platform has this
2. PPAC + ISPRL + ACLED pipeline calibrated to India's actual import structure
3. Russian crude shadow fleet risk explicitly modeled for India's unique ~37% Russia dependency

**DEMO (5 minutes):**
`00:00` Live event detected via GDELT →
`01:00` Route risk updates with evidence chain visible →
`02:00` Hormuz 30-day closure scenario runs →
`03:00` Supply gap + SPR pressure shown →
`04:00` LP optimizer produces ranked procurement recommendations →
`04:30` SPR drawdown schedule

All explainable. All traceable to real sources.

**COST:** ~$5 total for demo using free tiers and Anthropic API.

**VERDICT:** This is buildable, India-relevant, technically credible, and commercially meaningful. The differentiation is real. The data strategy is honest. The AI is hybrid and explainable.

> **Ship it.**

---

*Report generated for hackathon Phase 1 submission | Deadline: 23 August 2026, 4:00 PM IST*
*All data sources verified as of report date. Verify API availability before implementation.*
