"""Persist normalized ingestion records and update data source registry."""
from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ingestion.base import NormalizedEvent, NormalizedFxRate, NormalizedPrice
from app.ingestion.dedup import event_exists, fx_exists, prefix_description, price_exists
from app.ingestion.provenance import create_source_evidence
from app.models.domain import DataSource
from app.models.ingestion import CommodityPrice, FxRate, GeopoliticalEvent


def _naive_utc(dt: datetime | None) -> datetime | None:
    """PostgreSQL TIMESTAMP columns are naive; store UTC without tzinfo."""
    if dt is None:
        return None
    if dt.tzinfo is not None:
        return dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt


async def persist_event(session: AsyncSession, event: NormalizedEvent) -> tuple[str, int | None]:
    if await event_exists(session, event):
        return "duplicate", None
    row = GeopoliticalEvent(
        event_type=event.event_type,
        title=event.title,
        description=prefix_description(event),
        source_url=event.source_url,
        source_name=event.source_name,
        severity=Decimal(str(event.severity)) if event.severity is not None else None,
        confidence=Decimal(str(event.confidence)) if event.confidence is not None else None,
        occurred_at=_naive_utc(event.occurred_at),
        detected_at=_naive_utc(datetime.now(timezone.utc)),
        raw_text=event.raw_text,
        is_simulated=event.is_simulated,
    )
    session.add(row)
    await session.flush()
    await create_source_evidence(
        session,
        source_name=event.source_name,
        source_url=event.source_url,
        related_entity_type="event",
        related_entity_id=row.id,
        input_summary={
            "source_record_id": event.source_record_id,
            "source_published_at": event.source_published_at.isoformat() if event.source_published_at else None,
            "data_semantic": event.data_semantic,
        },
        output_summary={"event_id": row.id, "title": event.title},
        data_semantic=event.data_semantic,
    )
    return "accepted", row.id


async def persist_price(session: AsyncSession, price: NormalizedPrice) -> tuple[str, int | None]:
    if await price_exists(session, price):
        return "duplicate", None
    row = CommodityPrice(
        grade_name=price.grade_name,
        crude_grade_id=price.crude_grade_id,
        price_usd_per_barrel=Decimal(str(price.price_usd_per_barrel)),
        source=price.source,
        source_timestamp=_naive_utc(price.source_timestamp),
        observed_at=_naive_utc(datetime.now(timezone.utc)),
        data_semantic=price.data_semantic,
    )
    session.add(row)
    await session.flush()
    await create_source_evidence(
        session,
        source_name=price.source,
        source_url=None,
        related_entity_type="commodity_price",
        related_entity_id=row.id,
        input_summary={"source_record_id": price.source_record_id, "grade_name": price.grade_name},
        output_summary={"price_usd_per_barrel": float(price.price_usd_per_barrel)},
        data_semantic=price.data_semantic,
    )
    return "accepted", row.id


async def persist_fx_rate(session: AsyncSession, rate: NormalizedFxRate) -> tuple[str, int | None]:
    if await fx_exists(session, rate):
        return "duplicate", None
    row = FxRate(
        currency_pair=rate.currency_pair,
        rate=Decimal(str(rate.rate)),
        source=rate.source,
        source_timestamp=_naive_utc(rate.source_timestamp),
        observed_at=_naive_utc(datetime.now(timezone.utc)),
        data_semantic=rate.data_semantic,
    )
    session.add(row)
    await session.flush()
    await create_source_evidence(
        session,
        source_name=rate.source,
        source_url=None,
        related_entity_type="fx_rate",
        related_entity_id=row.id,
        input_summary={"source_record_id": rate.source_record_id, "currency_pair": rate.currency_pair},
        output_summary={"rate": float(rate.rate)},
        data_semantic=rate.data_semantic,
    )
    return "accepted", row.id


async def update_data_source_status(
    session: AsyncSession,
    source_name: str,
    *,
    status: str,
    last_fetched_at: datetime | None = None,
) -> None:
    row = await session.scalar(select(DataSource).where(DataSource.name == source_name))
    if row is None:
        return
    row.status = status
    if last_fetched_at is not None:
        row.last_fetched_at = _naive_utc(last_fetched_at)
