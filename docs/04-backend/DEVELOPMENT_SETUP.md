# Backend Development Setup

> **Implemented in Step 3:** local FastAPI foundation, PostgreSQL connectivity check, and `GET /health` only.
>
> **Planned for later steps:** all business endpoints, schema deployment, migrations, ingestion, LLM integration, and engines.

## Windows PowerShell

Run all commands from the repository root. Step 6A requires an actual `.env` with database values; the template contains placeholders only.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r .\backend\requirements.txt
Copy-Item .env.example .env
notepad .env  # set POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB, and DATABASE_URL
docker compose up -d postgres
docker compose ps
python -m uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000
```

In another PowerShell window:

```powershell
Invoke-RestMethod http://localhost:8000/health
Invoke-RestMethod http://localhost:8000/countries
Invoke-RestMethod http://localhost:8000/corridors
Invoke-RestMethod http://localhost:8000/crude-grades
Invoke-RestMethod http://localhost:8000/routes
Invoke-RestMethod http://localhost:8000/refineries
Invoke-RestMethod http://localhost:8000/suppliers
Invoke-RestMethod http://localhost:8000/reserves
```

The endpoint returns `status: "ok"` even if PostgreSQL is unavailable; inspect the `database` field for `connected` or `unavailable`. It never exposes connection credentials.

Useful Docker commands:

```powershell
docker compose logs -f postgres
docker compose down
```

`db/schema.sql` and `db/seed.sql` are planned artifacts. Step 3 does not mount, execute, or seed them.

Step 6A adds read-only reference-data endpoints, SQLAlchemy domain mappings, repository/service boundaries, and exact-alias/RapidFuzz entity resolution. Event intelligence, risk, scenarios, procurement, evidence, and prices are not implemented.
