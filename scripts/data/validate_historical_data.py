#!/usr/bin/env python3
"""
INDRA -- Historical Data Validation Script
Validates processed historical data files for format correctness.

Usage:
    python scripts/data/validate_historical_data.py
"""

import csv
import sys
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

errors = []
warnings = []
stats = {}


def error(file, msg):
    errors.append("[ERROR] %s: %s" % (file, msg))


def warn(file, msg):
    warnings.append("[WARN] %s: %s" % (file, msg))


def validate_commodity_prices():
    """Validate EIA commodity prices if present."""
    path = PROCESSED_DIR / "eia" / "commodity_prices.csv"
    name = "eia/commodity_prices.csv"
    if not path.exists():
        warn(name, "File not found -- EIA prices not yet acquired (REQUIRES_REGISTRATION)")
        stats[name] = 0
        return

    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    stats[name] = len(rows)

    required = ["grade_name", "price_usd_per_barrel", "source", "source_timestamp", "data_semantic"]
    for i, row in enumerate(rows):
        for field in required:
            if field not in row or not row[field].strip():
                error(name, "Row %d: missing field '%s'" % (i + 1, field))
                continue

        # Price must be positive
        try:
            price = float(row.get("price_usd_per_barrel", "0"))
            if price <= 0:
                error(name, "Row %d: price %.4f is not positive" % (i + 1, price))
            elif price > 200:
                warn(name, "Row %d: price %.4f seems unusually high" % (i + 1, price))
        except ValueError:
            error(name, "Row %d: invalid price '%s'" % (i + 1, row.get("price_usd_per_barrel")))

        # Source timestamp format
        ts = row.get("source_timestamp", "")
        if ts:
            try:
                datetime.fromisoformat(ts.replace("Z", "+00:00"))
            except ValueError:
                error(name, "Row %d: invalid timestamp '%s'" % (i + 1, ts))

        # Data semantic must match frozen schema classification
        semantic = row.get("data_semantic", "")
        valid_semantics = ("OBSERVED", "DERIVED", "HISTORICAL_CALIBRATED", "ASSUMED", "SIMULATED")
        if semantic and semantic not in valid_semantics:
            error(name, "Row %d: unexpected data_semantic '%s' (valid: %s)" % (i + 1, semantic, ', '.join(valid_semantics)))


def validate_fx_rates():
    """Validate RBI FX rates."""
    path = PROCESSED_DIR / "rbi" / "fx_rates.csv"
    name = "rbi/fx_rates.csv"
    if not path.exists():
        warn(name, "File not found -- RBI rates not yet acquired")
        stats[name] = 0
        return

    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    stats[name] = len(rows)

    required = ["currency_pair", "rate", "source", "source_timestamp", "data_semantic"]
    for i, row in enumerate(rows):
        for field in required:
            if field not in row or not row[field].strip():
                error(name, "Row %d: missing field '%s'" % (i + 1, field))

        # Rate must be reasonable for USD/INR
        try:
            rate = float(row.get("rate", "0"))
            if rate <= 0:
                error(name, "Row %d: rate %.4f is not positive" % (i + 1, rate))
            elif rate < 30 or rate > 120:
                warn(name, "Row %d: USD/INR rate %.4f outside expected range [30, 120]" % (i + 1, rate))
        except ValueError:
            error(name, "Row %d: invalid rate '%s'" % (i + 1, row.get("rate")))

        # Currency pair check
        pair = row.get("currency_pair", "")
        if pair and pair != "USD_INR":
            warn(name, "Row %d: unexpected currency pair '%s'" % (i + 1, pair))


def validate_ofac_entities():
    """Validate processed OFAC sanctions entities."""
    path = PROCESSED_DIR / "ofac" / "sanctions_entities.csv"
    name = "ofac/sanctions_entities.csv"
    if not path.exists():
        warn(name, "File not found -- OFAC data not yet acquired")
        stats[name] = 0
        return

    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    stats[name] = len(rows)

    # Match the current OfacAdapter.write_processed() contract. Source
    # provenance belongs to the OFAC adapter/acquisition manifest; this
    # normalized extract retains the official SDN identifier and entity name.
    required = ["entity_id", "entity_name", "data_semantic"]
    for i, row in enumerate(rows):
        for field in required:
            if field not in row or not row[field].strip():
                error(name, "Row %d: missing field '%s'" % (i + 1, field))

        if not row.get("entity_id", "").strip():
            error(name, "Row %d: empty OFAC entity identifier" % (i + 1))

        # Data semantic check
        semantic = row.get("data_semantic", "")
        if semantic and semantic != "OBSERVED":
            warn(name, "Row %d: OFAC data should be OBSERVED, got '%s'" % (i + 1, semantic))


def main():
    print("=" * 60)
    print("INDRA -- Historical Data Validation")
    print("Processed directory: %s" % PROCESSED_DIR)
    print("=" * 60)

    validate_commodity_prices()
    validate_fx_rates()
    validate_ofac_entities()

    print("\n" + "=" * 60)
    print("VALIDATION RESULTS")
    print("=" * 60)

    print("\nDataset sizes:")
    for name, count in sorted(stats.items()):
        print("  %s: %d rows" % (name, count))

    if warnings:
        print("\n[WARN] %d warnings:" % len(warnings))
        for w in warnings:
            print("  %s" % w)

    if errors:
        print("\n[FAIL] %d errors:" % len(errors))
        for e in errors:
            print("  %s" % e)
        print("\n[FAIL] VALIDATION FAILED -- %d error(s) found" % len(errors))
        sys.exit(1)
    else:
        print("\n[PASS] VALIDATION PASSED -- all historical datasets are valid")
        print("   Total datasets validated: %d" % len(stats))
        print("   Total rows: %d" % sum(stats.values()))
        sys.exit(0)


if __name__ == "__main__":
    main()
