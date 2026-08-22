"""GDELT DOC API adapter — energy/geopolitics keyword filter."""
from __future__ import annotations

import logging
import time
from datetime import datetime, timezone

import httpx

from app.config.settings import get_settings
from app.ingestion.base import FetchResult, NormalizedEvent, SourceRecord
from app.ingestion.normalizers import parse_datetime, truncate_text

logger = logging.getLogger("indra.ingestion.gdelt")

GDELT_DOC_URL = "https://api.gdeltproject.org/api/v2/doc/doc"
DEFAULT_QUERY = (
    '(oil OR crude OR petroleum OR "natural gas" OR tanker OR sanction OR hormuz OR "red sea" '
    'OR suez OR russia OR india OR opec) '
    'AND (middleeast OR iran OR iraq OR saudi OR yemen OR ukraine OR shipping OR disruption)'
)


class GdeltAdapter:
    source_name = "GDELT"
    source_type = "event"

    def __init__(self, client: httpx.AsyncClient | None = None):
        self._client = client

    async def fetch(self) -> FetchResult:
        settings = get_settings()
        started = time.perf_counter()
        params = {
            "query": settings.gdelt_query or DEFAULT_QUERY,
            "mode": "ArtList",
            "format": "json",
            "maxrecords": str(settings.gdelt_max_records),
            "sort": "DateDesc",
        }
        try:
            if self._client is not None:
                response = await self._client.get(GDELT_DOC_URL, params=params, timeout=settings.ingestion_timeout_seconds)
            else:
                async with httpx.AsyncClient(timeout=settings.ingestion_timeout_seconds) as client:
                    response = await client.get(GDELT_DOC_URL, params=params)
            duration_ms = int((time.perf_counter() - started) * 1000)
            if response.status_code != 200:
                return FetchResult(
                    source_name=self.source_name,
                    fetched_at=datetime.now(timezone.utc),
                    success=False,
                    error=f"HTTP {response.status_code}",
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
        articles = (raw or {}).get("articles") or []
        records = []
        for article in articles:
            record_id = str(article.get("url") or article.get("seendate") or article.get("title") or "")
            if not record_id:
                continue
            records.append(SourceRecord(source_record_id=record_id, payload=article))
        return records

    def normalize_events(self, records: list[SourceRecord]) -> list[NormalizedEvent]:
        events = []
        for record in records:
            payload = record.payload
            title = (payload.get("title") or "Untitled GDELT article").strip()
            url = payload.get("url")
            published = parse_datetime(payload.get("seendate"))
            summary = payload.get("snippet") or payload.get("summary")
            events.append(
                NormalizedEvent(
                    source_name=self.source_name,
                    source_record_id=record.source_record_id,
                    title=title,
                    description=summary,
                    source_url=url,
                    raw_text=truncate_text(summary or title),
                    occurred_at=published,
                    source_published_at=published,
                    event_type="OTHER",
                    data_semantic="OBSERVED",
                )
            )
        return events

    def validate_events(self, events: list[NormalizedEvent]) -> tuple[list[NormalizedEvent], list[str]]:
        accepted, rejected = [], []
        for event in events:
            if not event.title or len(event.title) < 5:
                rejected.append(f"missing title: {event.source_record_id}")
                continue
            accepted.append(event)
        return accepted, rejected
