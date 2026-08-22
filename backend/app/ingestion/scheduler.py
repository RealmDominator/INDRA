"""Lightweight ingestion scheduler (APScheduler)."""
from __future__ import annotations

import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.config.settings import get_settings
from app.database import AsyncSessionLocal
from app.ingestion.runner import run_acled, run_eia, run_gdelt, run_ofac, run_rbi, run_rss

logger = logging.getLogger("indra.ingestion.scheduler")
_scheduler: AsyncIOScheduler | None = None


async def _job_wrapper(runner):
    async with AsyncSessionLocal() as session:
        try:
            await runner(session)
        except Exception:
            logger.exception("scheduled_ingestion_failed runner=%s", runner.__name__)


def start_scheduler() -> AsyncIOScheduler | None:
    global _scheduler
    settings = get_settings()
    if not settings.ingestion_enabled:
        logger.info("Ingestion scheduler disabled (INGESTION_ENABLED=false)")
        return None
    if _scheduler is not None:
        return _scheduler

    _scheduler = AsyncIOScheduler()
    _scheduler.add_job(_job_wrapper, "interval", minutes=settings.ingestion_gdelt_interval_minutes, args=[run_gdelt], id="ingest_gdelt", replace_existing=True)
    _scheduler.add_job(_job_wrapper, "interval", minutes=settings.ingestion_rss_interval_minutes, args=[run_rss], id="ingest_rss", replace_existing=True)
    _scheduler.add_job(_job_wrapper, "interval", hours=settings.ingestion_acled_interval_hours, args=[run_acled], id="ingest_acled", replace_existing=True)
    _scheduler.add_job(_job_wrapper, "interval", hours=settings.ingestion_eia_interval_hours, args=[run_eia], id="ingest_eia", replace_existing=True)
    _scheduler.add_job(_job_wrapper, "interval", hours=settings.ingestion_rbi_interval_hours, args=[run_rbi], id="ingest_rbi", replace_existing=True)
    _scheduler.add_job(_job_wrapper, "interval", hours=settings.ingestion_ofac_interval_hours, args=[run_ofac], id="ingest_ofac", replace_existing=True)
    _scheduler.start()
    logger.info("Ingestion scheduler started")
    return _scheduler


def stop_scheduler() -> None:
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None
        logger.info("Ingestion scheduler stopped")
