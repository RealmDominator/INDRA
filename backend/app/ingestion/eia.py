"""EIA commodity price adapter."""
from __future__ import annotations

import logging
import time
from datetime import datetime, timezone

import httpx

from app.config.settings import get_settings
from app.ingestion.base import FetchResult, NormalizedPrice, SourceRecord
from app.ingestion.normalizers import parse_datetime

logger = logging.getLogger("indra.ingestion.eia")

EIA_BASE = "https://api.eia.gov/v2/petroleum/pri/spt/data/"


class EiaAdapter:
    source_name = "EIA"
    source_type = "commodity_price"

    SERIES = {"RBRTE": "Brent", "RWTC": "WTI"}

    def __init__(self, client: httpx.AsyncClient | None = None):
        self._client = client

    @property
    def is_configured(self) -> bool:
        return bool(get_settings().eia_api_key)

    async def fetch(self) -> FetchResult:
        settings = get_settings()
        if not self.is_configured:
            return FetchResult(
                source_name=self.source_name,
                fetched_at=datetime.now(timezone.utc),
                success=False,
                error="EIA_API_KEY not configured",
            )
        started = time.perf_counter()
        combined = {"response": {"data": []}}
        try:
            for series_id in self.SERIES:
                params = {
                    "api_key": settings.eia_api_key,
                    "frequency": "daily",
                    "data[0]": "value",
                    "facets[series][]": series_id,
                    "sort[0][column]": "period",
                    "sort[0][direction]": "desc",
                    "length": str(settings.eia_max_records),
                }
                if self._client is not None:
                    response = await self._client.get(EIA_BASE, params=params, timeout=settings.ingestion_timeout_seconds)
                else:
                    async with httpx.AsyncClient(timeout=settings.ingestion_timeout_seconds) as client:
                        response = await client.get(EIA_BASE, params=params)
                if response.status_code != 200:
                    return FetchResult(
                        source_name=self.source_name,
                        fetched_at=datetime.now(timezone.utc),
                        success=False,
                        error=f"HTTP {response.status_code} for series {series_id}",
                        http_status=response.status_code,
                    )
                payload = response.json()
                for row in payload.get("response", {}).get("data", []):
                    row["_grade_name"] = self.SERIES[series_id]
                    combined["response"]["data"].append(row)
            return FetchResult(
                source_name=self.source_name,
                fetched_at=datetime.now(timezone.utc),
                success=True,
                raw_payload=combined,
                duration_ms=int((time.perf_counter() - started) * 1000),
            )
        except Exception as exc:
            return FetchResult(
                source_name=self.source_name,
                fetched_at=datetime.now(timezone.utc),
                success=False,
                error=str(exc),
                duration_ms=int((time.perf_counter() - started) * 1000),
            )

    def parse(self, raw) -> list[SourceRecord]:
        rows = (raw or {}).get("response", {}).get("data", [])
        records = []
        for row in rows:
            period = row.get("period")
            value = row.get("value")
            grade = row.get("_grade_name") or row.get("series")
            if value is None or period is None:
                continue
            record_id = f"{grade}:{period}:{value}"
            records.append(SourceRecord(source_record_id=record_id, payload=row))
        return records

    def normalize_prices(self, records: list[SourceRecord]) -> list[NormalizedPrice]:
        prices = []
        for record in records:
            row = record.payload
            grade = row.get("_grade_name") or "Unknown"
            period = row.get("period")
            value = float(row["value"])
            ts = parse_datetime(f"{period}T00:00:00Z" if period and "T" not in period else period)
            prices.append(
                NormalizedPrice(
                    grade_name=grade,
                    price_usd_per_barrel=value,
                    source=self.source_name,
                    source_record_id=record.source_record_id,
                    source_timestamp=ts,
                    data_semantic="OBSERVED",
                )
            )
        return prices

    def validate_prices(self, prices: list[NormalizedPrice]) -> tuple[list[NormalizedPrice], list[str]]:
        accepted, rejected = [], []
        for price in prices:
            if price.price_usd_per_barrel <= 0 or price.price_usd_per_barrel > 500:
                rejected.append(price.source_record_id)
                continue
            accepted.append(price)
        return accepted, rejected
