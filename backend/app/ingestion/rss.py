"""Approved RSS/public feed adapter."""
from __future__ import annotations

import logging
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

import httpx

from app.config.settings import get_settings
from app.ingestion.base import FetchResult, NormalizedEvent, SourceRecord
from app.ingestion.normalizers import parse_datetime, truncate_text

logger = logging.getLogger("indra.ingestion.rss")

ENERGY_KEYWORDS = (
    "oil", "crude", "petroleum", "hormuz", "red sea", "suez", "sanction",
    "tanker", "opec", "refinery", "lng", "energy", "shipping", "russia", "india",
)


class RssAdapter:
    source_name = "RSS"
    source_type = "event"

    def __init__(self, client: httpx.AsyncClient | None = None):
        self._client = client

    async def fetch(self) -> FetchResult:
        settings = get_settings()
        feeds = settings.rss_feed_urls
        if not feeds:
            return FetchResult(
                source_name=self.source_name,
                fetched_at=datetime.now(timezone.utc),
                success=False,
                error="No RSS feed URLs configured",
            )
        started = time.perf_counter()
        combined = []
        errors = []
        for feed_url in feeds:
            try:
                if self._client is not None:
                    response = await self._client.get(feed_url, timeout=settings.ingestion_timeout_seconds)
                else:
                    async with httpx.AsyncClient(timeout=settings.ingestion_timeout_seconds, follow_redirects=True) as client:
                        response = await client.get(feed_url)
                if response.status_code != 200:
                    errors.append(f"{feed_url}: HTTP {response.status_code}")
                    continue
                combined.append({"feed_url": feed_url, "content": response.text})
            except Exception as exc:
                errors.append(f"{feed_url}: {exc}")
        if not combined:
            return FetchResult(
                source_name=self.source_name,
                fetched_at=datetime.now(timezone.utc),
                success=False,
                error="; ".join(errors) or "No RSS feeds fetched",
                duration_ms=int((time.perf_counter() - started) * 1000),
            )
        return FetchResult(
            source_name=self.source_name,
            fetched_at=datetime.now(timezone.utc),
            success=True,
            raw_payload={"feeds": combined, "errors": errors},
            duration_ms=int((time.perf_counter() - started) * 1000),
        )

    def parse(self, raw) -> list[SourceRecord]:
        records = []
        for feed in (raw or {}).get("feeds") or []:
            feed_url = feed.get("feed_url", "")
            try:
                root = ET.fromstring(feed.get("content") or "")
            except ET.ParseError:
                continue
            for item in root.findall(".//item"):
                title = (item.findtext("title") or "").strip()
                link = (item.findtext("link") or "").strip()
                pub = item.findtext("pubDate")
                desc = item.findtext("description") or item.findtext("summary")
                haystack = f"{title} {desc}".lower()
                if not any(k in haystack for k in ENERGY_KEYWORDS):
                    continue
                record_id = link or f"{feed_url}:{title}:{pub}"
                records.append(SourceRecord(source_record_id=record_id, payload={"title": title, "link": link, "pubDate": pub, "description": desc, "feed_url": feed_url}))
        return records

    def normalize_events(self, records: list[SourceRecord]) -> list[NormalizedEvent]:
        events = []
        for record in records:
            payload = record.payload
            published = parse_datetime(payload.get("pubDate"))
            events.append(
                NormalizedEvent(
                    source_name=self.source_name,
                    source_record_id=record.source_record_id,
                    title=payload.get("title") or "RSS item",
                    description=payload.get("description"),
                    source_url=payload.get("link"),
                    raw_text=truncate_text(payload.get("description") or payload.get("title")),
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
                rejected.append(event.source_record_id)
                continue
            accepted.append(event)
        return accepted, rejected
