"""
INDRA — Health endpoint

GET /health

Returns basic application health status and database connectivity.
This is the application health endpoint. Domain, intelligence, and ingestion
status endpoints are exposed by their respective routers.
"""
import time
from datetime import datetime, timezone

from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy import select

from app.database import check_db_connection
from app.database import AsyncSessionLocal
from app.ingestion.freshness import evaluate_freshness
from app.ingestion.runner import get_last_results
from app.models.domain import DataSource

router = APIRouter(tags=["health"])

_start_time = time.time()


class HealthResponse(BaseModel):
    status: str
    environment: str
    version: str
    uptime_seconds: float
    timestamp: str
    database: str
    message: str
    components: dict[str, str]
    source_summary: dict[str, int]


def _configured_source(name: str, settings) -> bool:
    if name == "EIA":
        return bool(settings.eia_api_key)
    if name == "ACLED":
        return bool(settings.acled_api_key and settings.acled_email)
    if name == "RSS":
        return bool(settings.rss_feed_url_list)
    return True


async def _source_summary(settings) -> dict[str, int]:
    """Return aggregate source states without exposing URLs or credentials."""
    counts = {"HEALTHY": 0, "DEGRADED": 0, "UNAVAILABLE": 0, "NOT_CONFIGURED": 0}
    try:
        async with AsyncSessionLocal() as session:
            rows = (await session.execute(select(DataSource).order_by(DataSource.id))).scalars().all()
        results = get_last_results()
        for row in rows:
            run = results.get(row.name)
            if row.status in {"ERROR", "FAILED"} or (run and run.status.value == "FAILED"):
                state = "DEGRADED"
            else:
                freshness = evaluate_freshness(
                    row.name,
                    configured=_configured_source(row.name, settings),
                    deferred=row.name == "ACLED" and not _configured_source(row.name, settings),
                    last_success=row.last_fetched_at,
                    last_error=run.error if run else None,
                )
                if run and run.freshness:
                    freshness = run.freshness
                state = {
                    "FRESH": "HEALTHY",
                    "PARTIAL": "DEGRADED",
                    "STALE": "DEGRADED",
                    "FAILED": "DEGRADED",
                    "NOT_CONFIGURED": "NOT_CONFIGURED",
                    "DEFERRED": "NOT_CONFIGURED",
                    "REQUIRES_ACCESS": "NOT_CONFIGURED",
                }.get(str(freshness), "UNAVAILABLE")
            counts[state] += 1
    except Exception:
        counts["UNAVAILABLE"] += 1
    return counts


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Application health check",
    description=(
        "Returns application health status and database connectivity."
    ),
)
async def health_check() -> HealthResponse:
    """
    Lightweight health check.
    - status: 'ok' if service is running
    - database: 'connected' | 'unavailable'
    """
    from app.config.settings import get_settings
    settings = get_settings()

    db_ok = await check_db_connection()
    source_summary = await _source_summary(settings) if db_ok else {
        "HEALTHY": 0, "DEGRADED": 0, "UNAVAILABLE": 1, "NOT_CONFIGURED": 0,
    }
    llm_status = "HEALTHY" if settings.openrouter_api_key else "NOT_CONFIGURED"
    if source_summary["UNAVAILABLE"]:
        sources_status = "UNAVAILABLE"
    elif source_summary["DEGRADED"]:
        sources_status = "DEGRADED"
    elif source_summary["NOT_CONFIGURED"]:
        sources_status = "DEGRADED" if source_summary["HEALTHY"] else "NOT_CONFIGURED"
    else:
        sources_status = "HEALTHY"
    components = {
        "application": "HEALTHY",
        "database": "HEALTHY" if db_ok else "UNAVAILABLE",
        "ingestion": "HEALTHY" if db_ok else "UNAVAILABLE",
        "llm_provider": llm_status,
        "external_sources": sources_status,
    }

    return HealthResponse(
        status="ok",
        environment=settings.app_env,
        version="0.4.0-step8c",
        uptime_seconds=round(time.time() - _start_time, 2),
        timestamp=datetime.now(timezone.utc).isoformat(),
        database="connected" if db_ok else "unavailable",
        message=(
            "INDRA backend is running. Database connected."
            if db_ok
            else "INDRA backend is running. Database unavailable — start Docker PostgreSQL."
        ),
        components=components,
        source_summary=source_summary,
    )
