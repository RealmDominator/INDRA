"""ACLED adapter — requires ACLED credentials."""
from __future__ import annotations

import logging
import time
from datetime import datetime, timezone

import httpx

from app.config.settings import get_settings
from app.ingestion.base import FetchResult, FreshnessState, IngestionRunResult, IngestionStatus, NormalizedEvent, SourceRecord
from app.ingestion.normalizers import parse_datetime, truncate_text

logger = logging.getLogger("indra.ingestion.acled")

ACLED_API_URL = "https://api.acleddata.com/acled/read"


class AcledAdapter:
    source_name = "ACLED"
    source_type = "event"

    def __init__(self, client: httpx.AsyncClient | None = None):
        self._client = client

    @property
    def is_configured(self) -> bool:
        settings = get_settings()
        return bool(settings.acled_api_key and settings.acled_email)

    async def fetch(self) -> FetchResult:
        settings = get_settings()
        if not self.is_configured:
            return FetchResult(
                source_name=self.source_name,
                fetched_at=datetime.now(timezone.utc),
                success=False,
                error="ACLED credentials not configured (ACLED_API_KEY + ACLED_EMAIL required)",
            )
        started = time.perf_counter()
        params = {
            "key": settings.acled_api_key,
            "email": settings.acled_email,
            "country": "Middle East|Yemen|Iran|Iraq|Saudi Arabia|Syria|Ukraine|Russia",
            "event_type": "Battles|Explosions/Remote violence|Violence against civilians|Strategic developments",
            "limit": str(settings.acled_max_records),
        }
        try:
            client = self._client
            if client is None:
                async with httpx.AsyncClient(timeout=settings.ingestion_timeout_seconds) as temp:
                    response = await temp.get(ACLED_API_URL, params=params)
            else:
                response = await client.get(ACLED_API_URL, params=params, timeout=settings.ingestion_timeout_seconds)
            duration_ms = int((time.perf_counter() - started) * 1000)
            if response.status_code != 200:
                return FetchResult(
                    source_name=self.source_name,
                    fetched_at=datetime.now(timezone.utc),
                    success=False,
                    error=f"HTTP {response.status_code}: {response.text[:200]}",
                    http_status=response.status_code,
                    duration_ms=duration_ms,
                )
            return FetchResult(
                source_name=self.source_name,
                fetched_at=datetime.now(timezone.utc),
                success=True,
                raw_payload=response.json(),
                http_status=response.status_code,
                duration_ms=duration_ms,
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
        rows = (raw or {}).get("data") or []
        return [SourceRecord(source_record_id=str(row.get("event_id_cnty") or row.get("data_id")), payload=row) for row in rows if row.get("event_id_cnty") or row.get("data_id")]

    def normalize_events(self, records: list[SourceRecord]) -> list[NormalizedEvent]:
        events = []
        for record in records:
            row = record.payload
            title = f"{row.get('event_type', 'Conflict')}: {row.get('location', 'Unknown')} ({row.get('country', '')})"
            notes = row.get("notes") or row.get("tags")
            occurred = parse_datetime(row.get("event_date"))
            events.append(
                NormalizedEvent(
                    source_name=self.source_name,
                    source_record_id=record.source_record_id,
                    title=title.strip(),
                    description=notes,
                    source_url=row.get("source"),
                    raw_text=truncate_text(notes or title),
                    occurred_at=occurred,
                    source_published_at=occurred,
                    event_type="MILITARY" if "battle" in title.lower() or "violence" in title.lower() else "OTHER",
                    data_semantic="OBSERVED",
                )
            )
        return events

    def validate_events(self, events: list[NormalizedEvent]) -> tuple[list[NormalizedEvent], list[str]]:
        accepted, rejected = [], []
        for event in events:
            if not event.title:
                rejected.append(event.source_record_id)
                continue
            accepted.append(event)
        return accepted, rejected

    def deferred_result(self) -> IngestionRunResult:
        return IngestionRunResult(
            source_name=self.source_name,
            source_type=self.source_type,
            status=IngestionStatus.SKIPPED,
            fetched_at=None,
            source_timestamp=None,
            error="ACLED credentials not configured",
            freshness=FreshnessState.REQUIRES_ACCESS,
            details={"reason": "Set ACLED_API_KEY and ACLED_EMAIL to enable"},
        )
