"""Step-8C focused tests for the persisted event-to-recommendation pipeline.

These tests use the real seeded PostgreSQL database. LLM behavior is supplied
through the existing CallableLLMProvider; no external provider or fake aliases
are introduced.
"""
from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete, select

from app.database import AsyncSessionLocal, engine
from app.intelligence import CallableLLMProvider, StructuredEvent, scenario_supply_gap, rank_procurement
from app.main import app
from app.models import Corridor, EvidenceRecord, GeopoliticalEvent
from app.services.entity_resolution import resolve_entity
from app.services.network import corridor_impact
from app.services.pipeline import ingest_and_process, process_event_by_id
from app.services.risk import corridor_risk_from_events


@pytest_asyncio.fixture(autouse=True)
async def dispose_database_engine():
    yield
    await engine.dispose()


def _source_name() -> str:
    return f"step8c-test-{uuid4().hex}"


async def _cleanup(source_name: str) -> None:
    async with AsyncSessionLocal() as session:
        await session.execute(delete(EvidenceRecord).where(EvidenceRecord.source_name == source_name))
        await session.execute(delete(GeopoliticalEvent).where(GeopoliticalEvent.source_name == source_name))
        await session.commit()


def _provider() -> CallableLLMProvider:
    async def extract(_: str) -> dict:
        return {
            "title": "Shipping disruption reported near Hormuz",
            "event_type": "ATTACK",
            "severity": 8,
            "country_names": ["India"],
            "corridor_names": ["Strait of Hormuz"],
            "route_names": [],
            "disruption_description": "A disruption affects shipping near Hormuz.",
            "confidence": 0.9,
        }

    return CallableLLMProvider(extract, provider="test", model="test-pipeline")


@pytest.mark.asyncio
async def test_ingestion_provider_fallback_and_persistence():
    source = _source_name()
    try:
        async with AsyncSessionLocal() as session:
            result = await ingest_and_process(
                session,
                "A sufficiently long event description without a configured provider.",
                source_name=source,
            )
            assert result.event_id is not None
            assert "event_loaded" in result.pipeline_stages
            assert "no_llm_provider_skip_extraction" in result.pipeline_stages
            assert result.errors == []

            row = await session.get(GeopoliticalEvent, result.event_id)
            assert row is not None
            assert row.source_name == source
            assert row.raw_text is not None

            evidence = (
                await session.execute(
                    select(EvidenceRecord).where(
                        EvidenceRecord.source_name == source,
                        EvidenceRecord.related_entity_id == result.event_id,
                    )
                )
            ).scalars().all()
            assert evidence
            assert evidence[0].data_semantic == "OBSERVED"
    finally:
        await _cleanup(source)


@pytest.mark.asyncio
async def test_provider_extraction_resolution_risk_network_scenario_procurement_and_evidence():
    source = _source_name()
    try:
        async with AsyncSessionLocal() as session:
            result = await ingest_and_process(
                session,
                "A long article describing an attack and crude shipping disruption near the Strait of Hormuz.",
                source_name=source,
                llm_provider=_provider(),
            )

            assert result.event_id is not None
            assert result.extraction["severity"] == 8
            assert result.provider_metadata["model"] == "test-pipeline"
            assert result.entity_resolution["resolved"]["countries"]
            assert result.entity_resolution["resolved"]["corridors"]
            assert result.entity_resolution["unresolved"] == {"countries": [], "corridors": [], "routes": []}
            assert result.risk and 0 <= result.risk["score"] <= 1
            assert result.network_impact["data_semantic"] == "DERIVED"
            assert result.network_impact["affected_routes"]
            assert result.network_impact["affected_refineries"]
            assert result.scenario["scenario_type"] == "HORMUZ_FULL"
            assert result.scenario["supply_gap_mmt"] > 0
            # Seed suppliers intentionally have no fabricated availability;
            # the pipeline reports an infeasible deterministic ranking.
            assert result.procurement["method"] == "deterministic_ranking"
            assert result.procurement["feasible"] is False
            assert [item["stage"] for item in result.evidence] == [
                "source", "extraction", "entity_resolution", "risk", "scenario", "optimization"
            ]

            row = await session.get(GeopoliticalEvent, result.event_id)
            assert row is not None
            assert row.affected_country_ids
            assert row.affected_corridor_ids
            assert row.llm_model_used == "test-pipeline"
    finally:
        await _cleanup(source)


@pytest.mark.asyncio
async def test_entity_resolution_known_fuzzy_and_unresolved_against_seeded_database():
    async with AsyncSessionLocal() as session:
        india = await resolve_entity(session, "country", "India")
        hormuz = await resolve_entity(session, "corridor", "Strait of Hurmuz")
        missing = await resolve_entity(session, "country", "Atlantis")

        assert india.resolved and india.match_type == "EXACT"
        assert hormuz.resolved and hormuz.match_type in {"FUZZY", "CONTAINS"}
        assert missing.resolved is False
        assert missing.entity_id is None


@pytest.mark.asyncio
async def test_risk_recalculation_uses_persisted_event_and_networkx_impact():
    source = _source_name()
    async with AsyncSessionLocal() as session:
        corridor = await session.scalar(select(Corridor).where(Corridor.code == "HORMUZ"))
        assert corridor is not None
        baseline = await corridor_risk_from_events(session, corridor.id)

        event = GeopoliticalEvent(
            event_type="ATTACK",
            title="Step 8C risk test",
            source_name=source,
            affected_corridor_ids=[corridor.id],
            severity=10,
            confidence=1,
            detected_at=datetime.now(timezone.utc).replace(tzinfo=None),
        )
        session.add(event)
        await session.flush()
        recalculated = await corridor_risk_from_events(session, corridor.id)
        impact = await corridor_impact(session, [corridor.id])

        assert recalculated.score > baseline.score
        assert impact["data_semantic"] == "DERIVED"
        assert impact["affected_routes"]
        assert impact["affected_refineries"]
        await session.rollback()


def test_scenario_and_procurement_outputs_are_deterministic_and_semantic():
    first = scenario_supply_gap("HORMUZ_FULL", 30, 100)
    second = scenario_supply_gap("HORMUZ_FULL", 30, 100)
    recommendation = rank_procurement(
        [
            {"id": 1, "available_volume": 2, "unit_cost": 10, "risk_score": 0.1, "compatibility_score": 0.9},
            {"id": 2, "available_volume": 2, "unit_cost": 5, "risk_score": 0.1, "compatibility_score": 0.3},
            {"id": 3, "available_volume": 2, "unit_cost": 5, "risk_score": 0.1, "compatibility_score": 0.9, "is_sanctioned": True},
        ],
        target_volume=1,
    )

    assert first == second
    assert first["data_semantic"] == "DERIVED"
    assert first["supply_gap_mmt"] > 0
    assert recommendation["feasible"] is True
    assert recommendation["method"] == "deterministic_ranking"
    assert recommendation["selected"][0]["candidate_id"] == 1
    assert all(item["data_semantic"] == "DERIVED" for item in recommendation["selected"])


@pytest.mark.asyncio
async def test_pipeline_missing_event_and_api_validation_errors():
    async with AsyncSessionLocal() as session:
        result = await process_event_by_id(session, 2147483647)
        assert result.event_id is None
        assert result.errors == ["Event 2147483647 not found"]

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        invalid = await client.post(
            "/scenarios",
            json={"scenario_type": "HORMUZ_FULL", "duration_days": -1},
        )
        assert invalid.status_code == 422
