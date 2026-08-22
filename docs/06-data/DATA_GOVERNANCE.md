# INDRA Data Governance

## Scope and baseline

This is the lifecycle contract for reference, seed, historical, and ingested data entering INDRA’s single PostgreSQL source of truth. It preserves the frozen semantic categories: `OBSERVED`, `DERIVED`, `HISTORICAL_CALIBRATED`, `ASSUMED`, and `SIMULATED`. It does not make unavailable external sources live.

The current reference-data inventory is `data/metadata/data_manifest.json`. Its entries record a dataset ID, source, acquisition timestamp (`downloaded_at`), semantic class, transformation, record count, checksum, and target table. Historical acquisition status is retained in `data/metadata/historical_acquisition.json` where applicable.

## Dataset versioning

Do not duplicate unchanged source files. A material data change creates a new manifest entry or updates the existing entry with a traceable version. Every important new or revised dataset must record:

| Field | Requirement |
|---|---|
| `dataset_version` | Immutable human-readable release/version identifier. |
| `source_name` and `source_url` | Publisher and retrieval location. |
| `acquired_at` / source timestamp | UTC acquisition time and source observation/publication time when known. |
| `data_semantic` | One frozen semantic category, never a live-data inference. |
| `schema_version` | Input-column/schema contract version. |
| `transformation_version` | Normalizer/curation/derivation version or commit reference. |
| `checksum` | SHA-256 for file-backed inputs and output artifacts where practical. |
| `target_table` and provenance | PostgreSQL destination plus source/ingestion evidence path. |

The Step-4 manifest is a legacy inventory with equivalent fields named `manifest_version`, `downloaded_at`, `semantic_class`, and `transformation`. New entries use the forward field names above; existing entries are not rewritten merely for formatting.

## Data quality gate

No source record becomes a database observation until it passes:

```text
source → fetch metadata → schema validation → semantic validation
       → duplicate detection → reference/FK validation → provenance validation
       → accepted or rejected with reason → PostgreSQL persistence
```

1. Adapters parse into `NormalizedEvent`, `NormalizedPrice`, `NormalizedFxRate`, or sanctions records and retain source timestamps.
2. `validate_*()` methods enforce required fields, value constraints, and canonical semantic labels.
3. Source-aware deduplication prevents repeated event/market observations from silently creating new facts.
4. Seed validation checks primary/reference identifiers and foreign-key-like links before load; `scripts/db/check_db.py` checks database FK/integrity after load.
5. Persistence writes source, timestamps, semantic label, and evidence/provenance attributes. Invalid rows are counted and reported, never silently converted.

Run locally:

```powershell
python scripts/data/validate_seed_data.py
python scripts/data/validate_historical_data.py
python scripts/db/check_db.py
```

## Change approval

A dataset change requires a review record covering source/license/access, manifest/version metadata, semantic classification, validation output, checksum, duplicate behavior, target-table impact, and rollback path. Changes to calibrated assumptions also require domain-owner sign-off; they are not reported as observed facts.

Credentialed feeds remain optional: an absent key/feed is represented as `NOT_CONFIGURED`, `REQUIRES_ACCESS`, or `DEFERRED`, not as empty observed data.
