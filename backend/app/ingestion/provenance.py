"""Provenance and evidence helpers for ingestion."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ingestion import EvidenceRecord


def _naive_utc(dt: datetime | None = None) -> datetime:
    dt = dt or datetime.now(timezone.utc)
    if dt.tzinfo is not None:
        return dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt


async def create_source_evidence(
    session: AsyncSession,
    *,
    source_name: str,
    source_url: str | None,
    related_entity_type: str,
    related_entity_id: int,
    input_summary: dict[str, Any],
    output_summary: dict[str, Any] | None = None,
    data_semantic: str = "OBSERVED",
) -> EvidenceRecord:
    record = EvidenceRecord(
        evidence_type="SOURCE",
        source_name=source_name,
        source_url=source_url,
        timestamp=_naive_utc(),
        related_entity_type=related_entity_type,
        related_entity_id=related_entity_id,
        model_or_method=f"ingestion:{source_name.lower()}",
        input_summary=input_summary,
        output_summary=output_summary or {},
        data_semantic=data_semantic,
    )
    session.add(record)
    await session.flush()
    return record
