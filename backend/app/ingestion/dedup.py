"""Deduplication helpers for ingested records."""
from __future__ import annotations

import hashlib
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ingestion.base import NormalizedEvent, NormalizedFxRate, NormalizedPrice
from app.models.ingestion import CommodityPrice, FxRate, GeopoliticalEvent


def _naive_utc(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    if dt.tzinfo is not None:
        return dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt


def stable_hash(*parts: str) -> str:
    joined = "|".join(p.strip().lower() for p in parts if p)
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()


def event_dedup_key(event: NormalizedEvent) -> str:
    if event.source_record_id:
        return stable_hash(event.source_name, event.source_record_id)
    if event.source_url:
        return stable_hash(event.source_name, event.source_url)
    occurred = event.occurred_at.isoformat() if event.occurred_at else ""
    return stable_hash(event.source_name, event.title, occurred)


def price_dedup_key(price: NormalizedPrice) -> str:
    ts = price.source_timestamp.isoformat() if price.source_timestamp else ""
    return stable_hash(price.source, price.grade_name, ts, str(price.price_usd_per_barrel))


def fx_dedup_key(rate: NormalizedFxRate) -> str:
    ts = rate.source_timestamp.isoformat() if rate.source_timestamp else ""
    return stable_hash(rate.source, rate.currency_pair, ts, str(rate.rate))


async def event_exists(session: AsyncSession, event: NormalizedEvent) -> bool:
    occurred = _naive_utc(event.occurred_at)
    if event.source_url:
        existing = await session.scalar(
            select(GeopoliticalEvent.id).where(
                GeopoliticalEvent.source_name == event.source_name,
                GeopoliticalEvent.source_url == event.source_url,
            ).limit(1)
        )
        if existing:
            return True
    if event.source_record_id:
        marker = f"[source_id:{event.source_record_id}]"
        existing = await session.scalar(
            select(GeopoliticalEvent.id).where(
                GeopoliticalEvent.source_name == event.source_name,
                GeopoliticalEvent.description.like(f"{marker}%"),
            ).limit(1)
        )
        if existing:
            return True
    if occurred:
        existing = await session.scalar(
            select(GeopoliticalEvent.id).where(
                GeopoliticalEvent.source_name == event.source_name,
                GeopoliticalEvent.title == event.title,
                GeopoliticalEvent.occurred_at == occurred,
            ).limit(1)
        )
        if existing:
            return True
    return False


async def price_exists(session: AsyncSession, price: NormalizedPrice) -> bool:
    query = select(CommodityPrice.id).where(
        CommodityPrice.source == price.source,
        CommodityPrice.grade_name == price.grade_name,
    )
    if price.source_timestamp:
        query = query.where(CommodityPrice.source_timestamp == _naive_utc(price.source_timestamp))
    else:
        query = query.where(CommodityPrice.price_usd_per_barrel == price.price_usd_per_barrel)
    return (await session.scalar(query.limit(1))) is not None


async def fx_exists(session: AsyncSession, rate: NormalizedFxRate) -> bool:
    query = select(FxRate.id).where(
        FxRate.source == rate.source,
        FxRate.currency_pair == rate.currency_pair,
    )
    if rate.source_timestamp:
        query = query.where(FxRate.source_timestamp == _naive_utc(rate.source_timestamp))
    return (await session.scalar(query.limit(1))) is not None


def prefix_description(event: NormalizedEvent) -> str | None:
    """Embed stable source ID in description when schema has no dedicated column."""
    if not event.source_record_id:
        return event.description
    marker = f"[source_id:{event.source_record_id}]"
    if event.description:
        return f"{marker} {event.description}"
    return marker
