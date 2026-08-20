#!/usr/bin/env python3
"""
INDRA — Seed Data Validation Script
Validates all seed CSV files for completeness, consistency, and referential integrity.

Usage:
    python scripts/data/validate_seed_data.py
"""

import csv
import sys
from pathlib import Path
from collections import defaultdict

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SEED_DIR = PROJECT_ROOT / "data" / "seed"

# Track validation results
errors = []
warnings = []
stats = defaultdict(int)


def error(file: str, msg: str):
    errors.append(f"[ERROR] {file}: {msg}")


def warn(file: str, msg: str):
    warnings.append(f"[WARN] {file}: {msg}")


def read_csv(filename: str) -> list[dict]:
    """Read a CSV file and return list of row dicts."""
    path = SEED_DIR / filename
    if not path.exists():
        error(filename, f"File not found: {path}")
        return []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    stats[filename] = len(rows)
    return rows


def validate_required_fields(filename: str, rows: list[dict], required: list[str]):
    """Check that required fields are present and non-empty."""
    for i, row in enumerate(rows):
        for field in required:
            if field not in row:
                error(filename, f"Row {i+1}: missing field '{field}'")
            elif not row[field] or row[field].strip() == "":
                error(filename, f"Row {i+1}: empty required field '{field}'")


def validate_unique(filename: str, rows: list[dict], field: str):
    """Check uniqueness of a field."""
    seen = {}
    for i, row in enumerate(rows):
        val = row.get(field, "")
        if val in seen:
            error(filename, f"Row {i+1}: duplicate '{field}' = '{val}' (first seen at row {seen[val]})")
        seen[val] = i + 1


def validate_positive_decimal(filename: str, rows: list[dict], field: str, allow_empty: bool = True):
    """Check that a decimal field is positive if present."""
    for i, row in enumerate(rows):
        val = row.get(field, "")
        if not val or val.strip() == "":
            if not allow_empty:
                error(filename, f"Row {i+1}: '{field}' is required but empty")
            continue
        try:
            num = float(val)
            if num < 0:
                error(filename, f"Row {i+1}: '{field}' = {val} is negative")
        except ValueError:
            error(filename, f"Row {i+1}: '{field}' = '{val}' is not a valid number")


def validate_coordinate(filename: str, rows: list[dict], lat_field: str, lon_field: str):
    """Validate latitude/longitude values."""
    for i, row in enumerate(rows):
        lat = row.get(lat_field, "")
        lon = row.get(lon_field, "")
        if lat and lat.strip():
            try:
                lat_val = float(lat)
                if lat_val < -90 or lat_val > 90:
                    error(filename, f"Row {i+1}: latitude {lat_val} out of range [-90, 90]")
            except ValueError:
                error(filename, f"Row {i+1}: latitude '{lat}' is not a valid number")
        if lon and lon.strip():
            try:
                lon_val = float(lon)
                if lon_val < -180 or lon_val > 180:
                    error(filename, f"Row {i+1}: longitude {lon_val} out of range [-180, 180]")
            except ValueError:
                error(filename, f"Row {i+1}: longitude '{lon}' is not a valid number")


def validate_fk_reference(filename: str, rows: list[dict], fk_field: str, ref_ids: set, ref_name: str):
    """Validate foreign key references."""
    for i, row in enumerate(rows):
        val = row.get(fk_field, "")
        if not val or val.strip() == "":
            continue
        # Handle comma-separated FK arrays
        ids = [v.strip() for v in val.split(",")]
        for id_val in ids:
            if id_val and id_val not in ref_ids:
                error(filename, f"Row {i+1}: '{fk_field}' = '{id_val}' not found in {ref_name}")


def validate_enum(filename: str, rows: list[dict], field: str, allowed: set, allow_empty: bool = True):
    """Validate that a field contains only allowed values."""
    for i, row in enumerate(rows):
        val = row.get(field, "")
        if not val or val.strip() == "":
            if not allow_empty:
                error(filename, f"Row {i+1}: '{field}' is required but empty")
            continue
        if val.strip() not in allowed:
            error(filename, f"Row {i+1}: '{field}' = '{val}' not in allowed values {allowed}")


def validate_iso3(filename: str, rows: list[dict]):
    """Validate ISO 3166-1 alpha-3 codes."""
    for i, row in enumerate(rows):
        iso3 = row.get("iso3", "")
        if iso3:
            if len(iso3) != 3:
                error(filename, f"Row {i+1}: iso3 '{iso3}' is not 3 characters")
            if not iso3.isalpha() or not iso3.isupper():
                error(filename, f"Row {i+1}: iso3 '{iso3}' should be uppercase letters")


def main():
    print("=" * 60)
    print("INDRA — Seed Data Validation")
    print(f"Seed directory: {SEED_DIR}")
    print("=" * 60)

    # === Countries ===
    print("\nValidating countries.csv...")
    countries = read_csv("countries.csv")
    validate_required_fields("countries.csv", countries, ["id", "name", "iso3"])
    validate_unique("countries.csv", countries, "id")
    validate_unique("countries.csv", countries, "iso3")
    validate_iso3("countries.csv", countries)
    country_ids = {row["id"] for row in countries}

    # === Corridors ===
    print("Validating corridors.csv...")
    corridors = read_csv("corridors.csv")
    validate_required_fields("corridors.csv", corridors, ["id", "code", "name"])
    validate_unique("corridors.csv", corridors, "id")
    validate_unique("corridors.csv", corridors, "code")
    validate_positive_decimal("corridors.csv", corridors, "base_risk_score")
    validate_positive_decimal("corridors.csv", corridors, "india_dependency_share")
    validate_enum("corridors.csv", corridors, "corridor_type",
                  {"CHOKEPOINT", "REGIONAL", "SUPPLIER_CORRIDOR"})
    corridor_ids = {row["id"] for row in corridors}

    # === Crude Grades ===
    print("Validating crude_grades.csv...")
    crude_grades = read_csv("crude_grades.csv")
    validate_required_fields("crude_grades.csv", crude_grades, ["id", "name"])
    validate_unique("crude_grades.csv", crude_grades, "id")
    validate_unique("crude_grades.csv", crude_grades, "name")
    validate_positive_decimal("crude_grades.csv", crude_grades, "api_gravity")
    validate_positive_decimal("crude_grades.csv", crude_grades, "sulfur_content_pct")
    validate_enum("crude_grades.csv", crude_grades, "category",
                  {"LIGHT_SWEET", "LIGHT_SOUR", "MEDIUM_SOUR", "HEAVY_SOUR"})
    validate_fk_reference("crude_grades.csv", crude_grades, "origin_country_id", country_ids, "countries")
    crude_grade_ids = {row["id"] for row in crude_grades}

    # === Ports ===
    print("Validating ports.csv...")
    ports = read_csv("ports.csv")
    validate_required_fields("ports.csv", ports, ["id", "name", "country_id"])
    validate_unique("ports.csv", ports, "id")
    validate_coordinate("ports.csv", ports, "latitude", "longitude")
    validate_fk_reference("ports.csv", ports, "country_id", country_ids, "countries")
    port_ids = {row["id"] for row in ports}

    # === Refineries ===
    print("Validating refineries.csv...")
    refineries = read_csv("refineries.csv")
    validate_required_fields("refineries.csv", refineries, ["id", "name", "owner", "state"])
    validate_unique("refineries.csv", refineries, "id")
    validate_positive_decimal("refineries.csv", refineries, "capacity_mmtpa")
    validate_coordinate("refineries.csv", refineries, "latitude", "longitude")
    validate_fk_reference("refineries.csv", refineries, "port_id", port_ids, "ports")
    refinery_ids = {row["id"] for row in refineries}

    # === Suppliers ===
    print("Validating suppliers.csv...")
    suppliers = read_csv("suppliers.csv")
    validate_required_fields("suppliers.csv", suppliers, ["id", "name", "country_id"])
    validate_unique("suppliers.csv", suppliers, "id")
    validate_fk_reference("suppliers.csv", suppliers, "country_id", country_ids, "countries")
    validate_fk_reference("suppliers.csv", suppliers, "crude_grade_ids", crude_grade_ids, "crude_grades")

    # === Refinery Supply Mix ===
    print("Validating refinery_supply_mix.csv...")
    mix = read_csv("refinery_supply_mix.csv")
    validate_required_fields("refinery_supply_mix.csv", mix, ["refinery_id", "crude_grade_id", "compatibility"])
    validate_fk_reference("refinery_supply_mix.csv", mix, "refinery_id", refinery_ids, "refineries")
    validate_fk_reference("refinery_supply_mix.csv", mix, "crude_grade_id", crude_grade_ids, "crude_grades")
    validate_enum("refinery_supply_mix.csv", mix, "compatibility",
                  {"HIGH", "MEDIUM", "LOW", "NONE"})
    validate_enum("refinery_supply_mix.csv", mix, "source_type",
                  {"PPAC_REPORTED", "COMPANY_REPORT", "ESTIMATED", "UNKNOWN"})
    validate_positive_decimal("refinery_supply_mix.csv", mix, "compatibility_score")

    # Check for duplicate refinery-grade combinations
    seen_combos = set()
    for i, row in enumerate(mix):
        combo = (row.get("refinery_id"), row.get("crude_grade_id"))
        if combo in seen_combos:
            error("refinery_supply_mix.csv",
                  f"Row {i+1}: duplicate refinery_id={combo[0]}, crude_grade_id={combo[1]}")
        seen_combos.add(combo)

    # === Routes ===
    print("Validating routes.csv...")
    routes = read_csv("routes.csv")
    validate_required_fields("routes.csv", routes, ["id", "name", "origin_port_id", "dest_port_id"])
    validate_unique("routes.csv", routes, "id")
    validate_fk_reference("routes.csv", routes, "origin_port_id", port_ids, "ports")
    validate_fk_reference("routes.csv", routes, "dest_port_id", port_ids, "ports")
    validate_fk_reference("routes.csv", routes, "corridor_ids", corridor_ids, "corridors")
    validate_positive_decimal("routes.csv", routes, "distance_nm")
    validate_positive_decimal("routes.csv", routes, "avg_transit_days")

    # === SPR ===
    print("Validating spr.csv...")
    spr = read_csv("spr.csv")
    validate_required_fields("spr.csv", spr, ["id", "location_name", "operator"])
    validate_unique("spr.csv", spr, "id")
    validate_positive_decimal("spr.csv", spr, "capacity_mmt")
    validate_coordinate("spr.csv", spr, "latitude", "longitude")

    # === Data Sources ===
    print("Validating data_sources.csv...")
    ds = read_csv("data_sources.csv")
    validate_required_fields("data_sources.csv", ds, ["id", "name"])
    validate_unique("data_sources.csv", ds, "id")

    # === Scenarios ===
    print("Validating scenarios.csv...")
    scenarios = read_csv("scenarios.csv")
    validate_required_fields("scenarios.csv", scenarios, ["id", "name", "scenario_type"])
    validate_unique("scenarios.csv", scenarios, "id")

    # === Summary ===
    print("\n" + "=" * 60)
    print("VALIDATION RESULTS")
    print("=" * 60)

    print("\nDataset sizes:")
    for filename, count in sorted(stats.items()):
        print(f"  {filename}: {count} rows")

    if warnings:
        print(f"\n[WARN] {len(warnings)} warnings:")
        for w in warnings:
            print(f"  {w}")

    if errors:
        print(f"\n[FAIL] {len(errors)} errors:")
        for e in errors:
            print(f"  {e}")
        print(f"\n[FAIL] VALIDATION FAILED -- {len(errors)} error(s) found")
        sys.exit(1)
    else:
        print(f"\n[PASS] VALIDATION PASSED -- all seed datasets are valid")
        print(f"   Total datasets: {len(stats)}")
        print(f"   Total rows: {sum(stats.values())}")
        sys.exit(0)


if __name__ == "__main__":
    main()
