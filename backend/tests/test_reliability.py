"""Step-9B reliability, bounded-failure, repeatability, and concurrency tests."""
from __future__ import annotations

import asyncio
import time
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete

from app.api import health as health_api
from app.database import AsyncSessionLocal, engine
from app.ingestion.acled import AcledAdapter
from app.ingestion.eia import EiaAdapter
from app.ingestion.freshness import evaluate_freshness
from app.ingestion.runner import run_acled, run_eia
from app.intelligence import CallableLLMProvider, optimize_procurement
from app.main import app
from app.models import EvidenceRecord, GeopoliticalEvent
from app.services.pipeline import ingest_and_process, process_event_by_id


@pytest_asyncio.fixture(autouse=True)
async def dispose_database_engine():
    yield
    await engine.dispose()


def _source() -> str:
    return f"step9b-{uuid4().hex}"


async def _provider_payload(_: str) -> dict:
    return {
        "title": "Hormuz shipping disruption",
        "event_type": "ATTACK",
        "severity": 8,
        "country_names": ["India"],
        "corridor_names": ["Strait of Hormuz"],
        "route_names": [],
        "disruption_description": "A crude shipping disruption is reported.",
        "confidence": 0.9,
    }


async def _cleanup(source: str) -> None:
    async with AsyncSessionLocal() as session:
        await session.execute(delete(EvidenceRecord).where(EvidenceRecord.source_name == source))
        await session.execute(delete(GeopoliticalEvent).where(GeopoliticalEvent.source_name == source))
        await session.commit()


@pytest.mark.asyncio
async def test_read_api_handles_modest_concurrency_without_failures():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        responses = await asyncio.gather(*(
            client.get("/corridors/risk") for _ in range(10)
        ))
    assert all(response.status_code == 200 for response in responses)


@pytest.mark.asyncio
async def test_database_unavailable_is_reported_without_traceback(monkeypatch):
    async def unavailable():
        return False

    monkeypatch.setattr(health_api, "check_db_connection", unavailable)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["database"] == "unavailable"
    assert "Traceback" not in response.text


@pytest.mark.asyncio
async def test_callable_provider_timeout_is_bounded_and_retried():
    attempts = 0

    async def slow(_: str):
        nonlocal attempts
        attempts += 1
        await asyncio.sleep(0.05)
        return {}

    provider = CallableLLMProvider(slow, provider="test", model="test", timeout_seconds=0.01, retries=2)
    started = time.perf_counter()
    with pytest.raises(ValueError, match="failed after 3 attempts"):
        await provider.extract_event("event text")
    elapsed = time.perf_counter() - started
    assert attempts == 3
    assert elapsed < 0.5


@pytest.mark.asyncio
async def test_optional_ingestion_sources_degrade_without_credentials():
    async with AsyncSessionLocal() as session:
        eia = await run_eia(session, EiaAdapter())
        acled = await run_acled(session, AcledAdapter())
    assert eia.status.value == "SKIPPED"
    assert eia.freshness.value == "NOT_CONFIGURED"
    assert acled.status.value == "SKIPPED"
    assert acled.freshness.value == "REQUIRES_ACCESS"


def test_stale_source_is_explicitly_classified():
    old = datetime.now(timezone.utc) - timedelta(days=10)
    state = evaluate_freshness("EIA", configured=True, last_success=old)
    assert state.value == "STALE"


def test_infeasible_optimizer_is_explicit_and_deterministic():
    candidates = [{
        "id": 1,
        "supplier_id": 1,
        "crude_grade_id": 1,
        "route_id": 1,
        "available_volume": 1,
        "unit_cost": 70,
        "risk_score": 0.2,
        "compatibility_score": 0.9,
        "is_operational": True,
    }]
    first = optimize_procurement(candidates, target_volume=2)
    second = optimize_procurement(candidates, target_volume=2)
    assert first == second
    assert first["feasible"] is False
    assert first["solver_status"] in {"INFEASIBLE", "FALLBACK"}
    assert first["unmet_volume"] > 0


@pytest.mark.asyncio
async def test_repeated_full_pipeline_is_stable_and_does_not_duplicate_event():
    source = _source()
    provider = CallableLLMProvider(_provider_payload, provider="test", model="test")
    try:
        async with AsyncSessionLocal() as session:
            first = await ingest_and_process(session, "A detailed Hormuz disruption article for reliability testing.", source, provider)
            second = await process_event_by_id(session, first.event_id, provider)
            assert first.event_id == second.event_id
            # Event recency is intentionally time-dependent; the deterministic
            # engine must remain numerically stable within that documented field.
            assert first.risk["score"] == pytest.approx(second.risk["score"], abs=1e-6)
            assert first.risk["risk_level"] == second.risk["risk_level"]
            assert first.risk["calculation_method"] == second.risk["calculation_method"]
            assert first.scenario == second.scenario
            assert first.procurement == second.procurement
            assert [item["stage"] for item in first.evidence] == [item["stage"] for item in second.evidence]

            rows = (await session.execute(
                GeopoliticalEvent.__table__.select().where(GeopoliticalEvent.source_name == source)
            )).all()
            assert len(rows) == 1
    finally:
        await _cleanup(source)
