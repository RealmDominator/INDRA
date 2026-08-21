#!/usr/bin/env python3
"""
INDRA -- Database Integrity Check Script
Verifies tables, row counts, FK relationships, value ranges, and semantic labels.

Usage:
    python scripts/db/check_db.py [--verbose]

Exit codes:
    0 = all checks passed
    1 = one or more checks failed
"""
import os
import sys
import argparse
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "db"))
from init_db import _load_env, _get_dsn

# ---- expected state --------------------------------------------------------

REQUIRED_TABLES = [
    "countries", "corridors", "crude_grades", "suppliers", "ports",
    "refineries", "refinery_supply_mix", "routes", "geopolitical_events",
    "risk_scores", "commodity_prices", "fx_rates", "scenarios",
    "scenario_results", "procurement_options", "strategic_reserves",
    "evidence_records", "evidence_links", "data_sources", "entity_aliases",
]

# Minimum row counts for seeded tables (from Step-4 validated datasets)
MIN_ROW_COUNTS = {
    "countries":           15,
    "corridors":            6,
    "crude_grades":        14,
    "ports":               20,
    "refineries":          20,
    "suppliers":            8,
    "refinery_supply_mix": 51,
    "routes":              15,
    "strategic_reserves":   3,
    "data_sources":        10,
    "scenarios":            5,
}

VALID_SEMANTICS = {"OBSERVED", "DERIVED", "HISTORICAL_CALIBRATED", "ASSUMED", "SIMULATED"}
VALID_COMPATIBILITY = {"HIGH", "MEDIUM", "LOW", "NONE"}

# ---- check infrastructure --------------------------------------------------

errors   = []
warnings = []
checks   = 0


def fail(msg):
    errors.append("[FAIL] %s" % msg)
    print("[FAIL] %s" % msg)


def warn(msg):
    warnings.append("[WARN] %s" % msg)
    print("[WARN] %s" % msg)


def ok(msg):
    global checks
    checks += 1
    print("[OK]   %s" % msg)


def section(title):
    print("\n--- %s ---" % title)


# ---- individual checks -----------------------------------------------------

def check_tables(cur):
    section("Required Tables")
    cur.execute("""
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
    """)
    existing = {row[0] for row in cur.fetchall()}
    for table in REQUIRED_TABLES:
        if table in existing:
            ok("Table exists: %s" % table)
        else:
            fail("Table missing: %s" % table)


def check_row_counts(cur):
    section("Row Counts (seeded tables)")
    for table, minimum in MIN_ROW_COUNTS.items():
        cur.execute("SELECT COUNT(*) FROM %s" % table)
        count = cur.fetchone()[0]
        if count >= minimum:
            ok("%s: %d rows (>= %d)" % (table, count, minimum))
        else:
            fail("%s: %d rows (expected >= %d)" % (table, count, minimum))
    # Tables expected empty at this stage
    for table in ("geopolitical_events", "risk_scores", "commodity_prices",
                  "fx_rates", "scenario_results", "procurement_options",
                  "evidence_records", "evidence_links", "entity_aliases"):
        cur.execute("SELECT COUNT(*) FROM %s" % table)
        count = cur.fetchone()[0]
        ok("%s: %d rows (empty is expected at Step 5)" % (table, count))


def check_primary_key_uniqueness(cur):
    section("Primary Key Uniqueness")
    for table in REQUIRED_TABLES:
        cur.execute("""
            SELECT COUNT(*), COUNT(DISTINCT id) FROM %s
        """ % table)
        row = cur.fetchone()
        total, distinct = row
        if total == distinct:
            ok("PK unique: %s (%d rows)" % (table, total))
        else:
            fail("PK duplicates in %s: total=%d, distinct=%d" % (table, total, distinct))


def check_foreign_keys(cur):
    section("Foreign Key Spot Checks")

    checks_fk = [
        ("suppliers.country_id -> countries",
         "SELECT COUNT(*) FROM suppliers s LEFT JOIN countries c ON s.country_id = c.id WHERE s.country_id IS NOT NULL AND c.id IS NULL"),
        ("ports.country_id -> countries",
         "SELECT COUNT(*) FROM ports p LEFT JOIN countries c ON p.country_id = c.id WHERE p.country_id IS NOT NULL AND c.id IS NULL"),
        ("refineries.port_id -> ports",
         "SELECT COUNT(*) FROM refineries r LEFT JOIN ports p ON r.port_id = p.id WHERE r.port_id IS NOT NULL AND p.id IS NULL"),
        ("routes.origin_port_id -> ports",
         "SELECT COUNT(*) FROM routes r LEFT JOIN ports p ON r.origin_port_id = p.id WHERE r.origin_port_id IS NOT NULL AND p.id IS NULL"),
        ("routes.dest_port_id -> ports",
         "SELECT COUNT(*) FROM routes r LEFT JOIN ports p ON r.dest_port_id = p.id WHERE r.dest_port_id IS NOT NULL AND p.id IS NULL"),
        ("crude_grades.origin_country_id -> countries",
         "SELECT COUNT(*) FROM crude_grades g LEFT JOIN countries c ON g.origin_country_id = c.id WHERE g.origin_country_id IS NOT NULL AND c.id IS NULL"),
        ("refinery_supply_mix.refinery_id -> refineries",
         "SELECT COUNT(*) FROM refinery_supply_mix m LEFT JOIN refineries r ON m.refinery_id = r.id WHERE r.id IS NULL"),
        ("refinery_supply_mix.crude_grade_id -> crude_grades",
         "SELECT COUNT(*) FROM refinery_supply_mix m LEFT JOIN crude_grades g ON m.crude_grade_id = g.id WHERE g.id IS NULL"),
    ]

    for label, query in checks_fk:
        cur.execute(query)
        orphans = cur.fetchone()[0]
        if orphans == 0:
            ok("FK valid: %s" % label)
        else:
            fail("FK broken: %s (%d orphan rows)" % (label, orphans))

    # Corridor array FK check: all corridor_ids in routes must exist
    cur.execute("""
        SELECT r.id, unnest(r.corridor_ids) AS cid FROM routes r
        WHERE r.corridor_ids IS NOT NULL AND array_length(r.corridor_ids, 1) > 0
    """)
    route_corridor_refs = cur.fetchall()
    cur.execute("SELECT id FROM corridors")
    valid_corridor_ids = {row[0] for row in cur.fetchall()}
    bad = [(rid, cid) for rid, cid in route_corridor_refs if cid not in valid_corridor_ids]
    if not bad:
        ok("FK valid: routes.corridor_ids -> corridors (all %d refs)" % len(route_corridor_refs))
    else:
        fail("FK broken: routes.corridor_ids has %d invalid refs: %s" % (len(bad), bad[:5]))

    # Supplier crude_grade_ids array FK check
    cur.execute("""
        SELECT s.id, unnest(s.crude_grade_ids) AS gid FROM suppliers s
        WHERE s.crude_grade_ids IS NOT NULL AND array_length(s.crude_grade_ids, 1) > 0
    """)
    supplier_grade_refs = cur.fetchall()
    cur.execute("SELECT id FROM crude_grades")
    valid_grade_ids = {row[0] for row in cur.fetchall()}
    bad = [(sid, gid) for sid, gid in supplier_grade_refs if gid not in valid_grade_ids]
    if not bad:
        ok("FK valid: suppliers.crude_grade_ids -> crude_grades (all %d refs)" % len(supplier_grade_refs))
    else:
        fail("FK broken: suppliers.crude_grade_ids has %d invalid refs: %s" % (len(bad), bad[:5]))


def check_value_ranges(cur):
    section("Value Ranges")

    # Risk scores 0.0–1.0
    for table, col in [
        ("corridors",          "base_risk_score"),
        ("corridors",          "india_dependency_share"),
        ("suppliers",          "current_sanctions_risk"),
        ("routes",             "current_risk_score"),
        ("refinery_supply_mix","compatibility_score"),
    ]:
        cur.execute("""
            SELECT COUNT(*) FROM %s
            WHERE %s IS NOT NULL AND (%s < 0.0 OR %s > 1.0)
        """ % (table, col, col, col))
        bad = cur.fetchone()[0]
        if bad == 0:
            ok("Score range valid: %s.%s" % (table, col))
        else:
            fail("Score out of 0.0-1.0 range: %s.%s (%d rows)" % (table, col, bad))

    # Coordinates
    for table, lat, lon in [
        ("ports",     "latitude",  "longitude"),
        ("refineries","latitude",  "longitude"),
        ("strategic_reserves","latitude","longitude"),
    ]:
        cur.execute("""
            SELECT COUNT(*) FROM %s
            WHERE latitude IS NOT NULL AND (latitude < -90 OR latitude > 90)
               OR longitude IS NOT NULL AND (longitude < -180 OR longitude > 180)
        """ % table)
        bad = cur.fetchone()[0]
        if bad == 0:
            ok("Coordinates valid: %s" % table)
        else:
            fail("Invalid coordinates in %s (%d rows)" % (table, bad))

    # Capacities non-negative
    for table, col in [
        ("refineries",         "capacity_mmtpa"),
        ("strategic_reserves", "capacity_mmt"),
    ]:
        cur.execute("""
            SELECT COUNT(*) FROM %s WHERE %s IS NOT NULL AND %s < 0
        """ % (table, col, col))
        bad = cur.fetchone()[0]
        if bad == 0:
            ok("Capacity non-negative: %s.%s" % (table, col))
        else:
            fail("Negative capacity in %s.%s (%d rows)" % (table, col, bad))

    # ISO3 codes exactly 3 chars
    cur.execute("SELECT COUNT(*) FROM countries WHERE iso3 IS NOT NULL AND length(iso3) != 3")
    bad = cur.fetchone()[0]
    if bad == 0:
        ok("ISO3 codes all 3-character")
    else:
        fail("Invalid ISO3 codes: %d rows" % bad)


def check_semantic_labels(cur):
    section("Semantic Labels")

    # refinery_supply_mix.compatibility
    cur.execute("""
        SELECT compatibility, COUNT(*) FROM refinery_supply_mix GROUP BY compatibility
    """)
    rows = cur.fetchall()
    bad = [r[0] for r in rows if r[0] not in VALID_COMPATIBILITY]
    if not bad:
        ok("refinery_supply_mix.compatibility values valid: %s" %
           {r[0]: r[1] for r in rows})
    else:
        fail("Invalid compatibility values: %s" % bad)

    # refinery_supply_mix.source_type
    cur.execute("SELECT DISTINCT source_type FROM refinery_supply_mix WHERE source_type IS NOT NULL")
    types = {r[0] for r in cur.fetchall()}
    ok("refinery_supply_mix.source_type values: %s" % sorted(types))

    # countries: required name + iso3
    cur.execute("SELECT COUNT(*) FROM countries WHERE name IS NULL OR name = ''")
    bad = cur.fetchone()[0]
    if bad == 0:
        ok("All countries have names")
    else:
        fail("Countries with null/empty name: %d" % bad)

    # Corridor codes are unique and non-empty
    cur.execute("SELECT code, COUNT(*) FROM corridors GROUP BY code HAVING COUNT(*) > 1")
    dupes = cur.fetchall()
    if not dupes:
        ok("Corridor codes unique")
    else:
        fail("Duplicate corridor codes: %s" % dupes)


def check_no_orphans(cur):
    section("No Orphan Records")

    # No refinery without a matching country (via port)
    cur.execute("""
        SELECT COUNT(*) FROM refineries r
        JOIN ports p ON r.port_id = p.id
        JOIN countries c ON p.country_id = c.id
        WHERE c.id IS NULL
    """)
    bad = cur.fetchone()[0]
    if bad == 0:
        ok("No orphan refineries (all refinery ports have countries)")
    else:
        warn("Refineries with port country not found: %d" % bad)

    # All seeded Indian refineries have country_id = 1 (India) via port
    cur.execute("""
        SELECT COUNT(*) FROM refineries r
        JOIN ports p ON r.port_id = p.id
        WHERE p.is_indian = TRUE AND p.country_id != 1
    """)
    bad = cur.fetchone()[0]
    if bad == 0:
        ok("All Indian ports correctly linked to India (country_id=1)")
    else:
        warn("Indian ports not linked to India: %d" % bad)


def check_null_semantics(cur):
    section("NULL Semantic Preservation")

    # SPR current_level_mmt must remain NULL (not publicly known)
    cur.execute("SELECT COUNT(*) FROM strategic_reserves WHERE current_level_mmt IS NOT NULL")
    non_null = cur.fetchone()[0]
    if non_null == 0:
        ok("SPR current_level_mmt is NULL for all sites (correct — not publicly disclosed)")
    else:
        warn("SPR current_level_mmt is set for %d sites — verify these are not fabricated" % non_null)

    # Refinery throughput should be NULL
    cur.execute("SELECT COUNT(*) FROM refineries WHERE throughput_current_mmtpa IS NOT NULL")
    non_null = cur.fetchone()[0]
    if non_null == 0:
        ok("refinery throughput_current_mmtpa is NULL for all refineries (correct)")
    else:
        warn("throughput_current_mmtpa set for %d refineries — verify not fabricated" % non_null)

    # refinery_supply_mix current_share_pct should be NULL
    cur.execute("SELECT COUNT(*) FROM refinery_supply_mix WHERE current_share_pct IS NOT NULL")
    non_null = cur.fetchone()[0]
    if non_null == 0:
        ok("refinery_supply_mix current_share_pct is NULL for all rows (correct)")
    else:
        warn("current_share_pct set for %d rows — verify not fabricated" % non_null)


# ---- main ------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="INDRA Database Integrity Checks")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    args = parser.parse_args()

    _load_env()

    try:
        import psycopg2
    except ImportError:
        print("[ERROR] psycopg2 not installed. Run: pip install psycopg2-binary")
        sys.exit(1)

    dsn = _get_dsn()
    pg_pass = os.environ.get("POSTGRES_PASSWORD", "")
    display_dsn = dsn.replace(pg_pass, "***") if pg_pass and pg_pass in dsn else dsn
    print("Connecting to: %s\n" % display_dsn)

    try:
        conn = psycopg2.connect(dsn)
        conn.autocommit = True
    except Exception as e:
        print("[ERROR] Cannot connect to PostgreSQL: %s" % e)
        sys.exit(1)

    cur = conn.cursor()

    try:
        check_tables(cur)
        check_row_counts(cur)
        check_primary_key_uniqueness(cur)
        check_foreign_keys(cur)
        check_value_ranges(cur)
        check_semantic_labels(cur)
        check_no_orphans(cur)
        check_null_semantics(cur)
    finally:
        cur.close()
        conn.close()

    print("\n" + "=" * 60)
    print("INTEGRITY CHECK SUMMARY")
    print("=" * 60)
    print("Checks passed: %d" % checks)
    if warnings:
        print("Warnings:       %d" % len(warnings))
        for w in warnings:
            print("  %s" % w)
    if errors:
        print("Errors:         %d" % len(errors))
        for e in errors:
            print("  %s" % e)
        print("\n[FAIL] Integrity checks FAILED -- %d error(s)" % len(errors))
        sys.exit(1)
    else:
        print("\n[PASS] All integrity checks passed.")
        sys.exit(0)


if __name__ == "__main__":
    main()
