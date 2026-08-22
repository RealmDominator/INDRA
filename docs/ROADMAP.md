# INDRA Controlled Product Roadmap

**Status:** Step 12C COMPLETE — roadmap only; no future item below is implied to be implemented.

## Purpose and planning assumptions

This roadmap starts from the repository as it exists today. INDRA remains a
React/Vite frontend → FastAPI backend → PostgreSQL monolith. NetworkX is an
in-memory graph-operation layer, the LLM is bounded to structured extraction,
and risk, scenario, and procurement calculations remain deterministic in the
current Phase 1 baseline.

Priorities reflect user value for Indian energy-supply-chain decisions, India
relevance, buildability, data accessibility, maintenance burden, security risk,
and demo value. A roadmap item is not a commitment to build it, and no future
item changes the frozen architecture by implication.

## Current capability map

| Capability | Current repository support | Current limitation/status |
|---|---|---|
| Data foundation | PostgreSQL schema/seed data, manifest, semantic labels, provenance/evidence records, validation scripts | Reference and curated data dominate; external freshness remains partial. |
| Ingestion | GDELT, RSS, ACLED, EIA, RBI, and OFAC adapters; normalization, deduplication, persistence, freshness, retries, status API | Fixture-verified; credentialed/live completion is Step 8B/11A **PARTIAL**. |
| LLM extraction | Provider abstraction, OpenRouter adapter, structured `StructuredEvent`, bounded timeout/retries, validation, entity-resolution handoff | Runtime model is provisional; live benchmark is pending access. Explanation generation is not implemented. |
| Entity resolution | Exact alias lookup plus RapidFuzz fallback and unresolved logging/response state | Quality depends on maintained reference names and aliases. |
| Risk | Phase-1 weighted deterministic risk engine, internal 0–1 and display 0–100, component contributions | No independently evaluated ML risk model. |
| Network impact | NetworkX traversal for supplier → route → port → refinery reachability, affected refineries, and alternate routes | PostgreSQL remains source of truth; graph is rebuilt in memory. |
| Scenario engine | Deterministic, parametric supply-gap, refinery, inventory/SPR, and cost-impact calculations with semantic/provenance output | Outputs are modeled estimates, not forecasts or live measurements. |
| Procurement | SciPy `linprog(method="highs")` for fully identified candidates; deterministic ranking fallback | Unknown capacity/compatibility/cost inputs are excluded or retained as fallback limitations. |
| Evidence | Source → extraction → resolution → calculation → scenario → optimization chain and evidence drawer | Evidence quality is bounded by source availability and provenance completeness. |
| Frontend | React/Vite dashboard covering EVENT → RISK → SCENARIO → PROCUREMENT → EVIDENCE, semantic/stale/error states | Narrow hackathon MVP; no enterprise workflow or user administration. |
| Deployment | Containerized PostgreSQL, FastAPI, and Nginx-served frontend; reproducible init/seed scripts | Production-like local deployment, not an enterprise production platform. |
| Monitoring | `/health`, `/ingestion/status`, component/source states, safe logs, runtime check script, DB integrity checks | Lightweight operational visibility; no distributed monitoring platform or SLA. |

## Status vocabulary

- **IMPLEMENTED:** verified in the repository and test evidence.
- **PARTIAL:** software path exists, but access, coverage, or verification is incomplete.
- **DEFERRED:** intentionally postponed pending data, access, or prioritization.
- **FUTURE:** a possible later capability, not designed as an implementation commitment.

## NOW — protect reliability and increase decision value

These are the highest-value follow-ups after the current MVP. They should stay
inside the existing monolith and use existing tables, adapters, contracts, and
tests.

| Feature | Value | Technical difficulty | Data dependency | Expected benefit | Risk | Priority |
|---|---|---:|---|---|---|---|
| External-source completion for the most useful accessible feeds | More current India-relevant event, sanctions, price, and FX coverage | Medium | Credentials, stable endpoints, source terms, freshness validation | Converts fixture/partial ingestion into dependable operational input | Source outages, licensing, secrets, misleading freshness | NOW |
| Source freshness and provenance hardening | Lets operators distinguish current, stale, failed, assumed, and simulated inputs | Low–Medium | Source timestamps and adapter metadata | Higher trust and faster incident diagnosis | Incorrect timestamps can create false confidence | NOW |
| Entity-resolution review queue and alias maintenance workflow | Reduces unresolved India, corridor, supplier, and port names | Medium | Curated aliases and human review | Better event-to-network coverage without embeddings | False merges can corrupt risk paths | NOW |
| LLM benchmark activation and prompt regression cycle | Establishes evidence before changing the provisional model | Low–Medium | `OPENROUTER_API_KEY`, fixed 25-example benchmark, evaluation annotations | Safe model/provider decision with measured latency and failure rates | Benchmark set is synthetic/limited; access cost | NOW |
| Evidence and audit-report export | Makes a recommendation reviewable by procurement and policy teams | Low–Medium | Complete evidence links and stable result identifiers | Stronger demo and operational handoff | Export may expose sensitive source text if not redacted | NOW |
| Preserve deterministic regression and operational checks in CI | Prevents changes to risk, scenario, procurement, and ingestion contracts | Low | Fixtures, seeded DB, mocked providers | Lower maintenance and release risk | Slow DB-backed CI if poorly isolated | NOW |

## NEXT — deepen India-specific planning workflows

These items should follow evidence that the NOW controls are useful and that
required data can be maintained.

| Feature | Value | Technical difficulty | Data dependency | Expected benefit | Risk | Priority |
|---|---|---:|---|---|---|---|
| Historical corridor-risk calibration | Makes deterministic weights and baseline exposure more defensible for Indian routes | High | Versioned event, route, import, and disruption outcome history | Better calibrated decision support without immediately introducing ML | Circular labels, missing coverage, false precision | NEXT |
| Scenario library with saved assumptions and comparison | Speeds recurring Hormuz, Red Sea, Russia-loss, price, and SPR analyses | Medium | Versioned assumptions and scenario provenance | Faster policy/procurement what-if analysis | Users may mistake assumptions for observed facts | NEXT |
| Policy and procurement review workflow | Records approval, notes, selected alternatives, and evidence snapshot | Medium | Identity/audit requirements and authorization design | Makes recommendations usable beyond a demo | Security and access-control burden | NEXT |
| Alert subscriptions with bounded polling | Surfaces material source changes, stale feeds, or high-risk corridors | Medium–High | Reliable source freshness and alert thresholds | Earlier operator awareness | Alert fatigue, duplicate notifications, external delivery secrets | NEXT |
| Refinery compatibility and supplier-capacity data improvement | Improves LP eligibility and reduces ranking fallback | High | Verified refinery intake, supplier availability, route capacity | More useful procurement allocations | Commercial/confidential data and uncertain engineering limits | NEXT |
| Cross-source event corroboration | Separates single-source reports from corroborated observations | Medium | Multiple accessible sources and deduplication rules | More transparent confidence and lower false-positive risk | Correlated sources may appear independent | NEXT |

## LATER — only after data and operating demand justify it

| Feature | Value | Technical difficulty | Data dependency | Expected benefit | Risk | Priority |
|---|---|---:|---|---|---|---|
| Conditional XGBoost candidate evaluation | Tests whether supervised disruption probability adds value over the deterministic baseline | High | Independent time-indexed target, pre-cutoff features, temporal train/validation/test data | Evidence-based ML decision if data supports it | Leakage, weak labels, overfitting, unjustified promotion | LATER / CONDITIONAL |
| Explainability for an approved ML candidate | Helps users inspect model drivers | Medium after ML exists | Valid trained model and stable feature semantics | Better reviewability | Correlation may be misread as causation; SHAP does not validate labels | LATER / CONDITIONAL |
| Multi-horizon risk and scenario comparison | Supports 7/14/30-day planning decisions | Medium–High | Historical outcomes and horizon-specific assumptions | More useful contingency planning | Conflicting horizons and false forecast interpretation | LATER |
| Automated periodic calibration reports | Shows drift in source coverage, resolution, risk components, and optimizer feasibility | Medium | Versioned runtime telemetry and benchmark history | Long-term maintenance visibility | Privacy/storage burden and misleading aggregate metrics | LATER |
| Additional accessible official price/import datasets | Improves price/FX and supply-gap context | Medium | Official accessible source, legal use, timestamp alignment | Better cost and gap context for India | Maintenance burden and inconsistent publication formats | LATER |

## Conditional ML gate

XGBoost must not proceed because it is fashionable or because a seed dataset is
available. The gate is:

```text
independent historical target
→ target timestamp and fixed horizon
→ sufficient covered positive and negative windows
→ feature cutoff/leakage audit
→ temporal split
→ restrained candidate and reproducible artifacts
→ comparison with Phase-1 deterministic baseline on identical labels
→ explicit decision: better / not better / insufficient data
```

The current decision is **INSUFFICIENT DATA FOR VALID EVALUATION**. Until the
gate passes, no XGBoost dependency, model, score, SHAP output, or production
integration should be added.

## Data-source prioritization

Prioritize sources using reliability, accessibility, India relevance, freshness,
and maintenance cost:

1. **Existing official/accessible paths:** RBI reference-rate fallback, OFAC
   official sanctions snapshot when reachable, and validated existing feeds.
2. **Credentialed sources with clear India value:** EIA for prices and ACLED
   for conflict events, after access, terms, timestamp, and bounded-failure
   verification are in place.
3. **Corroborating public event sources:** GDELT/RSS only with explicit source
   quality, deduplication, and freshness labels.
4. **Historical panels:** acquire only when licensing, schema, target coverage,
   timestamps, and checksum/version requirements are documented.

Paid feeds, including commercial AIS, require a documented business case,
measured decision value, security review, and maintenance owner. No paid feed is
required for the current MVP roadmap.

## DO NOT BUILD without an explicit architecture reconsideration

These are not roadmap commitments and remain outside the frozen design:

- Kafka or other event-streaming infrastructure for MVP-scale workloads;
- Neo4j, MongoDB, or a second persistent database;
- blockchain;
- Kubernetes, service meshes, or microservices;
- GPU-heavy custom models, LSTM, GNN, reinforcement learning, or vector
  databases without an approved evidence-based need;
- unnecessary real-time AIS or claims of live vessel tracking without a
  justified, verified source;
- enterprise authentication, multi-tenancy, or a large administrative product
  before a real deployment owner and security requirements exist.

## Roadmap governance

Every roadmap promotion from NEXT/LATER to implementation must have a short
decision record covering user value, data owner, security/privacy impact,
maintenance owner, expected test evidence, semantic/provenance behavior, and
rollback. Product work must preserve the existing contracts unless an explicit
architecture decision reopens them.

