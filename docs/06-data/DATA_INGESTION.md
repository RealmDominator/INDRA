# INDRA — Data Ingestion Architecture (Step 8B)

> **Status:** Step 8B — PARTIAL (fixture-verified; live-source access remains environment-dependent)  
> **Date:** 22 August 2026

---

## Overview

INDRA ingests approved external sources through a single adapter contract:

```
external source → fetch → parse → validate → normalize → deduplicate → persist → provenance → freshness
```

PostgreSQL remains the source of truth. Ingestion does **not** calculate risk scores, scenarios, or procurement results.

---

## Architecture

```
backend/app/ingestion/
├── base.py          # Adapter contracts, canonical records, freshness enums
├── normalizers.py   # Datetime/text helpers
├── dedup.py         # Source-aware deduplication
├── provenance.py    # evidence_records for ingested rows
├── persistence.py   # PostgreSQL writes + data_sources status updates
├── gdelt.py         # GDELT DOC API
├── acled.py         # ACLED (credential-gated)
├── eia.py           # EIA commodity prices (API key)
├── rbi.py           # RBI FX from processed official CSV
├── ofac.py          # OFAC SDN refresh → processed sanctions CSV
├── rss.py           # Approved RSS feeds
├── runner.py        # Orchestration + retry
└── scheduler.py     # APScheduler (optional, config-driven)
```

Manual one-shot run: `python scripts/data/run_ingestion.py`

API status: `GET /ingestion/status`

Persisted events feed: `GET /events`

---

## Source Adapter Contract

Each adapter exposes:

| Stage | Responsibility |
|---|---|
| `fetch()` | HTTP/file fetch with timeout |
| `parse()` | Raw payload → `SourceRecord` list |
| `normalize_*()` | Canonical INDRA records |
| `validate_*()` | Accept/reject with reasons |

Run results report: source name, timestamps, record counts, errors, freshness state, semantic class.

---

## Source Status (Verified 22 Aug 2026 — Step 11A activation attempt)

| Source | Connection Status | Notes |
|---|---|---|
| **GDELT** | PARTIAL (adapter + fixture tests; live runner blocked) | Bounded run returned `All connection attempts failed`; poll ~15 min when scheduler enabled |
| **RSS** | NOT_CONFIGURED (adapter + fixture tests) | Requires `RSS_FEED_URLS`; poll ~60 min |
| **OFAC** | PARTIAL (adapter + fixture tests; live runner blocked) | Bounded run returned `All connection attempts failed`; daily refresh to `data/raw/ofac` + `data/processed/ofac` |
| **RBI** | PARTIAL | Processed CSV loaded; 3 existing rows were duplicates; no reliable bulk automation API |
| **EIA** | REQUIRES_ACCESS | Adapter ready; needs `EIA_API_KEY` |
| **ACLED** | REQUIRES_ACCESS | Adapter ready; needs `ACLED_API_KEY` + `ACLED_EMAIL` |

This is **not real-time**. Polling intervals are configuration-driven with documented source latency.

---

## Credentials (environment only)

```bash
EIA_API_KEY=           # api.eia.gov (free registration)
ACLED_API_KEY=
ACLED_EMAIL=
INGESTION_ENABLED=false   # set true to start APScheduler
RSS_FEED_URLS=https://...,https://...
```

Never commit credentials. `.env` is gitignored.

---

## Normalization

### Events → `geopolitical_events`

- OBSERVED semantic class
- `event_type=OTHER` until LLM enrichment (Step 8A pipeline)
- No internal database IDs assigned at ingestion
- Stable source ID embedded in description as `[source_id:...]` when no URL exists

### Prices → `commodity_prices`

- Separate stream from FX (no synchronized INR column)
- OBSERVED semantic class

### FX → `fx_rates`

- OBSERVED from RBI processed CSV
- No fabricated current rates when file missing

### OFAC → processed sanctions CSV

- Energy-filtered entities only
- Raw SDN kept separate from normalized extract

---

## Deduplication

| Record type | Primary key | Fallback |
|---|---|---|
| Events | `source_name + source_url` | `source_name + source_record_id` marker | `source_name + title + occurred_at` |
| Prices | `source + grade_name + source_timestamp` | — |
| FX | `source + currency_pair + source_timestamp` | — |

No random UUID-only deduplication.

---

## Freshness Model

States: `FRESH`, `STALE`, `FAILED`, `NOT_CONFIGURED`, `DEFERRED`, `PARTIAL`, `REQUIRES_ACCESS`

Thresholds configured in `settings.py` (override via env):

- GDELT stale after 30 minutes
- RSS stale after 120 minutes
- EIA/RBI/OFAC stale after 48–72 hours

---

## Failure Handling

- Per-source timeout (`INGESTION_TIMEOUT_SECONDS`, default 30s)
- Bounded retries with backoff (`INGESTION_MAX_RETRIES`, default 2)
- Source failure does not crash the application
- Last successful data preserved
- Failures logged without secrets
- Status exposed via `/ingestion/status`

---

## Provenance

Each persisted row creates an `evidence_records` entry:

- `evidence_type=SOURCE`
- `input_summary` includes `source_record_id`, timestamps
- `data_semantic=OBSERVED` for external observations

---

## Polling Schedule (when `INGESTION_ENABLED=true`)

| Source | Default interval |
|---|---|
| GDELT | 15 minutes |
| RSS | 60 minutes |
| ACLED | 24 hours |
| EIA | 24 hours |
| RBI | 24 hours |
| OFAC | 24 hours |

---

## Testing

```powershell
$env:DATABASE_URL="postgresql+asyncpg://indra_user:<development_password>@localhost:5432/indra_db"
python -m pytest backend/tests/test_ingestion.py -q
```

Fixtures in `backend/tests/fixtures/ingestion/`. No live API dependency by default.

Optional live smoke: set credentials and run `python scripts/data/run_ingestion.py`.

---

## Deferred / Out of Scope

- Kafka, Redis, microservices
- NewsAPI (24h delay on free tier — not connected in Step 8B)
- Real-time AIS
- ML training
- Frontend redesign

---

## Pipeline Integration

Ingested events remain compatible with:

```
raw observation → (optional) LLM extraction → entity resolution → internal IDs
```

Ingestion does not bypass entity resolution or write incorrect foreign-key IDs.
