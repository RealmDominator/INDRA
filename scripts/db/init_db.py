#!/usr/bin/env python3
"""
INDRA -- Database Initialization Script
Applies db/schema.sql then db/seed.sql to the development PostgreSQL database.

Usage:
    python scripts/db/init_db.py [--schema-only] [--seed-only]

Environment:
    DATABASE_URL  (or POSTGRES_USER/POSTGRES_PASSWORD/POSTGRES_DB/POSTGRES_HOST)
    Reads from .env if present.

Exit codes:
    0 = success
    1 = failure
"""
import argparse
import os
import sys
from pathlib import Path

# ---- project root ----------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

SCHEMA_FILE = PROJECT_ROOT / "db" / "schema.sql"
SEED_FILE   = PROJECT_ROOT / "db" / "seed.sql"


def _load_env():
    """Load .env file if present (minimal, no third-party deps needed)."""
    env_file = PROJECT_ROOT / ".env"
    if env_file.exists():
        with open(env_file, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, val = line.partition("=")
                    key = key.strip()
                    val = val.strip().strip('"').strip("'")
                    if key not in os.environ:
                        os.environ[key] = val


def _get_dsn() -> str:
    """
    Build a psycopg2-compatible DSN from environment.
    Prefers DATABASE_URL (strips +asyncpg driver prefix).
    Falls back to individual POSTGRES_* vars.
    """
    db_url = os.environ.get("DATABASE_URL", "")
    if db_url:
        # Strip SQLAlchemy driver prefix: postgresql+asyncpg:// → postgresql://
        if "+asyncpg" in db_url:
            db_url = db_url.replace("+asyncpg", "", 1)
        if "+psycopg2" in db_url:
            db_url = db_url.replace("+psycopg2", "", 1)
        return db_url

    # Fallback: compose from individual vars
    user     = os.environ.get("POSTGRES_USER", "")
    password = os.environ.get("POSTGRES_PASSWORD", "")
    db       = os.environ.get("POSTGRES_DB", "")
    host     = os.environ.get("POSTGRES_HOST",     "localhost")
    port     = os.environ.get("POSTGRES_PORT",     "5432")
    if not all((user, password, db)):
        raise RuntimeError("DATABASE_URL or POSTGRES_USER/POSTGRES_PASSWORD/POSTGRES_DB must be configured")
    return f"postgresql://{user}:{password}@{host}:{port}/{db}"


def _execute_sql_file(conn, filepath: Path, label: str):
    """Execute a SQL file against the given connection."""
    print("[%s] Reading %s ..." % (label, filepath.relative_to(PROJECT_ROOT)))
    sql = filepath.read_text(encoding="utf-8")

    with conn.cursor() as cur:
        cur.execute(sql)
    conn.commit()
    print("[%s] Done." % label)


def main():
    parser = argparse.ArgumentParser(description="INDRA Database Initialization")
    parser.add_argument("--schema-only", action="store_true",
                        help="Apply schema only (skip seed data)")
    parser.add_argument("--seed-only", action="store_true",
                        help="Apply seed only (schema must already exist)")
    args = parser.parse_args()

    _load_env()

    try:
        import psycopg2
    except ImportError:
        print("[ERROR] psycopg2 not installed. Run: pip install psycopg2-binary")
        sys.exit(1)

    dsn = _get_dsn()
    # Mask password for logging
    display_dsn = dsn
    pg_pass = os.environ.get("POSTGRES_PASSWORD", "")
    if pg_pass and pg_pass in display_dsn:
        display_dsn = display_dsn.replace(pg_pass, "***")
    print("Connecting to: %s" % display_dsn)

    try:
        conn = psycopg2.connect(dsn)
        conn.autocommit = False
    except Exception as e:
        print("[ERROR] Cannot connect to PostgreSQL: %s" % e)
        print("  Make sure the container is running: docker compose up -d")
        sys.exit(1)

    try:
        if not args.seed_only:
            if not SCHEMA_FILE.exists():
                print("[ERROR] Schema file not found: %s" % SCHEMA_FILE)
                sys.exit(1)
            _execute_sql_file(conn, SCHEMA_FILE, "SCHEMA")

        if not args.schema_only:
            if not SEED_FILE.exists():
                print("[ERROR] Seed file not found: %s" % SEED_FILE)
                sys.exit(1)
            _execute_sql_file(conn, SEED_FILE, "SEED")

        print("\n[OK] Database initialization complete.")
    except Exception as e:
        conn.rollback()
        print("\n[ERROR] Database initialization failed: %s" % e)
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
