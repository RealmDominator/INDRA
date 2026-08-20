# Backend Development Setup

> **Implemented in Step 3:** local FastAPI foundation, PostgreSQL connectivity check, and `GET /health` only.
>
> **Planned for later steps:** all business endpoints, schema deployment, migrations, ingestion, LLM integration, and engines.

## Windows PowerShell

Run all commands from the repository root.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r .\backend\requirements.txt
Copy-Item .env.example .env
docker compose up -d postgres
docker compose ps
python -m uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000
```

In another PowerShell window:

```powershell
Invoke-RestMethod http://localhost:8000/health
```

The endpoint returns `status: "ok"` even if PostgreSQL is unavailable; inspect the `database` field for `connected` or `unavailable`. It never exposes connection credentials.

Useful Docker commands:

```powershell
docker compose logs -f postgres
docker compose down
```

`db/schema.sql` and `db/seed.sql` are planned artifacts. Step 3 does not mount, execute, or seed them.
