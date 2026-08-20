# INDRA — Development Rules

> **Every development agent MUST read this file before modifying any project code.**
>
> These rules are derived from the research reports and the project's data-honesty contract. Violations compromise the project's credibility.

---

## Rule 1: Read Before Modifying

Read the relevant documentation before modifying code. The `docs/` directory contains architectural decisions, API specifications, database schemas, and scope constraints that must be respected. Implementing features without reading the relevant doc will lead to inconsistencies.

**Key documents:**
- `docs/01-product/MVP_SCOPE.md` — What to build and what NOT to build
- `docs/02-architecture/SYSTEM_ARCHITECTURE.md` — Component responsibilities and data flow
- `docs/07-ai-ml/AI_MODEL_STRATEGY.md` — LLM abstraction requirements
- `docs/07-ai-ml/AI_PIPELINE.md` — Boundaries of what the LLM should and should not do

## Rule 2: Never Modify Unrelated Files

When implementing a feature, modify only the files directly related to that feature. Do not refactor unrelated code, rename unrelated files, or "clean up" code outside your task scope.

## Rule 3: No New Technologies Without Justification

Do not introduce new technologies, frameworks, libraries, or databases without explicit justification documented in a decision record. The technology stack is defined in `docs/02-architecture/SYSTEM_ARCHITECTURE.md`.

**Explicitly prohibited additions (Phase 1):**
- Kafka, Neo4j, MongoDB, ClickHouse, Elasticsearch
- Kubernetes, Docker Swarm
- dbt, Airflow, Prefect
- Blockchain / distributed ledger
- LSTM, GNN, reinforcement learning frameworks
- Any paid commercial data feed SDK

## Rule 4: No Fake Real-World Data

Do not create synthetic data and present it as real-world data. If seed data is needed:
- Use publicly available data from PPAC, ISPRL, EIA, ACLED, GDELT, OFAC, RBI
- If values must be estimated (e.g., refinery throughput percentages), clearly mark them as estimates with source references
- Never invent crude oil prices, exchange rates, vessel positions, or import volumes

## Rule 5: Never Represent Simulated Data as Live Data

Every data element displayed in the UI must carry its data-semantic tag:
- `OBSERVED` — directly fetched from an external source (EIA price, GDELT event, OFAC sanctions)
- `DERIVED` — calculated from observed values using a documented formula (risk score, supply gap)
- `HISTORICAL_CALIBRATED` — parameter derived from analysis of historical events (PPAC import share, price impact multiplier)
- `ASSUMED` — configuration or user assumption not derived from data (freight multiplier, risk weight)
- `SIMULATED` — synthetic state generated for scenario/demo purposes

Never display a `SIMULATED` value without the tag. Never claim "real-time" for data that is HISTORICAL_CALIBRATED or ASSUMED.

## Rule 6: Never Fabricate ML Metrics

Do not claim model accuracy, precision, recall, F1, or any evaluation metric without:
1. A defined evaluation dataset
2. A documented evaluation methodology
3. Actual model output on that dataset
4. Reproducible evaluation code

Saying "87% accuracy" without a confusion matrix and dataset description will be caught by judges.

## Rule 7: Never Claim Real-Time Without Verification

Do not claim an API or data feed is "real-time" unless you have verified:
1. The API is currently accessible
2. The data actually updates at the claimed frequency
3. The free tier supports the claimed update frequency

**Known non-real-time sources:**
- PPAC — monthly PDFs/CSVs, no real-time API
- NewsAPI free tier — 24-hour delay
- ACLED — weekly updates
- AIS — real-time requires $5K+/month subscription

## Rule 8: Keep the LLM's Role Bounded

The LLM is used for exactly two purposes in INDRA:

1. **Event extraction:** Converting unstructured news text into structured JSON (event_type, severity, affected_entities, affected_corridors, confidence)
2. **Explanation generation:** Converting structured calculation results into readable natural-language summaries

The LLM must **NOT**:
- Compute risk scores (use deterministic weighted formula)
- Make procurement decisions (use LP optimization / ranking algorithm)
- Calculate supply gaps (use parametric arithmetic)
- Simulate scenarios (use deterministic propagation engine)
- Invent prices, transit times, stock levels, or optimization results
- Generate data that should come from external sources
- Replace any deterministic computation with a generative response

## Rule 9: Numerical Calculations Must Be Reproducible

Risk scores, scenario results, supply gaps, procurement rankings, and SPR drawdown estimates must be computed by deterministic formulas or optimization algorithms. Given the same inputs, the same outputs must result every time.

Do not use:
- LLM-generated numbers for any quantitative output
- Random number generators without fixed seeds for any user-facing output
- Temperature > 0 for any LLM call that produces structured data

## Rule 10: Evidence/Source Paths Are Mandatory

Every important output displayed to the user must have an evidence trail where applicable:

```
Source article / data feed
    ↓
Extracted event (with confidence)
    ↓
Risk contribution (with weight)
    ↓
Scenario assumptions (clearly labeled)
    ↓
Calculated impact (with formula reference)
    ↓
Recommendation (with ranking criteria)
```

A risk score of 0.78 with no explanation is meaningless. An evidence chain that drills to source articles, timestamps, and component weights is genuinely impressive.

## Rule 11: Update Documentation When Architecture Changes

If you change an architectural decision (e.g., switch from weighted scoring to ML-based scoring, add a new data source, modify the API surface), update the corresponding documentation file AND note the change in the commit message.

Do not let documentation and code diverge.

## Rule 12: Run Tests After Implementation Changes

After implementing or modifying a feature:
1. Run the relevant unit tests
2. Run the API integration tests if backend code changed
3. Verify the frontend renders correctly if UI code changed
4. Run the end-to-end pipeline test if the core chain was modified

See `docs/09-testing/TESTING.md` for the testing strategy.

## Rule 13: Maintain the Existing Folder Structure

The repository structure is defined in `README.md`. Do not:
- Create new top-level directories without justification
- Move files between directories without updating documentation
- Rename directories
- Create files in locations that don't match the established structure

## Rule 14: Simple Working Components Over Unnecessary Infrastructure

Prefer:
- APScheduler over Kafka
- NetworkX over Neo4j
- PostgreSQL JSONB over MongoDB
- Python scripts over Airflow
- Docker Compose over Kubernetes
- Monolith over microservices

The goal is a working, demonstrable decision loop — not an impressive architecture diagram.

## Rule 15: Do Not Solve Production Problems During the Hackathon

Do not spend time on:
- Multi-tenant architecture
- Horizontal scaling
- Production monitoring / alerting
- SOC 2 compliance
- Enterprise SSO / SAML
- CI/CD pipeline optimization
- Load testing for thousands of users
- Database sharding or replication

These are explicitly Phase 2/3 concerns. Solving them now wastes hackathon time.

---

## Quick Reference

```
✅ DO:
   - Use real data sources (GDELT, ACLED, EIA, OFAC, RBI, PPAC)
   - Label every data point with its data-semantic tag:
     OBSERVED / DERIVED / HISTORICAL_CALIBRATED / ASSUMED / SIMULATED
   - Show evidence trails for recommendations
   - Use deterministic formulas for quantitative outputs
   - Use the LLM for extraction and explanation only
   - Keep the stack small and working

❌ DO NOT:
   - Claim real-time data without verification
   - Fabricate ML metrics
   - Use the LLM for numerical calculations
   - Add technologies not in the approved stack
   - Create fake vessel positions or import volumes
   - Build Phase 2/3 features during the hackathon
```
