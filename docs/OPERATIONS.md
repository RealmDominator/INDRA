# INDRA Operations Guide

This guide covers lightweight monitoring and maintenance for the React/Vite →
FastAPI → PostgreSQL MVP. It does not introduce a second monitoring database or
claim enterprise production readiness.

## Health checks

```powershell
Invoke-WebRequest http://127.0.0.1:8000/health
python scripts/ops/check_runtime.py
python scripts/db/check_db.py
```

`GET /health` returns the application and database state plus safe component
states: `HEALTHY`, `DEGRADED`, `UNAVAILABLE`, or `NOT_CONFIGURED`. It includes
an aggregate source summary, but never returns credentials, tokens, prompts, or
authorization headers. A database outage is reported with HTTP 200 and an
`UNAVAILABLE` component so container health diagnostics remain safe.

## Ingestion and freshness

`GET /ingestion/status` reports each configured source’s status, last fetched
timestamp, freshness, last run status, accepted record count, and bounded error
message. The freshness vocabulary is `FRESH`, `STALE`, `FAILED`,
`NOT_CONFIGURED`, `DEFERRED`, `PARTIAL`, or `REQUIRES_ACCESS`.

```powershell
Invoke-WebRequest http://127.0.0.1:8000/ingestion/status
python scripts/data/run_ingestion.py
```

`STALE`, `FAILED`, and `PARTIAL` require investigation; `NOT_CONFIGURED` and
`REQUIRES_ACCESS` mean that credentials or feed configuration is absent. The
current external-source limitation remains Step 8B/11A PARTIAL. Do not label
fixture, historical, RBI fallback, or simulated data as live.

## Logs and failure diagnosis

The backend logs startup, request completion/failure, database health failures,
provider retries/failures, ingestion failures, and pipeline failures. Logs use
provider/model metadata and counts where possible. API keys, passwords, tokens,
authorization headers, and unnecessary raw prompts are not logged.

Typical checks:

```powershell
docker compose -f docker-compose.production.yml ps
docker compose -f docker-compose.production.yml logs --tail=100 backend
docker compose -f docker-compose.production.yml logs --tail=100 postgres
```

Use the returned stage or source name to isolate a failure. Client responses
are deliberately generic for unexpected 500 errors; validation failures return
422 and unavailable provider extraction returns a safe 503.

## Recovery

1. Check `/health` and `/ingestion/status`.
2. If the database is unavailable, inspect PostgreSQL health/logs and verify
   `DATABASE_URL`/Compose credentials without printing them.
3. If a source is `NOT_CONFIGURED` or `REQUIRES_ACCESS`, configure its existing
   environment variables; do not substitute fabricated observations.
4. If a source is `FAILED` or `STALE`, inspect bounded adapter errors and retry
   the relevant ingestion run after the source is reachable.
5. If schema integrity is suspect, run `python scripts/db/check_db.py`.
6. Restart only the affected local container after correcting configuration.

## Database maintenance

```powershell
python scripts/db/check_db.py
python scripts/db/init_db.py
```

`reset_db.py --confirm` is development-only and destroys local database state;
do not use it as a production recovery procedure. PostgreSQL remains the
persistent source of truth and seed loading is separate from runtime health.

## Provider maintenance

The LLM provider is bounded by configured timeout and retry limits. Missing
`OPENROUTER_API_KEY` is `NOT_CONFIGURED`; it is not treated as a successful
provider. The live benchmark remains pending and XGBoost remains an unstarted
Phase-2 candidate.

## Deployment sanity

```powershell
docker compose -f docker-compose.production.yml config --quiet
docker compose -f docker-compose.production.yml up -d
python scripts/ops/check_runtime.py
npm --prefix frontend run build
```

Stop the local deployment with:

```powershell
docker compose -f docker-compose.production.yml down
```
