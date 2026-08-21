# Database Development Setup

## Implemented in Step 5

- PostgreSQL 16 runs through the existing Docker Compose service.
- `db/schema.sql` is the authoritative schema and applies cleanly.
- `db/seed.sql` is generated from the validated `data/seed/*.csv` files.
- The database scripts support initialization, reset/reseed, and integrity checks.
- SQLAlchemy connects through the environment-driven `DATABASE_URL`.
- Alembic structure is prepared for future migrations; no migration is defined in Step 5.

## Planned for later steps

Business tables may receive event, price, FX, evidence, and runtime records later. No business API, ingestion, LLM, entity-resolution, risk, scenario, or optimization feature is implemented here.

## Windows PowerShell commands

From the repository root:

```powershell
Copy-Item .env.example .env
.\.venv\Scripts\Activate.ps1
python -m pip install -r .\backend\requirements.txt

docker compose up -d postgres
docker compose ps

python .\scripts\data\validate_seed_data.py
python .\scripts\db\init_db.py
python .\scripts\db\check_db.py
```

Reset and rebuild the development database:

```powershell
python .\scripts\db\reset_db.py --confirm
python .\scripts\db\check_db.py
```

Inspect or stop PostgreSQL:

```powershell
docker compose logs -f postgres
docker compose down
```

The loader is reproducible from the curated CSVs:

```powershell
python .\scripts\data\load_seed_data.py --output .\db\seed.sql
```

The scripts read `DATABASE_URL` (or the `POSTGRES_*` variables) from the environment. Credentials are never embedded in Python source or committed `.env` files.

The existing FastAPI smoke check remains the only endpoint:

```powershell
Invoke-RestMethod http://localhost:8000/health
```

With PostgreSQL running, its `database` field is `connected`.
