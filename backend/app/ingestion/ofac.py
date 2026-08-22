"""OFAC SDN refresh adapter."""
from __future__ import annotations

import csv
import hashlib
import io
import logging
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx

from app.config.settings import get_settings
from app.ingestion.base import FetchResult, NormalizedSanctionEntity, SourceRecord

logger = logging.getLogger("indra.ingestion.ofac")

OFAC_CSV_URL = "https://www.treasury.gov/ofac/downloads/sdn.csv"
PROJECT_ROOT = Path(__file__).resolve().parents[3]
ENERGY_KEYWORDS = (
    "oil", "petroleum", "energy", "gas", "crude", "refinery", "petrochemical",
    "national iranian oil", "rosneft", "lukoil", "gazprom", "pdvsa", "sonangol",
)


class OfacAdapter:
    source_name = "OFAC"
    source_type = "sanctions"

    def __init__(self, client: httpx.AsyncClient | None = None):
        self._client = client
        self.raw_dir = PROJECT_ROOT / "data" / "raw" / "ofac"
        self.processed_dir = PROJECT_ROOT / "data" / "processed" / "ofac"

    async def fetch(self) -> FetchResult:
        settings = get_settings()
        started = time.perf_counter()
        try:
            if self._client is not None:
                response = await self._client.get(OFAC_CSV_URL, timeout=settings.ingestion_timeout_seconds)
            else:
                async with httpx.AsyncClient(timeout=settings.ingestion_timeout_seconds, follow_redirects=True) as client:
                    response = await client.get(OFAC_CSV_URL)
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
            content = response.text
            self.raw_dir.mkdir(parents=True, exist_ok=True)
            raw_path = self.raw_dir / "sdn.csv"
            raw_path.write_text(content, encoding="utf-8")
            return FetchResult(
                source_name=self.source_name,
                fetched_at=datetime.now(timezone.utc),
                success=True,
                raw_payload={"content": content, "sha256": hashlib.sha256(content.encode()).hexdigest()},
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
        content = (raw or {}).get("content") or ""
        reader = csv.reader(io.StringIO(content))
        records = []
        for idx, row in enumerate(reader):
            if len(row) < 2:
                continue
            entity_id = row[0].strip()
            name = row[1].strip() if len(row) > 1 else ""
            program = row[2].strip() if len(row) > 2 else ""
            if not entity_id or not name:
                continue
            haystack = " ".join(row).lower()
            if not any(keyword in haystack for keyword in ENERGY_KEYWORDS):
                continue
            records.append(SourceRecord(source_record_id=entity_id, payload={"entity_id": entity_id, "name": name, "program": program, "row": row}))
        return records

    def normalize_sanctions(self, records: list[SourceRecord]) -> list[NormalizedSanctionEntity]:
        entities = []
        for record in records:
            payload = record.payload
            entities.append(
                NormalizedSanctionEntity(
                    entity_name=payload["name"],
                    source_record_id=record.source_record_id,
                    program=payload.get("program"),
                    updated_at=datetime.now(timezone.utc),
                    data_semantic="OBSERVED",
                )
            )
        return entities

    def write_processed(self, entities: list[NormalizedSanctionEntity]) -> Path:
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        out_path = self.processed_dir / "sanctions_entities.csv"
        with open(out_path, "w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["entity_id", "entity_name", "program", "data_semantic"])
            for entity in entities:
                writer.writerow([entity.source_record_id, entity.entity_name, entity.program or "", entity.data_semantic])
        return out_path
