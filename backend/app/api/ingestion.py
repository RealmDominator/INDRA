"""Minimal ingestion status API."""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select

from app.database import get_db
from app.ingestion.freshness import evaluate_freshness
from app.ingestion.runner import get_last_results
from app.models.domain import DataSource

router = APIRouter(prefix="/ingestion", tags=["ingestion"])


class SourceFreshness(BaseModel):
    name: str
    status: str | None
    last_fetched_at: datetime | None
    freshness: str
    last_run_status: str | None = None
    last_error: str | None = None
    record_count: int | None = None


class IngestionStatusResponse(BaseModel):
    timestamp: str
    scheduler_enabled: bool
    sources: list[SourceFreshness]
    data_semantic: str = "OBSERVED"


@router.get("/status", response_model=IngestionStatusResponse)
async def ingestion_status(session=Depends(get_db)):
    from app.config.settings import get_settings

    settings = get_settings()
    last_results = get_last_results()
    rows = (await session.execute(select(DataSource).order_by(DataSource.id))).scalars().all()
    sources = []
    for row in rows:
        run = last_results.get(row.name)
        freshness = evaluate_freshness(
            row.name,
            configured=row.name not in {"EIA", "ACLED"} or (
                (row.name == "EIA" and bool(settings.eia_api_key))
                or (row.name == "ACLED" and bool(settings.acled_api_key and settings.acled_email))
            ),
            deferred=row.name == "ACLED" and not (settings.acled_api_key and settings.acled_email),
            last_success=row.last_fetched_at,
            last_error=run.error if run else None,
        )
        # Persisted source failures must remain visible across process restarts;
        # do not infer FRESH solely from the failed attempt timestamp.
        if row.status in {"ERROR", "FAILED"}:
            freshness = "FAILED"
        if run and run.freshness:
            freshness = run.freshness
        sources.append(
            SourceFreshness(
                name=row.name,
                status=row.status,
                last_fetched_at=row.last_fetched_at,
                freshness=str(freshness),
                last_run_status=run.status.value if run else None,
                last_error=run.error if run else None,
                record_count=run.records_accepted if run else None,
            )
        )
    return IngestionStatusResponse(
        timestamp=datetime.now(timezone.utc).isoformat(),
        scheduler_enabled=settings.ingestion_enabled,
        sources=sources,
    )


@router.post("/run")
async def run_ingestion(session=Depends(get_db)):
    """
    Trigger a manual ingestion run for all sources.
    Returns ingestion results with counts of new events.
    """
    from app.ingestion.runner import run_all
    try:
        results = await run_all(session)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Ingestion run failed: {exc}")

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "sources": [
            {
                "name": r.source_name,
                "status": r.status.value,
                "records_fetched": r.records_fetched,
                "records_accepted": r.records_accepted,
                "records_rejected": r.records_rejected,
                "records_duplicate": r.records_duplicate,
                "freshness": str(r.freshness),
                "error": r.error,
            }
            for r in results
        ],
    }

