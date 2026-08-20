# INDRA — India Disruption Response Architecture

> **From geopolitical event to procurement recommendation in minutes, not hours.**

---

## Problem

India imports approximately 88% of its crude oil requirements (~232 MMT in FY2024-25). Approximately 42% of these imports transit the Strait of Hormuz. India's Strategic Petroleum Reserves total ~5.33 MMT — roughly 9.5 days of coverage against an IEA-recommended 90 days. When geopolitical events disrupt supply corridors, India's oil companies (IOC, BPCL, HPCL) and government agencies (MoPNG, ISPRL) currently rely on fragmented, manual decision-making with 48–72 hour response lags. No integrated system connects geopolitical signals → shipping risk → refinery impact → reserve drawdown → procurement decisions.

## Target Users

- **IOC / BPCL / HPCL** crude procurement analysts and refinery supply-chain teams
- **MoPNG** policy and crisis-monitoring teams
- **ISPRL** strategic reserve planning teams
- **DGH** (Directorate General of Hydrocarbons)

This is a **B2B/GovTech decision-support** product, not a consumer application.

## MVP Capabilities

INDRA is a hackathon MVP that demonstrates one complete, explainable decision loop:

1. **Geopolitical Event Monitor** — Ingest events from GDELT, ACLED, RSS feeds; extract structured data via LLM
2. **India Risk Dashboard** — Explainable, weighted risk scores for Hormuz, Red Sea, Russia, and other corridors
3. **India Supply Network Map** — Interactive Leaflet map showing refineries, ports, SPR locations, routes, and chokepoints
4. **Scenario Simulator** — Deterministic disruption scenarios (Hormuz closure, Russia supply loss, Red Sea disruption, price spikes)
5. **Procurement Alternative Ranker** — Algorithmic/LP-based ranking of crude alternatives with refinery compatibility constraints
6. **SPR Decision Support Calculator** — Modelled drawdown requirements and bridge duration estimates
7. **Evidence Trail** — Every recommendation traceable from source article → extracted event → risk contribution → scenario assumptions → recommendation

## High-Level Architecture

```
External Data Sources (GDELT, ACLED, OFAC, EIA, RBI, PPAC, RSS)
        ↓
Python Ingestion Layer (APScheduler)
        ↓
Validation / Normalization (Pydantic, RapidFuzz)
        ↓
┌─────────────────────┬─────────────────┬──────────────────┐
│ LLM Event Extraction│  Risk Engine    │  Supply Graph    │
│                     │  (Rules-based)  │  (NetworkX)      │
└─────────┬───────────┴────────┬────────┴─────────┬────────┘
          └────────────────────┼──────────────────┘
                               ↓
                     PostgreSQL (single DB)
                               ↓
          ┌────────────────────┼────────────────────┐
          ↓                    ↓                    ↓
   Scenario Engine     Procurement Engine     SPR Engine
   (deterministic)     (ranking / LP)         (deterministic)
          └────────────────────┼────────────────────┘
                               ↓
                    Recommendation Builder
                               ↓
                    React Dashboard + Leaflet Map
```

## Current Development Status

**Step 0 — Foundation (CURRENT)**

The project is in the foundation phase. The repository structure, documentation contract, and development rules have been established. No application feature code has been implemented.

**What exists:**
- Complete documentation contract (architecture, API spec, database schema, AI/ML strategy, etc.)
- Research reports that define scope and constraints
- Development rules and conventions
- Planned directory structure

**What does NOT exist yet:**
- FastAPI routes / business logic
- React components / UI
- Trained ML models
- Live API integrations
- Database migrations
- Docker deployment services

## Repository Structure

```
INDRA/
├── README.md                          # This file
├── .gitignore                         # Git ignore rules
├── .env.example                       # Environment variable template
├── docker-compose.yml                 # Docker services (skeleton)
│
├── research/                          # Primary research sources (DO NOT MODIFY)
│   ├── research_report_1.md           # PETRAS — Brutally Honest Technical Analysis
│   └── research_report_2.md           # INDRA — Final Realistic Master Report
│
├── docs/                              # Project documentation
│   ├── DEVELOPMENT_RULES.md           # Mandatory rules for all development agents
│   ├── 01-product/                    # Product definition
│   │   ├── SOLUTION_OVERVIEW.md
│   │   └── MVP_SCOPE.md
│   ├── 02-architecture/               # System architecture
│   │   ├── SYSTEM_ARCHITECTURE.md
│   │   └── architecture/              # Architecture diagrams
│   ├── 03-frontend/                   # UI/UX specification
│   │   └── UI_UX.md
│   ├── 04-backend/                    # API specification
│   │   └── API_SPEC.md
│   ├── 05-database/                   # Database design
│   │   └── DATABASE_SCHEMA.md
│   ├── 06-data/                       # Data source strategy
│   │   └── DATA_SOURCES.md
│   ├── 07-ai-ml/                      # AI/ML documentation
│   │   ├── AI_PIPELINE.md
│   │   ├── ML_MODEL.md
│   │   └── AI_MODEL_STRATEGY.md
│   ├── 08-engines/                    # Computation engines
│   │   ├── SCENARIO_ENGINE.md
│   │   └── OPTIMIZATION.md
│   ├── 09-testing/                    # Testing strategy
│   │   └── TESTING.md
│   └── 10-demo/                       # Demo preparation
│       └── DEMO_SCRIPT.md
│
├── backend/                           # FastAPI backend (not yet implemented)
├── frontend/                          # React frontend (not yet implemented)
├── data/                              # Data directories
│   ├── raw/                           # Raw ingested data
│   ├── processed/                     # Cleaned/transformed data
│   ├── seed/                          # India-specific seed data
│   ├── historical/                    # Historical datasets
│   └── simulated/                     # Scenario simulation data
│
├── ml/                                # ML pipeline
│   ├── datasets/                      # Training/evaluation datasets
│   ├── training/                      # Training scripts
│   ├── evaluation/                    # Evaluation scripts and results
│   ├── models/                        # Saved model artifacts
│   └── artifacts/                     # SHAP plots, feature importance, etc.
│
├── prompts/                           # LLM prompt templates
├── db/                                # Database
│   ├── migrations/                    # Schema migrations
│   ├── schema.sql                     # Planned schema DDL
│   └── seed.sql                       # Seed data SQL
│
├── scripts/                           # Utility and setup scripts
└── deployment/                        # Deployment configuration
```

## Data Honesty Policy

INDRA enforces a strict data-transparency contract. Every data element displayed in the UI must be classified as one of:

| Classification | Meaning | UI Label |
|---|---|---|
| **LIVE** | Currently fetched from external source | `LIVE` |
| **RECENT / PERIODIC** | Updated on a schedule (daily/weekly) | `RECENT` |
| **HISTORICAL / SEEDED** | Static reference data from public sources | `HISTORICAL` |
| **DERIVED** | Calculated from other data (risk scores, gaps) | `DERIVED` |
| **SIMULATED** | Generated for scenario/demo purposes | `SIMULATED` |

**Rules:**
- Never represent simulated data as live data
- Never fabricate ML metrics or model results
- Never claim real-time AIS vessel tracking without verified paid access
- Never present scenario-derived estimates as measured values
- Always show data freshness timestamps
- Always provide evidence trails for recommendations

## Future Scope (OUT OF SCOPE for Phase 1)

The following are explicitly **out of scope** for the hackathon MVP. They may be mentioned in documentation as future roadmap items only:

- Real-time AIS vessel tracking (requires $5K+/month commercial subscription)
- Kafka / event streaming infrastructure
- Neo4j graph database
- LSTM / Transformer price forecasting
- Reinforcement learning
- Graph neural networks
- GPU-heavy custom transformer training
- Mobile application
- Kubernetes orchestration
- Blockchain
- Enterprise authentication / SSO / SAP integration
- Paid commercial data feeds (Bloomberg, Reuters, Spire)
- Multi-database architecture
- Microservices decomposition

## Development Rules

All development agents MUST read [docs/DEVELOPMENT_RULES.md](docs/DEVELOPMENT_RULES.md) before modifying any code.

Key rules:
1. Read relevant documentation before modifying code
2. Never introduce new technologies without explicit justification
3. Do not create fake real-world data
4. Never represent simulated data as live data
5. Keep the LLM's role bounded to event extraction and explanation
6. Numerical calculations must remain reproducible
7. Every important output must have an evidence/source path
8. Maintain the existing folder structure

## Links to Important Documents

| Document | Path |
|---|---|
| Solution Overview | [docs/01-product/SOLUTION_OVERVIEW.md](docs/01-product/SOLUTION_OVERVIEW.md) |
| MVP Scope | [docs/01-product/MVP_SCOPE.md](docs/01-product/MVP_SCOPE.md) |
| System Architecture | [docs/02-architecture/SYSTEM_ARCHITECTURE.md](docs/02-architecture/SYSTEM_ARCHITECTURE.md) |
| UI/UX Specification | [docs/03-frontend/UI_UX.md](docs/03-frontend/UI_UX.md) |
| API Specification | [docs/04-backend/API_SPEC.md](docs/04-backend/API_SPEC.md) |
| Database Schema | [docs/05-database/DATABASE_SCHEMA.md](docs/05-database/DATABASE_SCHEMA.md) |
| Data Sources | [docs/06-data/DATA_SOURCES.md](docs/06-data/DATA_SOURCES.md) |
| AI Pipeline | [docs/07-ai-ml/AI_PIPELINE.md](docs/07-ai-ml/AI_PIPELINE.md) |
| ML Model Strategy | [docs/07-ai-ml/ML_MODEL.md](docs/07-ai-ml/ML_MODEL.md) |
| AI Model Strategy | [docs/07-ai-ml/AI_MODEL_STRATEGY.md](docs/07-ai-ml/AI_MODEL_STRATEGY.md) |
| Scenario Engine | [docs/08-engines/SCENARIO_ENGINE.md](docs/08-engines/SCENARIO_ENGINE.md) |
| Procurement Optimization | [docs/08-engines/OPTIMIZATION.md](docs/08-engines/OPTIMIZATION.md) |
| Testing Strategy | [docs/09-testing/TESTING.md](docs/09-testing/TESTING.md) |
| Demo Script | [docs/10-demo/DEMO_SCRIPT.md](docs/10-demo/DEMO_SCRIPT.md) |
| Development Rules | [docs/DEVELOPMENT_RULES.md](docs/DEVELOPMENT_RULES.md) |
| Research Report 1 (PETRAS) | [research/research_report_1.md](research/research_report_1.md) |
| Research Report 2 (INDRA Master) | [research/research_report_2.md](research/research_report_2.md) |

---

**Hackathon:** PSB Cybersecurity, Fraud & AI Hackathon 2026
**Problem Statement:** AI-Driven Energy Supply Chain Resilience / Problem Statement 1
**Phase 1 Deadline:** 23 August 2026, 4:00 PM IST
