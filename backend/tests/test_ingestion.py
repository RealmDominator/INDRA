"""Step 8B ingestion tests — fixtures only, no live external APIs."""
import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio

from app.ingestion.acled import AcledAdapter
from app.ingestion.base import FetchResult, FreshnessState
from app.ingestion.dedup import event_dedup_key, stable_hash
from app.ingestion.eia import EiaAdapter
from app.ingestion.freshness import evaluate_freshness
from app.ingestion.gdelt import GdeltAdapter
from app.ingestion.ofac import OfacAdapter
from app.ingestion.rbi import RbiAdapter
from app.ingestion.rss import RssAdapter
from app.ingestion.runner import run_eia, run_gdelt, run_rbi
from app.database import engine
from app.ingestion.base import NormalizedEvent

FIXTURES = Path(__file__).parent / "fixtures" / "ingestion"


@pytest_asyncio.fixture(autouse=True)
async def dispose_database_engine():
    yield
    await engine.dispose()


def test_gdelt_parse_normalize_validate():
    raw = json.loads((FIXTURES / "gdelt_sample.json").read_text(encoding="utf-8"))
    adapter = GdeltAdapter()
    records = adapter.parse(raw)
    events = adapter.normalize_events(records)
    accepted, rejected = adapter.validate_events(events)
    assert len(records) == 2
    assert len(accepted) == 2
    assert accepted[0].source_name == "GDELT"
    assert accepted[0].data_semantic == "OBSERVED"
    assert rejected == []


def test_gdelt_deduplication_key_stable():
    event = NormalizedEvent(
        source_name="GDELT",
        source_record_id="https://example.com/gdelt-001",
        title="Test",
    )
    assert event_dedup_key(event) == stable_hash("GDELT", "https://example.com/gdelt-001")


def test_eia_parse_normalize_validate():
    raw = json.loads((FIXTURES / "eia_sample.json").read_text(encoding="utf-8"))
    adapter = EiaAdapter()
    records = adapter.parse(raw)
    prices = adapter.normalize_prices(records)
    accepted, rejected = adapter.validate_prices(prices)
    assert len(accepted) == 2
    assert accepted[0].grade_name == "Brent"
    assert accepted[0].data_semantic == "OBSERVED"


@pytest.mark.asyncio
async def test_eia_not_configured():
    adapter = EiaAdapter()
    fetch = await adapter.fetch()
    assert fetch.success is False
    assert "EIA_API_KEY" in (fetch.error or "")


@pytest.mark.asyncio
async def test_rbi_parse_from_fixture_csv():
    sample = FIXTURES / "rbi_sample.csv"
    adapter = RbiAdapter(processed_path=sample)
    fetch = await adapter.fetch()
    assert fetch.success is True
    records = adapter.parse(fetch.raw_payload)
    rates = adapter.normalize_fx(records)
    accepted, rejected = adapter.validate_fx(rates)
    assert len(accepted) == 2
    assert accepted[0].currency_pair == "USD_INR"


def test_rss_parse_and_keyword_filter():
    xml = (FIXTURES / "rss_sample.xml").read_text(encoding="utf-8")
    adapter = RssAdapter()
    records = adapter.parse({"feeds": [{"feed_url": "https://example.com/feed", "content": xml}]})
    events = adapter.normalize_events(records)
    assert len(events) == 1
    assert "Hormuz" in events[0].title


def test_ofac_parse_energy_filter():
    content = "36,\"PETROLEUM COMPANY\",SDGT\n999,\"GENERIC CORP\",SDGT\n"
    adapter = OfacAdapter()
    records = adapter.parse({"content": content})
    assert len(records) == 1
    entities = adapter.normalize_sanctions(records)
    assert entities[0].entity_name == "PETROLEUM COMPANY"


def test_acled_requires_access():
    adapter = AcledAdapter()
    result = adapter.deferred_result()
    assert result.freshness == FreshnessState.REQUIRES_ACCESS
    assert result.status.value == "SKIPPED"


def test_freshness_not_configured():
    assert evaluate_freshness("EIA", configured=False) == FreshnessState.NOT_CONFIGURED


@pytest.mark.asyncio
async def test_run_gdelt_with_mock_client():
    from app.database import AsyncSessionLocal

    raw = json.loads((FIXTURES / "gdelt_sample.json").read_text(encoding="utf-8"))
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = raw
    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response
    adapter = GdeltAdapter(client=mock_client)

    async with AsyncSessionLocal() as session:
        result = await run_gdelt(session, adapter=adapter)
    assert result.records_fetched == 2
    assert result.records_accepted + result.records_duplicate == 2
    assert result.source_name == "GDELT"


@pytest.mark.asyncio
async def test_run_gdelt_deduplicates_on_second_run():
    from app.database import AsyncSessionLocal

    raw = json.loads((FIXTURES / "gdelt_sample.json").read_text(encoding="utf-8"))
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = raw
    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response
    adapter = GdeltAdapter(client=mock_client)

    async with AsyncSessionLocal() as session:
        first = await run_gdelt(session, adapter=adapter)
        second = await run_gdelt(session, adapter=adapter)
    assert first.records_fetched == 2
    assert first.records_accepted + first.records_duplicate == 2
    assert second.records_duplicate == 2
    assert second.records_accepted == 0
