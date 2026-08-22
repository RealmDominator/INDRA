"""Ingestion orchestration for all source adapters."""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.ingestion.acled import AcledAdapter
from app.ingestion.base import FreshnessState, IngestionRunResult, IngestionStatus
from app.ingestion.eia import EiaAdapter
from app.ingestion.freshness import evaluate_freshness
from app.ingestion.gdelt import GdeltAdapter
from app.ingestion.ofac import OfacAdapter
from app.ingestion.persistence import persist_event, persist_fx_rate, persist_price, update_data_source_status
from app.ingestion.rbi import RbiAdapter
from app.ingestion.rss import RssAdapter

logger = logging.getLogger("indra.ingestion.runner")

_LAST_RESULTS: dict[str, IngestionRunResult] = {}
_LAST_SUCCESS: dict[str, datetime] = {}


def get_last_results() -> dict[str, IngestionRunResult]:
    return dict(_LAST_RESULTS)


async def _run_with_retry(fetch_coro_factory, retries: int, backoff: float):
    last_error = None
    for attempt in range(retries + 1):
        result = await fetch_coro_factory()
        if result.success:
            return result
        last_error = result.error
        if attempt < retries:
            await asyncio.sleep(backoff * (attempt + 1))
    return result


async def run_gdelt(session: AsyncSession, adapter: GdeltAdapter | None = None) -> IngestionRunResult:
    adapter = adapter or GdeltAdapter()
    from app.config.settings import get_settings
    settings = get_settings()
    fetch = await _run_with_retry(adapter.fetch, settings.ingestion_max_retries, settings.ingestion_retry_backoff_seconds)
    if not fetch.success:
        result = IngestionRunResult(
            source_name=adapter.source_name,
            source_type=adapter.source_type,
            status=IngestionStatus.FAILED,
            fetched_at=fetch.fetched_at,
            source_timestamp=None,
            error=fetch.error,
            freshness=FreshnessState.FAILED,
        )
        await update_data_source_status(session, adapter.source_name, status="ERROR", last_fetched_at=fetch.fetched_at)
        _LAST_RESULTS[adapter.source_name] = result
        return result

    records = adapter.parse(fetch.raw_payload)
    events = adapter.normalize_events(records)
    accepted, rejected = adapter.validate_events(events)
    dupes = 0
    inserted = 0
    for event in accepted:
        outcome, _ = await persist_event(session, event)
        if outcome == "duplicate":
            dupes += 1
        elif outcome == "accepted":
            inserted += 1
    await session.commit()
    _LAST_SUCCESS[adapter.source_name] = fetch.fetched_at
    freshness = evaluate_freshness(adapter.source_name, configured=True, last_success=fetch.fetched_at)
    result = IngestionRunResult(
        source_name=adapter.source_name,
        source_type=adapter.source_type,
        status=IngestionStatus.SUCCESS if inserted or dupes else IngestionStatus.PARTIAL,
        fetched_at=fetch.fetched_at,
        source_timestamp=accepted[0].source_published_at if accepted else None,
        records_fetched=len(records),
        records_accepted=inserted,
        records_rejected=len(rejected),
        records_duplicate=dupes,
        freshness=freshness,
        details={"duration_ms": fetch.duration_ms},
    )
    await update_data_source_status(session, adapter.source_name, status="ACTIVE", last_fetched_at=fetch.fetched_at)
    await session.commit()
    _LAST_RESULTS[adapter.source_name] = result
    logger.info("gdelt_ingestion accepted=%d duplicate=%d rejected=%d", inserted, dupes, len(rejected))
    return result


async def run_acled(session: AsyncSession, adapter: AcledAdapter | None = None) -> IngestionRunResult:
    adapter = adapter or AcledAdapter()
    if not adapter.is_configured:
        result = adapter.deferred_result()
        _LAST_RESULTS[adapter.source_name] = result
        await update_data_source_status(session, adapter.source_name, status="UNAVAILABLE")
        await session.commit()
        return result
    from app.config.settings import get_settings
    settings = get_settings()
    fetch = await _run_with_retry(adapter.fetch, settings.ingestion_max_retries, settings.ingestion_retry_backoff_seconds)
    if not fetch.success:
        result = IngestionRunResult(
            source_name=adapter.source_name,
            source_type=adapter.source_type,
            status=IngestionStatus.FAILED,
            fetched_at=fetch.fetched_at,
            source_timestamp=None,
            error=fetch.error,
            freshness=FreshnessState.FAILED,
        )
        _LAST_RESULTS[adapter.source_name] = result
        return result
    records = adapter.parse(fetch.raw_payload)
    events = adapter.normalize_events(records)
    accepted, rejected = adapter.validate_events(events)
    dupes = inserted = 0
    for event in accepted:
        outcome, _ = await persist_event(session, event)
        dupes += outcome == "duplicate"
        inserted += outcome == "accepted"
    await session.commit()
    _LAST_SUCCESS[adapter.source_name] = fetch.fetched_at
    result = IngestionRunResult(
        source_name=adapter.source_name,
        source_type=adapter.source_type,
        status=IngestionStatus.SUCCESS,
        fetched_at=fetch.fetched_at,
        source_timestamp=accepted[0].source_published_at if accepted else None,
        records_fetched=len(records),
        records_accepted=inserted,
        records_rejected=len(rejected),
        records_duplicate=dupes,
        freshness=evaluate_freshness(adapter.source_name, configured=True, last_success=fetch.fetched_at),
    )
    await update_data_source_status(session, adapter.source_name, status="ACTIVE", last_fetched_at=fetch.fetched_at)
    await session.commit()
    _LAST_RESULTS[adapter.source_name] = result
    return result


async def run_eia(session: AsyncSession, adapter: EiaAdapter | None = None) -> IngestionRunResult:
    adapter = adapter or EiaAdapter()
    if not adapter.is_configured:
        result = IngestionRunResult(
            source_name=adapter.source_name,
            source_type=adapter.source_type,
            status=IngestionStatus.SKIPPED,
            fetched_at=None,
            source_timestamp=None,
            error="EIA_API_KEY not configured",
            freshness=FreshnessState.NOT_CONFIGURED,
        )
        _LAST_RESULTS[adapter.source_name] = result
        return result
    from app.config.settings import get_settings
    settings = get_settings()
    fetch = await _run_with_retry(adapter.fetch, settings.ingestion_max_retries, settings.ingestion_retry_backoff_seconds)
    if not fetch.success:
        result = IngestionRunResult(
            source_name=adapter.source_name,
            source_type=adapter.source_type,
            status=IngestionStatus.FAILED,
            fetched_at=fetch.fetched_at,
            source_timestamp=None,
            error=fetch.error,
            freshness=FreshnessState.FAILED,
        )
        _LAST_RESULTS[adapter.source_name] = result
        return result
    records = adapter.parse(fetch.raw_payload)
    prices = adapter.normalize_prices(records)
    accepted, rejected = adapter.validate_prices(prices)
    dupes = inserted = 0
    for price in accepted:
        outcome, _ = await persist_price(session, price)
        dupes += outcome == "duplicate"
        inserted += outcome == "accepted"
    await session.commit()
    _LAST_SUCCESS[adapter.source_name] = fetch.fetched_at
    latest_ts = max((p.source_timestamp for p in accepted if p.source_timestamp), default=None)
    result = IngestionRunResult(
        source_name=adapter.source_name,
        source_type=adapter.source_type,
        status=IngestionStatus.SUCCESS,
        fetched_at=fetch.fetched_at,
        source_timestamp=latest_ts,
        records_fetched=len(records),
        records_accepted=inserted,
        records_rejected=len(rejected),
        records_duplicate=dupes,
        freshness=evaluate_freshness(adapter.source_name, configured=True, last_success=fetch.fetched_at),
    )
    await update_data_source_status(session, adapter.source_name, status="ACTIVE", last_fetched_at=fetch.fetched_at)
    await session.commit()
    _LAST_RESULTS[adapter.source_name] = result
    return result


async def run_rbi(session: AsyncSession, adapter: RbiAdapter | None = None) -> IngestionRunResult:
    adapter = adapter or RbiAdapter()
    from app.config.settings import get_settings
    settings = get_settings()
    fetch = await _run_with_retry(adapter.fetch, settings.ingestion_max_retries, settings.ingestion_retry_backoff_seconds)
    if not fetch.success:
        result = IngestionRunResult(
            source_name=adapter.source_name,
            source_type=adapter.source_type,
            status=IngestionStatus.FAILED,
            fetched_at=fetch.fetched_at,
            source_timestamp=None,
            error=fetch.error,
            freshness=FreshnessState.PARTIAL,
            details={"note": "RBI bulk automation unavailable; requires manual DBIE export"},
        )
        _LAST_RESULTS[adapter.source_name] = result
        return result
    records = adapter.parse(fetch.raw_payload)
    rates = adapter.normalize_fx(records)
    accepted, rejected = adapter.validate_fx(rates)
    dupes = inserted = 0
    for rate in accepted:
        outcome, _ = await persist_fx_rate(session, rate)
        dupes += outcome == "duplicate"
        inserted += outcome == "accepted"
    await session.commit()
    _LAST_SUCCESS[adapter.source_name] = fetch.fetched_at
    latest_ts = max((r.source_timestamp for r in accepted if r.source_timestamp), default=None)
    result = IngestionRunResult(
        source_name=adapter.source_name,
        source_type=adapter.source_type,
        status=IngestionStatus.SUCCESS if inserted else IngestionStatus.PARTIAL,
        fetched_at=fetch.fetched_at,
        source_timestamp=latest_ts,
        records_fetched=len(records),
        records_accepted=inserted,
        records_rejected=len(rejected),
        records_duplicate=dupes,
        freshness=FreshnessState.PARTIAL if inserted else FreshnessState.STALE,
        details={"note": "Loaded from processed RBI CSV; not live bulk API"},
    )
    await update_data_source_status(session, adapter.source_name, status="ACTIVE" if inserted else "STALE", last_fetched_at=fetch.fetched_at)
    await session.commit()
    _LAST_RESULTS[adapter.source_name] = result
    return result


async def run_ofac(session: AsyncSession, adapter: OfacAdapter | None = None) -> IngestionRunResult:
    adapter = adapter or OfacAdapter()
    from app.config.settings import get_settings
    settings = get_settings()
    fetch = await _run_with_retry(adapter.fetch, settings.ingestion_max_retries, settings.ingestion_retry_backoff_seconds)
    if not fetch.success:
        result = IngestionRunResult(
            source_name=adapter.source_name,
            source_type=adapter.source_type,
            status=IngestionStatus.FAILED,
            fetched_at=fetch.fetched_at,
            source_timestamp=None,
            error=fetch.error,
            freshness=FreshnessState.FAILED,
        )
        _LAST_RESULTS[adapter.source_name] = result
        return result
    records = adapter.parse(fetch.raw_payload)
    entities = adapter.normalize_sanctions(records)
    out_path = adapter.write_processed(entities)
    await session.commit()
    _LAST_SUCCESS[adapter.source_name] = fetch.fetched_at
    result = IngestionRunResult(
        source_name=adapter.source_name,
        source_type=adapter.source_type,
        status=IngestionStatus.SUCCESS,
        fetched_at=fetch.fetched_at,
        source_timestamp=fetch.fetched_at,
        records_fetched=len(records),
        records_accepted=len(entities),
        records_rejected=0,
        records_duplicate=0,
        freshness=evaluate_freshness(adapter.source_name, configured=True, last_success=fetch.fetched_at),
        details={"processed_path": str(out_path), "sha256": (fetch.raw_payload or {}).get("sha256")},
    )
    await update_data_source_status(session, adapter.source_name, status="ACTIVE", last_fetched_at=fetch.fetched_at)
    await session.commit()
    _LAST_RESULTS[adapter.source_name] = result
    return result


async def run_rss(session: AsyncSession, adapter: RssAdapter | None = None) -> IngestionRunResult:
    adapter = adapter or RssAdapter()
    from app.config.settings import get_settings
    settings = get_settings()
    if not settings.rss_feed_urls:
        result = IngestionRunResult(
            source_name=adapter.source_name,
            source_type=adapter.source_type,
            status=IngestionStatus.SKIPPED,
            fetched_at=None,
            source_timestamp=None,
            error="No RSS feeds configured",
            freshness=FreshnessState.NOT_CONFIGURED,
        )
        _LAST_RESULTS[adapter.source_name] = result
        return result
    fetch = await _run_with_retry(adapter.fetch, settings.ingestion_max_retries, settings.ingestion_retry_backoff_seconds)
    if not fetch.success:
        result = IngestionRunResult(
            source_name=adapter.source_name,
            source_type=adapter.source_type,
            status=IngestionStatus.FAILED,
            fetched_at=fetch.fetched_at,
            source_timestamp=None,
            error=fetch.error,
            freshness=FreshnessState.FAILED,
        )
        _LAST_RESULTS[adapter.source_name] = result
        return result
    records = adapter.parse(fetch.raw_payload)
    events = adapter.normalize_events(records)
    accepted, rejected = adapter.validate_events(events)
    dupes = inserted = 0
    for event in accepted:
        outcome, _ = await persist_event(session, event)
        dupes += outcome == "duplicate"
        inserted += outcome == "accepted"
    await session.commit()
    _LAST_SUCCESS[adapter.source_name] = fetch.fetched_at
    result = IngestionRunResult(
        source_name=adapter.source_name,
        source_type=adapter.source_type,
        status=IngestionStatus.SUCCESS if inserted or dupes else IngestionStatus.PARTIAL,
        fetched_at=fetch.fetched_at,
        source_timestamp=accepted[0].source_published_at if accepted else None,
        records_fetched=len(records),
        records_accepted=inserted,
        records_rejected=len(rejected),
        records_duplicate=dupes,
        freshness=evaluate_freshness(adapter.source_name, configured=True, last_success=fetch.fetched_at),
    )
    await update_data_source_status(session, adapter.source_name, status="ACTIVE", last_fetched_at=fetch.fetched_at)
    await session.commit()
    _LAST_RESULTS[adapter.source_name] = result
    return result


async def run_all(session: AsyncSession) -> list[IngestionRunResult]:
    results = []
    for runner in (run_gdelt, run_rss, run_acled, run_eia, run_rbi, run_ofac):
        try:
            results.append(await runner(session))
        except Exception as exc:
            logger.exception("ingestion_runner_failed source=%s", runner.__name__)
            results.append(
                IngestionRunResult(
                    source_name=runner.__name__,
                    source_type="unknown",
                    status=IngestionStatus.FAILED,
                    fetched_at=datetime.now(timezone.utc),
                    source_timestamp=None,
                    error=str(exc),
                    freshness=FreshnessState.FAILED,
                )
            )
    return results
