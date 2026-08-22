"""RBI USD/INR reference rate adapter.

RBI does not expose a reliable bulk automation API. This adapter:
1. Attempts to load official processed CSV if present (Step 4 sample / manual DBIE export)
2. Does NOT fabricate current FX values when no data is available
"""
from __future__ import annotations

import csv
import logging
from datetime import datetime, timezone
from pathlib import Path

from app.config.settings import get_settings
from app.ingestion.base import FetchResult, NormalizedFxRate, SourceRecord
from app.ingestion.normalizers import parse_datetime

logger = logging.getLogger("indra.ingestion.rbi")

PROJECT_ROOT = Path(__file__).resolve().parents[3]


class RbiAdapter:
    source_name = "RBI"
    source_type = "fx_rate"

    def __init__(self, processed_path: Path | None = None):
        self.processed_path = processed_path or (PROJECT_ROOT / "data" / "processed" / "rbi" / "fx_rates.csv")

    async def fetch(self) -> FetchResult:
        """Load from processed official-format CSV; no unofficial FX APIs."""
        fetched_at = datetime.now(timezone.utc)
        if not self.processed_path.exists():
            return FetchResult(
                source_name=self.source_name,
                fetched_at=fetched_at,
                success=False,
                error=f"RBI processed file not found: {self.processed_path}. Manual DBIE export required for bulk FX.",
            )
        try:
            rows = []
            with open(self.processed_path, newline="", encoding="utf-8") as handle:
                reader = csv.DictReader(handle)
                for row in reader:
                    rows.append(row)
            if not rows:
                return FetchResult(
                    source_name=self.source_name,
                    fetched_at=fetched_at,
                    success=False,
                    error="RBI processed CSV is empty",
                )
            return FetchResult(
                source_name=self.source_name,
                fetched_at=fetched_at,
                success=True,
                raw_payload={"rows": rows, "path": str(self.processed_path)},
            )
        except Exception as exc:
            return FetchResult(
                source_name=self.source_name,
                fetched_at=fetched_at,
                success=False,
                error=str(exc),
            )

    def parse(self, raw) -> list[SourceRecord]:
        rows = (raw or {}).get("rows") or []
        records = []
        for row in rows:
            pair = row.get("currency_pair") or "USD_INR"
            date = row.get("source_timestamp") or row.get("observation_date")
            rate = row.get("rate")
            if rate is None:
                continue
            record_id = f"{pair}:{date}:{rate}"
            records.append(SourceRecord(source_record_id=record_id, payload=row))
        return records

    def normalize_fx(self, records: list[SourceRecord]) -> list[NormalizedFxRate]:
        rates = []
        for record in records:
            row = record.payload
            ts = parse_datetime(row.get("source_timestamp") or row.get("observation_date"))
            rates.append(
                NormalizedFxRate(
                    currency_pair=row.get("currency_pair") or "USD_INR",
                    rate=float(row["rate"]),
                    source=self.source_name,
                    source_record_id=record.source_record_id,
                    source_timestamp=ts,
                    data_semantic=row.get("data_semantic") or "OBSERVED",
                )
            )
        return rates

    def validate_fx(self, rates: list[NormalizedFxRate]) -> tuple[list[NormalizedFxRate], list[str]]:
        accepted, rejected = [], []
        for rate in rates:
            if rate.rate <= 0 or rate.rate > 200:
                rejected.append(rate.source_record_id)
                continue
            accepted.append(rate)
        return accepted, rejected
