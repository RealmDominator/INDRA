import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.database import AsyncSessionLocal, engine
from app.services.entity_resolution import resolve_entity


@pytest_asyncio.fixture(autouse=True)
async def dispose_database_engine():
    yield
    await engine.dispose()


@pytest.mark.asyncio
async def test_reference_endpoints_return_seeded_data():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        assert (await client.get("/countries")).json().__len__() == 15
        assert (await client.get("/corridors")).json().__len__() == 6
        assert (await client.get("/crude-grades")).json().__len__() == 14
        assert (await client.get("/routes")).json().__len__() == 15
        assert (await client.get("/refineries")).json().__len__() == 20
        assert (await client.get("/suppliers")).json().__len__() == 8
        assert (await client.get("/reserves")).json()["locations"].__len__() == 3


@pytest.mark.asyncio
async def test_invalid_corridor_filter_returns_404():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/routes?corridor=NOT_A_CORRIDOR")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_entity_resolution_exact_fuzzy_and_unresolved():
    async with AsyncSessionLocal() as session:
        exact = await resolve_entity(session, "country", "India")
        fuzzy = await resolve_entity(session, "corridor", "Strait of Hurmuz")
        unresolved = await resolve_entity(session, "country", "Atlantis")
    assert (exact.resolved, exact.match_type, exact.entity_id) == (True, "EXACT", 1)
    assert fuzzy.resolved and fuzzy.match_type == "FUZZY" and fuzzy.entity_id == 1
    assert not unresolved.resolved and unresolved.entity_id is None
