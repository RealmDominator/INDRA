"""Freshness evaluation for external data sources."""
from __future__ import annotations

from datetime import datetime, timezone

from app.config.settings import get_settings
from app.ingestion.base import FreshnessState


def _age_minutes(since: datetime | None, now: datetime | None = None) -> float | None:
    if since is None:
        return None
    now = now or datetime.now(timezone.utc)
    if since.tzinfo is None:
        since = since.replace(tzinfo=timezone.utc)
    return (now - since).total_seconds() / 60.0


def evaluate_freshness(
    source_name: str,
    *,
    configured: bool,
    deferred: bool = False,
    last_success: datetime | None = None,
    last_attempt: datetime | None = None,
    last_error: str | None = None,
) -> FreshnessState:
    settings = get_settings()
    if deferred:
        return FreshnessState.DEFERRED
    if not configured:
        return FreshnessState.NOT_CONFIGURED
    if last_success is None and last_error:
        return FreshnessState.FAILED
    if last_success is None:
        return FreshnessState.NOT_CONFIGURED

    thresholds = {
        "GDELT": settings.ingestion_gdelt_stale_minutes,
        "RSS": settings.ingestion_rss_stale_minutes,
        "ACLED": settings.ingestion_acled_stale_hours * 60,
        "EIA": settings.ingestion_eia_stale_hours * 60,
        "RBI": settings.ingestion_rbi_stale_hours * 60,
        "OFAC": settings.ingestion_ofac_stale_hours * 60,
    }
    stale_after = thresholds.get(source_name.upper(), 24 * 60)
    age = _age_minutes(last_success)
    if age is None:
        return FreshnessState.NOT_CONFIGURED
    if age <= stale_after:
        return FreshnessState.FRESH
    if last_error and last_attempt and (_age_minutes(last_attempt) or 0) < stale_after:
        return FreshnessState.PARTIAL
    return FreshnessState.STALE
