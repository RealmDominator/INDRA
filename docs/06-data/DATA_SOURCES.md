# INDRA — Data Sources

> Source: PETRAS Analysis §6, §7; INDRA Master Report §7
>
> Every data source used by INDRA must be classified, documented, and its limitations acknowledged.
>
> **Revision:** Post-review corrections. Updated classification to data semantic system. Added price/FX asynchronous architecture.

---

## Source Classification Framework (Data Semantic)

| Classification | Definition | UI Badge | Example |
|---|---|---|---|
| **OBSERVED** | Data directly fetched from an external API/feed | Green badge | EIA crude prices, GDELT events, OFAC sanctions, RBI FX rate |
| **DERIVED** | Calculated from observed values using a documented formula | Blue badge | Risk scores, supply gaps, INR prices, procurement rankings |
| **HISTORICAL_CALIBRATED** | Parameter derived from analysis of historical events | Gray badge | PPAC import shares, price impact multipliers, freight ratios |
| **ASSUMED** | Configuration/user assumption not derived from data | Orange badge | Risk weights, compatibility estimates, freight multiplier |
| **SIMULATED** | Synthetic state generated for scenario/demo purposes | Amber badge + ⚠ | Demo fixture events, scenario disruptions |

---

## Live / Near-Real-Time Sources

### GDELT Project ✅ USE

| Field | Detail |
|---|---|
| URL | gdeltproject.org |
| Cost | FREE |
| API / Access | BigQuery (Google), direct download, REST API |
| Update Frequency | 15-minute updates |
| Coverage | Global news event database |
| Phase 1 Strategy | Poll GDELT API every 15 minutes for Middle East / energy-related events |
| Limitations | Noisy; requires keyword filtering. Not all events are energy-relevant. |
| Registration | None required for direct download; Google Cloud account for BigQuery |

### OFAC Sanctions ✅ USE

| Field | Detail |
|---|---|
| URL | sanctionslist.treasury.gov |
| Cost | FREE |
| API | YES — XML/CSV download, API access |
| Update Frequency | Multiple times per day |
| Coverage | US sanctions designations (SDN list) |
| Phase 1 Strategy | Daily poll; check suppliers/entities against SDN list |
| Limitations | US-centric. Does not cover EU/UN sanctions directly. |
| Registration | None required |

### RSS News Feeds ✅ USE

| Field | Detail |
|---|---|
| Sources | Reuters Energy, Al Jazeera Middle East, BBC World, etc. |
| Cost | FREE |
| Update Frequency | Minutes |
| Phase 1 Strategy | Hourly poll of curated RSS feeds with energy/geopolitics keyword filter |
| Limitations | Unstructured text; requires LLM extraction |

---

## Recent / Periodic Sources

### ACLED (Armed Conflict Location & Event Data) ✅ USE

| Field | Detail |
|---|---|
| URL | acleddata.com |
| Cost | FREE for research and non-commercial use |
| API | YES — acleddata.com/data-export-tool/ |
| Update Frequency | Weekly, with near-real-time for some regions |
| Coverage | Excellent for Middle East conflict events |
| Phase 1 Strategy | Daily poll; filter by region (Middle East, Horn of Africa) |
| Registration | Required — apply for API access |
| Limitations | Weekly update cycle means events can be 1–7 days delayed |

### EIA (US Energy Information Administration) ✅ USE

| Field | Detail |
|---|---|
| URL | api.eia.gov |
| Cost | FREE |
| API | YES — REST API with API key |
| Update Frequency | Daily/weekly depending on series |
| Coverage | Global crude oil prices (Brent, WTI), production, inventories |
| Phase 1 Strategy | Daily poll for Brent/WTI prices; weekly for inventories |
| Registration | Required — register for free API key at api.eia.gov |
| Limitations | US-focused; international data has some delay |

### RBI (Reserve Bank of India) ✅ USE

| Field | Detail |
|---|---|
| URL | rbi.org.in/statistics |
| Cost | FREE |
| API | YES — statistical data API |
| Update Frequency | Daily (business days) |
| Coverage | USD/INR exchange rates (reference rate) |
| Phase 1 Strategy | Daily poll for USD/INR rate |
| Registration | None required |
| Limitations | Reference rate only; does not reflect real-time FX market |

### NewsAPI ⚠ USE WITH CAVEAT

| Field | Detail |
|---|---|
| URL | newsapi.org |
| Cost | FREE tier available |
| API | YES |
| Update Frequency | **24-hour delay on free plan** |
| Phase 1 Strategy | Use free tier with explicit delay acknowledgment |
| Registration | Required |
| Limitations | Free tier has 24-hour delay, 100 requests/day, and only returns articles from the past month. **Do NOT claim "real-time" news from NewsAPI free tier.** |

---

## Historical / Seeded Sources

### PPAC (Petroleum Planning & Analysis Cell) ✅ USE HISTORICAL

| Field | Detail |
|---|---|
| URL | ppac.gov.in |
| Cost | FREE |
| Format | PDF reports, CSV/Excel data tables |
| Update Frequency | Monthly reports, annual summaries |
| Coverage | India crude import volumes by source, refinery throughput, product output |
| Phase 1 Strategy | Download and parse all available historical files; load into database as seed data |
| Limitations | **No real-time API.** Data is published as PDFs/spreadsheets. Claiming "real-time PPAC data" is fabrication. |

### ISPRL (Indian Strategic Petroleum Reserves Ltd) ✅ USE HISTORICAL

| Field | Detail |
|---|---|
| URL | isprl.gov.in |
| Cost | FREE |
| Format | Annual reports, press releases |
| Coverage | SPR location, capacity data |
| Phase 1 Strategy | Hardcode 3 SPR locations from public reports (Visakhapatnam, Mangalore, Padur) |
| Limitations | Current fill levels are not publicly disclosed in real-time. Use capacity as baseline. |

### Data.gov.in ✅ USE

| Field | Detail |
|---|---|
| URL | data.gov.in |
| Cost | FREE |
| API | YES |
| Coverage | Various petroleum datasets from Indian government |
| Phase 1 Strategy | Pull relevant petroleum datasets via API |

### World Bank Commodity Data ✅ USE FOR HISTORICAL

| Field | Detail |
|---|---|
| URL | worldbank.org/commodities |
| Cost | FREE |
| API | YES |
| Update Frequency | Monthly |
| Coverage | Historical commodity prices |
| Phase 1 Strategy | Good source for historical training data and calibration |

### IMD / NOAA Weather ⚠ SHOULD HAVE

| Field | Detail |
|---|---|
| URL | IMD: mausam.imd.gov.in; NOAA: noaa.gov |
| Cost | FREE |
| Coverage | Cyclone warnings, maritime weather |
| Phase 1 Strategy | Weather disruption overlay if time permits |

---

## Unavailable / Not Used Sources

### AIS Vessel Tracking ❌ DO NOT CLAIM REAL-TIME

| Source | Cost | Reality |
|---|---|---|
| Spire Maritime | $5,000–$50,000/month | Enterprise only |
| ExactEarth | Similar pricing | Enterprise only |
| MarineTraffic API | ~$500/month commercial | Paid |
| VesselFinder | Freemium (delayed) | Demo-only quality |

**What CAN be used honestly:**
- Historical AIS route data for major India-bound crude corridors (pre-loaded)
- Marine Cadastre (marinecadastre.gov): FREE historical AIS data for US waters
- AIS Hub (aishub.net): Community AIS feed, some historical data available free

**Demo strategy:** Pre-load historical tanker route data. When running a scenario, animate route changes on pre-computed alternate paths. Label clearly as "scenario simulation on historical route data."

### Commercial Data Feeds ❌ NOT AVAILABLE

| Source | Cost | Status |
|---|---|---|
| Bloomberg Terminal | $20K+/year | Not available |
| Reuters Eikon / LSEG | $20K+/year | Not available |
| Platts / S&P Global | Enterprise pricing | Not available |
| Baltic Dirty Tanker Index (BDTI) | Baltic Exchange (paid) | Not available |
| Clarksons Freight | Paid | Not available |

---

## India-Specific Reference Data (for Seed Database)

### Indian Refineries (~20)

Source: PPAC Annual Report 2024-25, company annual reports.

Key refineries include: Jamnagar DTA (Reliance, 35.8 MMTPA), Jamnagar SEZ (Reliance, 22.8), Paradip (IOC, 15.0), Koyali (IOC, 13.7), Panipat (IOC, 15.0), BPCL Kochi (15.5), Mangalore (MRPL, 15.0), Bathinda (HPCL-Mittal, 11.25), Chennai (CPCL, 10.5), and others.

Full list with capacities and crude compatibility is documented in `research/research_report_1.md` §6.

### Indian Crude Import Sources (~FY2025)

| Country | Share | Primary Grades | Risk Profile |
|---|---|---|---|
| Russia | ~36–38% | Urals, ESPO | Sanctions risk (secondary), shadow fleet |
| Iraq | ~20–22% | Basrah Light/Heavy | Hormuz risk |
| Saudi Arabia | ~14–16% | Arab Light/Extra Light | Hormuz risk |
| UAE | ~5–6% | Murban | Hormuz risk |
| USA | ~5–6% | WTI, Eagle Ford | No transit risk |
| Kuwait | ~3–4% | Kuwait Export | Hormuz risk |
| Nigeria | ~2–3% | Bonny Light | Atlantic route |
| Others | ~8–10% | Various | Varies |

Source: PPAC monthly import data, approximate FY2025.

### Indian SPR Locations

| Location | Operator | State | Capacity (MMT) |
|---|---|---|---|
| Visakhapatnam | ISPRL | Andhra Pradesh | 1.33 |
| Mangalore | ISPRL | Karnataka | 1.50 |
| Padur | ISPRL | Karnataka | 2.50 |
| **Total** | | | **5.33** |

Source: ISPRL official website, MoPNG reports.

---

## Data Source Status Tracking

The system must maintain a `data_sources` table that tracks:
- Last successful fetch timestamp
- Current status (ACTIVE, STALE, ERROR, UNAVAILABLE)
- Update frequency

This information must be accessible via the `/health` API endpoint.

---

## Price / FX Asynchronous Architecture

Commodity prices (EIA) and FX rates (RBI) are ingested independently into separate database tables:

| Source | Table | Polling Frequency |
|---|---|---|
| EIA API | `commodity_prices` | Daily |
| RBI API | `fx_rates` | Daily |

**INR price derivation rule:**
1. Take the commodity price record with `source_timestamp` = T₁
2. Find the FX rate with the nearest `source_timestamp` ≤ T₁ (nearest-valid-prior rule)
3. Compute: `price_inr = price_usd × fx_rate`
4. Record both source timestamps in the evidence trail

This is a **query-time calculation**, not a stored column. The previous design using a PostgreSQL GENERATED column has been removed because EIA and RBI data arrive asynchronously at different timestamps.

---

## Step 4 — Acquisition Status (21 August 2026)

| Source | Step 4 Status | Details |
|---|---|---|
| **GDELT** | DEFERRED | Deferred to event-ingestion step. Not seed data. |
| **OFAC** | **ACQUIRED** | SDN list downloaded (5.6 MB raw). 1,674 energy-relevant entities extracted. |
| **RSS** | DEFERRED | Deferred to event-ingestion step. |
| **ACLED** | DEFERRED | Deferred to event-ingestion step. Requires registration. |
| **EIA** | REQUIRES_REGISTRATION | Free API key required (api.eia.gov). Bulk XLS download also requires programmatic access. No commodity price data acquired in Step 4. |
| **RBI** | PARTIAL | 3 real reference-rate data points documented. No bulk CSV API available. Full historical requires manual DBIE portal download. |
| **NewsAPI** | DEFERRED | Deferred to event-ingestion step. |
| **PPAC** | **ACQUIRED** (manual) | Refinery capacities, import shares, and supplier data curated from PPAC annual reports via research reports into seed datasets. |
| **ISPRL** | **ACQUIRED** (manual) | 3 SPR locations with capacities from ISPRL official website. Current fill levels not publicly disclosed. |
| **Data.gov.in** | DEFERRED | No specific datasets required for Phase 1 seed data beyond PPAC. |
| **World Bank** | DEFERRED | Historical commodity prices deferred; EIA is primary source. |

