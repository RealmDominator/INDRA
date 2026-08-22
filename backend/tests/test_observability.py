"""Step-12A operational health and safe degradation checks."""

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.api import health as health_api
from app.database import engine
from app.ingestion.freshness import evaluate_freshness


@pytest_asyncio.fixture(autouse=True)
async def dispose_database_engine():
    yield
    await engine.dispose()
from app.main import app


@pytest.mark.asyncio
async def test_health_reports_component_and_source_states():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["components"]["application"] == "HEALTHY"
    assert body["components"]["database"] == "HEALTHY"
    assert body["components"]["llm_provider"] in {"HEALTHY", "NOT_CONFIGURED"}
    assert set(body["source_summary"]) == {"HEALTHY", "DEGRADED", "UNAVAILABLE", "NOT_CONFIGURED"}


@pytest.mark.asyncio
async def test_health_reports_database_unavailable_without_details(monkeypatch):
    async def unavailable():
        return False

    monkeypatch.setattr(health_api, "check_db_connection", unavailable)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["components"]["database"] == "UNAVAILABLE"
    assert body["components"]["ingestion"] == "UNAVAILABLE"
    assert "password" not in response.text.lower()
    assert "traceback" not in response.text.lower()


def test_source_failure_is_explicitly_classified():
    state = evaluate_freshness(
        "GDELT",
        configured=True,
        last_success=None,
        last_error="bounded provider timeout",
    )
    assert state.value == "FAILED"
