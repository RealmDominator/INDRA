# INDRA Deployment Guide

INDRA keeps the frozen Phase-1 topology:

```text
React/Vite frontend → FastAPI backend → PostgreSQL
```

NetworkX remains in-process for graph traversal. LLM calls are optional and
environment-configured; risk, scenario, and procurement calculations remain
deterministic. External ingestion credentials are optional and Step 8B remains
partial.

## Prerequisites

- Docker Desktop with Compose
- Python 3.11+ for host-side scripts/tests
- Node.js 20+ and npm for host-side frontend development

## Environment

Copy `.env.example` to `.env` and set a non-default PostgreSQL password:

```powershell
Copy-Item .env.example .env
```

Required local database variables are `POSTGRES_USER`, `POSTGRES_PASSWORD`,
`POSTGRES_DB`, and `DATABASE_URL`. `CORS_ORIGINS` controls backend browser
origins. Keep `APP_DEBUG=false` for production-like runs. LLM and external
source keys may remain empty; unavailable providers are reported explicitly.

Never commit `.env` or place secrets in frontend variables. Only variables
prefixed `VITE_` are compiled into frontend assets.

## Development deployment

Start PostgreSQL only:

```powershell
docker compose up -d postgres
python scripts/db/init_db.py
python -m uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000
```

In another shell:

```powershell
cd frontend
npm ci
npm run dev
```

Verify `http://localhost:8000/health` and open `http://localhost:3000`.
Use `python scripts/db/reset_db.py --confirm` only for development data
resets. It refuses non-development environments.

## Production-like local deployment

The separate `docker-compose.production.yml` starts PostgreSQL, the backend,
and an Nginx-served production frontend. It does not run the Vite development
server. PostgreSQL is bound to loopback only for local integrity checks and is
not exposed on external interfaces:

```powershell
docker compose -f docker-compose.production.yml up -d --build
docker compose -f docker-compose.production.yml run --rm backend python scripts/db/init_db.py
docker compose -f docker-compose.production.yml ps
```

The backend is available on `http://localhost:8000`; the frontend is on
`http://localhost`. Database initialization is intentionally a separate,
explicit operation. Production migrations are not generated automatically:
`db/schema.sql` remains authoritative and seed loading is separate.

## Migrations and database lifecycle

Alembic is a foundation only. There are no generated migrations because the
frozen PostgreSQL schema is currently authoritative. Apply a reviewed schema
change with the existing database scripts, and add an intentional Alembic
migration only when the project approves migration ownership.

```powershell
python scripts/db/check_db.py
```

Do not run `reset_db.py` against production data.

## Health, logs, and shutdown

- Backend: `GET /health` reports application and PostgreSQL connectivity.
- Backend container: healthcheck calls `/health` without exposing secrets.
- Frontend container: Nginx healthcheck verifies HTTP availability.
- Logs: `docker compose -f docker-compose.production.yml logs -f backend`.

Shutdown without deleting the database volume:

```powershell
docker compose -f docker-compose.production.yml down
```

## Troubleshooting

- Database unavailable: check `docker compose ... ps`, `.env` credentials, and
  run `scripts/db/init_db.py` after PostgreSQL is healthy.
- CORS errors: set `CORS_ORIGINS` to the exact browser origin, such as
  `http://localhost` or `http://localhost:3000`.
- LLM extraction unavailable: expected when `OPENROUTER_API_KEY` is empty;
  use the deterministic fallback/demo path.
- EIA/ACLED unavailable: expected while Step 8B credentials are unset.
- Frontend API mismatch: set `VITE_API_BASE` at frontend image build time or
  use the development default `http://localhost:8000`.

## Reproducibility verification

```powershell
python -m pytest backend/tests -q
python backend/tests/test_e2e_pipeline.py
python scripts/db/check_db.py
cd frontend; npm run build
docker compose -f docker-compose.production.yml config
```

These checks require no external API credentials.

## Security audit notes

The production-like profile forces `APP_DEBUG=false`, uses environment-driven
database and provider configuration, binds PostgreSQL to `127.0.0.1`, runs the
backend as a non-root user, and does not copy `.env` into images. `CORS_ORIGINS`
must be set to explicit browser origins; credentials are not stored in the
frontend bundle. The Vite development server is loopback-bound; production
serves the compiled frontend through Nginx. See `docs/09-testing/TESTING.md`
for the verified Step 9A security checks and the documented Vite advisory
follow-up.
