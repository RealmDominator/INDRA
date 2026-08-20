#!/usr/bin/env python3
"""
INDRA -- Seed Data Loader
Loads curated seed CSV files into PostgreSQL using INSERT statements.

This is a one-time utility script, NOT an application service.
It reads CSVs from data/seed/ and generates SQL INSERT statements
that can be applied to a PostgreSQL database.

Usage:
    python scripts/data/load_seed_data.py > db/seed.sql
    python scripts/data/load_seed_data.py --execute  # Direct DB load (requires DATABASE_URL env var)
"""

import csv
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SEED_DIR = PROJECT_ROOT / "data" / "seed"


def escape_sql(value):
    """Escape a value for SQL insertion."""
    if value is None or value == "" or value.strip() == "":
        return "NULL"
    # Escape single quotes
    escaped = value.replace("'", "''")
    return "'%s'" % escaped


def format_array(value):
    """Convert comma-separated string to PostgreSQL array literal."""
    if value is None or value == "" or value.strip() == "":
        return "NULL"
    items = [v.strip() for v in value.split(",") if v.strip()]
    if not items:
        return "NULL"
    # Check if items are numeric
    try:
        [int(i) for i in items]
        return "ARRAY[%s]" % ",".join(items)
    except ValueError:
        return "ARRAY[%s]" % ",".join("'%s'" % i.replace("'", "''") for i in items)


def format_bool(value):
    """Convert string boolean to SQL boolean."""
    if value is None or value == "" or value.strip() == "":
        return "NULL"
    return "TRUE" if value.upper() in ("TRUE", "1", "YES") else "FALSE"


def format_decimal(value):
    """Convert string decimal to SQL decimal."""
    if value is None or value == "" or value.strip() == "":
        return "NULL"
    try:
        float(value)
        return value
    except ValueError:
        return "NULL"


def format_int(value):
    """Convert string int to SQL int."""
    if value is None or value == "" or value.strip() == "":
        return "NULL"
    try:
        return str(int(value))
    except ValueError:
        return "NULL"


def format_json(value):
    """Format a JSON string for SQL."""
    if value is None or value == "" or value.strip() == "":
        return "NULL"
    # Validate it's valid JSON
    try:
        json.loads(value)
        return "'%s'::jsonb" % value.replace("'", "''")
    except json.JSONDecodeError:
        return "NULL"


def read_csv_file(filename):
    """Read a CSV file and return rows."""
    path = SEED_DIR / filename
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def generate_countries_sql(rows):
    """Generate INSERT statements for countries."""
    lines = []
    lines.append("-- Countries (%d rows)" % len(rows))
    lines.append("-- Source: ISO 3166-1 / PPAC / research reports")
    for row in rows:
        lines.append(
            "INSERT INTO countries (id, name, iso3, base_risk_score, region, is_hormuz_dependent, is_red_sea_dependent) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)"
            " ON CONFLICT (id) DO NOTHING;" % (
                format_int(row["id"]),
                escape_sql(row["name"]),
                escape_sql(row["iso3"]),
                "NULL",  # base_risk_score deferred to risk engine
                escape_sql(row.get("region", "")),
                format_bool(row.get("is_hormuz_dependent", "")),
                format_bool(row.get("is_red_sea_dependent", "")),
            )
        )
    return "\n".join(lines)


def generate_corridors_sql(rows):
    """Generate INSERT statements for corridors."""
    lines = []
    lines.append("\n-- Corridors (%d rows)" % len(rows))
    lines.append("-- Source: INDRA architecture / PPAC / research reports")
    for row in rows:
        lines.append(
            "INSERT INTO corridors (id, code, name, description, corridor_type, "
            "affected_countries, base_risk_score, india_dependency_share, is_active) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
            " ON CONFLICT (id) DO NOTHING;" % (
                format_int(row["id"]),
                escape_sql(row["code"]),
                escape_sql(row["name"]),
                escape_sql(row.get("description", "")),
                escape_sql(row.get("corridor_type", "")),
                format_array(row.get("affected_countries", "")),
                format_decimal(row.get("base_risk_score", "")),
                format_decimal(row.get("india_dependency_share", "")),
                format_bool(row.get("is_active", "TRUE")),
            )
        )
    return "\n".join(lines)


def generate_crude_grades_sql(rows):
    """Generate INSERT statements for crude_grades."""
    lines = []
    lines.append("\n-- Crude Grades (%d rows)" % len(rows))
    lines.append("-- Source: EIA / industry references")
    for row in rows:
        lines.append(
            "INSERT INTO crude_grades (id, name, api_gravity, sulfur_content_pct, "
            "category, origin_country_id, notes) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)"
            " ON CONFLICT (id) DO NOTHING;" % (
                format_int(row["id"]),
                escape_sql(row["name"]),
                format_decimal(row.get("api_gravity", "")),
                format_decimal(row.get("sulfur_content_pct", "")),
                escape_sql(row.get("category", "")),
                format_int(row.get("origin_country_id", "")),
                escape_sql(row.get("source", "")),
            )
        )
    return "\n".join(lines)


def generate_ports_sql(rows):
    """Generate INSERT statements for ports."""
    lines = []
    lines.append("\n-- Ports (%d rows)" % len(rows))
    lines.append("-- Source: UN/LOCODE / Indian Port Association / research reports")
    for row in rows:
        lines.append(
            "INSERT INTO ports (id, name, un_locode, country_id, is_indian, "
            "latitude, longitude, annual_crude_throughput_mmtpa, current_operational_status) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
            " ON CONFLICT (id) DO NOTHING;" % (
                format_int(row["id"]),
                escape_sql(row["name"]),
                escape_sql(row.get("un_locode", "")),
                format_int(row.get("country_id", "")),
                format_bool(row.get("is_indian", "")),
                format_decimal(row.get("latitude", "")),
                format_decimal(row.get("longitude", "")),
                format_decimal(row.get("annual_crude_throughput_mmtpa", "")),
                escape_sql(row.get("current_operational_status", "OPERATIONAL")),
            )
        )
    return "\n".join(lines)


def generate_refineries_sql(rows):
    """Generate INSERT statements for refineries."""
    lines = []
    lines.append("\n-- Refineries (%d rows)" % len(rows))
    lines.append("-- Source: PPAC Annual Report / research reports")
    for row in rows:
        lines.append(
            "INSERT INTO refineries (id, name, owner, state, port_id, capacity_mmtpa, "
            "throughput_current_mmtpa, latitude, longitude) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
            " ON CONFLICT (id) DO NOTHING;" % (
                format_int(row["id"]),
                escape_sql(row["name"]),
                escape_sql(row.get("owner", "")),
                escape_sql(row.get("state", "")),
                format_int(row.get("port_id", "")),
                format_decimal(row.get("capacity_mmtpa", "")),
                format_decimal(row.get("throughput_current_mmtpa", "")),
                format_decimal(row.get("latitude", "")),
                format_decimal(row.get("longitude", "")),
            )
        )
    return "\n".join(lines)


def generate_suppliers_sql(rows):
    """Generate INSERT statements for suppliers."""
    lines = []
    lines.append("\n-- Suppliers (%d rows)" % len(rows))
    lines.append("-- Source: PPAC / OFAC / research reports")
    for row in rows:
        lines.append(
            "INSERT INTO suppliers (id, name, country_id, crude_grade_ids, "
            "annual_supply_capacity_mmtpa, current_sanctions_risk, is_sanctioned, sanction_source) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            " ON CONFLICT (id) DO NOTHING;" % (
                format_int(row["id"]),
                escape_sql(row["name"]),
                format_int(row.get("country_id", "")),
                format_array(row.get("crude_grade_ids", "")),
                format_decimal(row.get("annual_supply_capacity_mmtpa", "")),
                format_decimal(row.get("current_sanctions_risk", "")),
                format_bool(row.get("is_sanctioned", "")),
                escape_sql(row.get("sanction_source", "")),
            )
        )
    return "\n".join(lines)


def generate_refinery_supply_mix_sql(rows):
    """Generate INSERT statements for refinery_supply_mix."""
    lines = []
    lines.append("\n-- Refinery Supply Mix (%d rows)" % len(rows))
    lines.append("-- Source: ESTIMATED from research report crude-slate categories")
    lines.append("-- NOTE: All compatibility values are ESTIMATED. No fabricated share percentages.")
    for row in rows:
        lines.append(
            "INSERT INTO refinery_supply_mix (refinery_id, crude_grade_id, compatibility, "
            "compatibility_score, current_share_pct, max_share_pct, source_type, notes) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s);" % (
                format_int(row["refinery_id"]),
                format_int(row["crude_grade_id"]),
                escape_sql(row.get("compatibility", "")),
                format_decimal(row.get("compatibility_score", "")),
                format_decimal(row.get("current_share_pct", "")),
                format_decimal(row.get("max_share_pct", "")),
                escape_sql(row.get("source_type", "ESTIMATED")),
                escape_sql(row.get("notes", "")),
            )
        )
    return "\n".join(lines)


def generate_routes_sql(rows):
    """Generate INSERT statements for routes."""
    lines = []
    lines.append("\n-- Routes (%d rows)" % len(rows))
    lines.append("-- Source: Sea-distances.org / industry references")
    for row in rows:
        lines.append(
            "INSERT INTO routes (id, name, origin_port_id, dest_port_id, corridor_ids, "
            "distance_nm, avg_transit_days, base_freight_rate_per_mt, current_risk_score, is_operational) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            " ON CONFLICT (id) DO NOTHING;" % (
                format_int(row["id"]),
                escape_sql(row["name"]),
                format_int(row.get("origin_port_id", "")),
                format_int(row.get("dest_port_id", "")),
                format_array(row.get("corridor_ids", "")),
                format_int(row.get("distance_nm", "")),
                format_decimal(row.get("avg_transit_days", "")),
                format_decimal(row.get("base_freight_rate_per_mt", "")),
                format_decimal(row.get("current_risk_score", "")),
                format_bool(row.get("is_operational", "TRUE")),
            )
        )
    return "\n".join(lines)


def generate_spr_sql(rows):
    """Generate INSERT statements for strategic_reserves."""
    lines = []
    lines.append("\n-- Strategic Petroleum Reserves (%d rows)" % len(rows))
    lines.append("-- Source: ISPRL official website / MoPNG reports")
    for row in rows:
        lines.append(
            "INSERT INTO strategic_reserves (id, location_name, operator, state, capacity_mmt, "
            "current_level_mmt, latitude, longitude, data_classification) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
            " ON CONFLICT (id) DO NOTHING;" % (
                format_int(row["id"]),
                escape_sql(row["location_name"]),
                escape_sql(row.get("operator", "")),
                escape_sql(row.get("state", "")),
                format_decimal(row.get("capacity_mmt", "")),
                format_decimal(row.get("current_level_mmt", "")),
                format_decimal(row.get("latitude", "")),
                format_decimal(row.get("longitude", "")),
                escape_sql(row.get("data_classification", "HISTORICAL")),
            )
        )
    return "\n".join(lines)


def generate_data_sources_sql(rows):
    """Generate INSERT statements for data_sources."""
    lines = []
    lines.append("\n-- Data Sources (%d rows)" % len(rows))
    for row in rows:
        lines.append(
            "INSERT INTO data_sources (id, name, url, update_frequency, status, classification) "
            "VALUES (%s, %s, %s, %s, %s, %s)"
            " ON CONFLICT (id) DO NOTHING;" % (
                format_int(row["id"]),
                escape_sql(row["name"]),
                escape_sql(row.get("url", "")),
                escape_sql(row.get("update_frequency", "")),
                escape_sql(row.get("status", "ACTIVE")),
                escape_sql(row.get("classification", "")),
            )
        )
    return "\n".join(lines)


def generate_scenarios_sql(rows):
    """Generate INSERT statements for scenarios."""
    lines = []
    lines.append("\n-- Preset Scenarios (%d rows)" % len(rows))
    lines.append("-- Source: SCENARIO_ENGINE.md / research reports / EIA historical calibration")
    for row in rows:
        lines.append(
            "INSERT INTO scenarios (id, name, scenario_type, parameters) "
            "VALUES (%s, %s, %s, %s)"
            " ON CONFLICT (id) DO NOTHING;" % (
                format_int(row["id"]),
                escape_sql(row["name"]),
                escape_sql(row.get("scenario_type", "")),
                format_json(row.get("parameters", "")),
            )
        )
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="INDRA Seed Data Loader")
    parser.add_argument("--output", default=None, help="Output SQL file (default: stdout)")
    args = parser.parse_args()

    header = """-- =============================================================================
-- INDRA -- Seed Data (PostgreSQL)
-- =============================================================================
-- STATUS: GENERATED from curated CSV seed datasets (Step 4, %s)
--
-- This file contains INSERT statements for India-specific reference data.
-- All data sources are documented in docs/06-data/DATA_ACQUISITION_PLAN.md
-- and data/metadata/data_manifest.json.
--
-- Source CSVs: data/seed/*.csv
-- Generated by: scripts/data/load_seed_data.py
-- =============================================================================
""" % datetime.now().strftime("%d %B %Y")

    sections = []
    sections.append(header)

    # Load and generate in dependency order
    sections.append(generate_countries_sql(read_csv_file("countries.csv")))
    sections.append(generate_corridors_sql(read_csv_file("corridors.csv")))
    sections.append(generate_crude_grades_sql(read_csv_file("crude_grades.csv")))
    sections.append(generate_ports_sql(read_csv_file("ports.csv")))
    sections.append(generate_refineries_sql(read_csv_file("refineries.csv")))
    sections.append(generate_suppliers_sql(read_csv_file("suppliers.csv")))
    sections.append(generate_refinery_supply_mix_sql(read_csv_file("refinery_supply_mix.csv")))
    sections.append(generate_routes_sql(read_csv_file("routes.csv")))
    sections.append(generate_spr_sql(read_csv_file("spr.csv")))
    sections.append(generate_data_sources_sql(read_csv_file("data_sources.csv")))
    sections.append(generate_scenarios_sql(read_csv_file("scenarios.csv")))

    # Sequence resets
    sections.append("""
-- =============================================================================
-- Reset sequences to max(id) + 1 for each table
-- =============================================================================
SELECT setval('countries_id_seq', (SELECT COALESCE(MAX(id), 0) FROM countries) + 1, false);
SELECT setval('corridors_id_seq', (SELECT COALESCE(MAX(id), 0) FROM corridors) + 1, false);
SELECT setval('crude_grades_id_seq', (SELECT COALESCE(MAX(id), 0) FROM crude_grades) + 1, false);
SELECT setval('ports_id_seq', (SELECT COALESCE(MAX(id), 0) FROM ports) + 1, false);
SELECT setval('refineries_id_seq', (SELECT COALESCE(MAX(id), 0) FROM refineries) + 1, false);
SELECT setval('suppliers_id_seq', (SELECT COALESCE(MAX(id), 0) FROM suppliers) + 1, false);
SELECT setval('routes_id_seq', (SELECT COALESCE(MAX(id), 0) FROM routes) + 1, false);
SELECT setval('strategic_reserves_id_seq', (SELECT COALESCE(MAX(id), 0) FROM strategic_reserves) + 1, false);
SELECT setval('data_sources_id_seq', (SELECT COALESCE(MAX(id), 0) FROM data_sources) + 1, false);
SELECT setval('scenarios_id_seq', (SELECT COALESCE(MAX(id), 0) FROM scenarios) + 1, false);
""")

    output = "\n".join(sections)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print("Seed SQL written to: %s" % args.output)
    else:
        print(output)


if __name__ == "__main__":
    main()
