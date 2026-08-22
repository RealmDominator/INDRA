#!/usr/bin/env python3
"""
INDRA -- Database Reset Script
Drops all application tables and re-applies schema + seed from scratch.

DEVELOPMENT ONLY. Will refuse to run if APP_ENV != 'development'.

Usage:
    python scripts/db/reset_db.py [--confirm]

Environment:
    DATABASE_URL  (or POSTGRES_USER/POSTGRES_PASSWORD/POSTGRES_DB/POSTGRES_HOST)
    APP_ENV  must be 'development' or must pass --confirm

Exit codes:
    0 = success
    1 = failure or refused
"""
import argparse
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "db"))

# Import helpers from init_db
from init_db import _load_env, _get_dsn, _execute_sql_file, redact_dsn

SCHEMA_FILE = PROJECT_ROOT / "db" / "schema.sql"
SEED_FILE   = PROJECT_ROOT / "db" / "seed.sql"

# Tables to drop, in reverse FK order
DROP_ORDER = [
    "evidence_links",
    "evidence_records",
    "procurement_options",
    "scenario_results",
    "scenarios",
    "risk_scores",
    "geopolitical_events",
    "refinery_supply_mix",
    "routes",
    "refineries",
    "suppliers",
    "ports",
    "crude_grades",
    "corridors",
    "strategic_reserves",
    "fx_rates",
    "commodity_prices",
    "data_sources",
    "entity_aliases",
    "countries",
]


def main():
    parser = argparse.ArgumentParser(description="INDRA Database Reset (DEV ONLY)")
    parser.add_argument("--confirm", action="store_true",
                        help="Skip interactive confirmation prompt")
    args = parser.parse_args()

    _load_env()

    app_env = os.environ.get("APP_ENV", "development")
    if app_env != "development":
        print("[REFUSED] reset_db.py only runs in APP_ENV=development (current: %s)" % app_env)
        sys.exit(1)

    if not args.confirm:
        ans = input("This will DROP all INDRA tables and reseed. Type 'yes' to continue: ")
        if ans.strip().lower() != "yes":
            print("Aborted.")
            sys.exit(0)

    try:
        import psycopg2
    except ImportError:
        print("[ERROR] psycopg2 not installed. Run: pip install psycopg2-binary")
        sys.exit(1)

    dsn = _get_dsn()
    print("Connecting to: %s" % redact_dsn(dsn))

    try:
        conn = psycopg2.connect(dsn)
        conn.autocommit = False
    except Exception as e:
        print("[ERROR] Cannot connect: %s" % e)
        sys.exit(1)

    try:
        print("\n[RESET] Dropping all application tables...")
        with conn.cursor() as cur:
            for table in DROP_ORDER:
                cur.execute("DROP TABLE IF EXISTS %s CASCADE;" % table)
                print("  Dropped: %s" % table)
        conn.commit()
        print("[RESET] All tables dropped.")

        print("\n[SCHEMA] Applying schema...")
        _execute_sql_file(conn, SCHEMA_FILE, "SCHEMA")

        print("\n[SEED] Loading seed data...")
        _execute_sql_file(conn, SEED_FILE, "SEED")

        print("\n[OK] Database reset and reseeded successfully.")
    except Exception as e:
        conn.rollback()
        print("\n[ERROR] Reset failed: %s" % e)
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
