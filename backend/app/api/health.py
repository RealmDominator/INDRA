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

from app.database import check_db_connection

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
    )
