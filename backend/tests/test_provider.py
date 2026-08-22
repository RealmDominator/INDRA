"""
Step-8A provider tests.
Tests the OpenRouter provider without requiring an external API key.
All tests use mocks — deterministic engine tests remain in test_intelligence.py.
"""
import asyncio
import json
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch, MagicMock

from httpx import ASGITransport, AsyncClient

from app.intelligence import (
    ExtractionResult, ProviderMetadata, StructuredEvent,
    UnconfiguredLLMProvider, CallableLLMProvider,
)
from app.providers.factory import create_llm_provider
from app.providers.openrouter import OpenRouterProvider
from app.main import app
from app.database import engine


@pytest_asyncio.fixture(autouse=True)
async def dispose_database_engine():
    yield
    await engine.dispose()


# ---------------------------------------------------------------------------
# OpenRouterProvider unit tests
# ---------------------------------------------------------------------------

def test_openrouter_provider_rejects_missing_key():
    """Provider must refuse to initialize without an API key."""
    with pytest.raises(ValueError, match="API key is required"):
        OpenRouterProvider(api_key="")

    with pytest.raises(ValueError, match="API key is required"):
        OpenRouterProvider(api_key=None)


def test_openrouter_provider_accepts_valid_key():
    """Provider initializes with a valid API key."""
    provider = OpenRouterProvider(api_key="sk-test-123")
    assert provider.model == "openai/gpt-4o-mini"
    assert provider.timeout_seconds == 15.0
    assert provider.max_retries == 2


def test_openrouter_provider_model_info():
    """get_model_info returns metadata for evidence trail."""
    provider = OpenRouterProvider(api_key="sk-test", model="anthropic/claude-3.5-haiku")
    info = provider.get_model_info()
    assert info["provider"] == "openrouter"
    assert info["model"] == "anthropic/claude-3.5-haiku"


# ---------------------------------------------------------------------------
# Mocked extraction tests
# ---------------------------------------------------------------------------

VALID_LLM_RESPONSE = {
    "title": "Iran military drill near Hormuz",
    "event_type": "MILITARY",
    "severity": 7,
    "country_names": ["Iran"],
    "corridor_names": ["Hormuz"],
    "route_names": [],
    "disruption_description": "Iranian military exercises near Strait of Hormuz",
    "confidence": 0.9,
}


def _mock_openrouter_response(payload: dict, status_code: int = 200):
    """Create a mock httpx response for OpenRouter."""
    mock_response = MagicMock()
    mock_response.status_code = status_code
    mock_response.json.return_value = {
        "choices": [{"message": {"content": json.dumps(payload)}}]
    }
    mock_response.text = json.dumps({"choices": [{"message": {"content": json.dumps(payload)}}]})
    return mock_response


@pytest.mark.asyncio
async def test_provider_validates_structured_output():
    """Valid LLM response → StructuredEvent + metadata."""
    provider = OpenRouterProvider(api_key="sk-test")

    with patch("app.providers.openrouter.httpx.AsyncClient") as MockClient:
        mock_client = AsyncMock()
        mock_client.post.return_value = _mock_openrouter_response(VALID_LLM_RESPONSE)
        MockClient.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        MockClient.return_value.__aexit__ = AsyncMock(return_value=False)

        result = await provider.extract_event("Iran's military conducted exercises...")
        assert isinstance(result, ExtractionResult)
        assert result.event.event_type == "MILITARY"
        assert result.event.severity == 7
        assert result.event.country_names == ["Iran"]
        assert result.metadata.provider == "openrouter"
        assert result.metadata.attempts == 1
        assert result.metadata.latency_ms >= 0


@pytest.mark.asyncio
async def test_provider_rejects_malformed_json():
    """Garbage response after all retries → ValueError."""
    provider = OpenRouterProvider(api_key="sk-test", max_retries=1)

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "this is not json at all"}}]
    }
    mock_response.text = "ok"

    with patch("app.providers.openrouter.httpx.AsyncClient") as MockClient:
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        MockClient.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        MockClient.return_value.__aexit__ = AsyncMock(return_value=False)

        with pytest.raises(ValueError, match="extraction failed after"):
            await provider.extract_event("some article text here")


@pytest.mark.asyncio
async def test_provider_handles_api_error():
    """Non-200 status code → RuntimeError → retries → ValueError."""
    provider = OpenRouterProvider(api_key="sk-test", max_retries=0)

    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"

    with patch("app.providers.openrouter.httpx.AsyncClient") as MockClient:
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        MockClient.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        MockClient.return_value.__aexit__ = AsyncMock(return_value=False)

        with pytest.raises(ValueError, match="extraction failed"):
            await provider.extract_event("article text")


@pytest.mark.asyncio
async def test_provider_rejects_database_ids_in_output():
    """LLM output with integer IDs in country_names → validation error."""
    provider = OpenRouterProvider(api_key="sk-test", max_retries=0)

    bad_payload = {**VALID_LLM_RESPONSE, "country_names": [1, 2]}

    with patch("app.providers.openrouter.httpx.AsyncClient") as MockClient:
        mock_client = AsyncMock()
        mock_client.post.return_value = _mock_openrouter_response(bad_payload)
        MockClient.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        MockClient.return_value.__aexit__ = AsyncMock(return_value=False)

        with pytest.raises(ValueError, match="extraction failed"):
            await provider.extract_event("article text")


@pytest.mark.asyncio
async def test_provider_retries_then_succeeds():
    """First call returns bad JSON, second returns valid → success on attempt 2."""
    provider = OpenRouterProvider(api_key="sk-test", max_retries=1)

    bad_response = MagicMock()
    bad_response.status_code = 200
    bad_response.json.return_value = {"choices": [{"message": {"content": "{invalid"}}]}
    bad_response.text = "ok"

    good_response = _mock_openrouter_response(VALID_LLM_RESPONSE)

    with patch("app.providers.openrouter.httpx.AsyncClient") as MockClient:
        mock_client = AsyncMock()
        mock_client.post.side_effect = [bad_response, good_response]
        MockClient.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        MockClient.return_value.__aexit__ = AsyncMock(return_value=False)

        result = await provider.extract_event("some article")
        assert result.metadata.attempts == 2
        assert result.event.event_type == "MILITARY"


@pytest.mark.asyncio
async def test_provider_metadata_recorded():
    """Provider metadata includes provider name, model, attempts, latency."""
    provider = OpenRouterProvider(api_key="sk-test", model="google/gemini-2.0-flash-001")

    with patch("app.providers.openrouter.httpx.AsyncClient") as MockClient:
        mock_client = AsyncMock()
        mock_client.post.return_value = _mock_openrouter_response(VALID_LLM_RESPONSE)
        MockClient.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        MockClient.return_value.__aexit__ = AsyncMock(return_value=False)

        result = await provider.extract_event("article text")
        assert result.metadata.provider == "openrouter"
        assert result.metadata.model == "google/gemini-2.0-flash-001"
        assert result.metadata.attempts == 1
        assert isinstance(result.metadata.latency_ms, int)


# ---------------------------------------------------------------------------
# UnconfiguredLLMProvider tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_unconfigured_provider_raises_cleanly():
    """UnconfiguredLLMProvider raises RuntimeError with clear message."""
    provider = UnconfiguredLLMProvider()
    with pytest.raises(RuntimeError, match="No application LLM provider is configured"):
        await provider.extract_event("any text")


# ---------------------------------------------------------------------------
# CallableLLMProvider tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_callable_provider_validates_output():
    """CallableLLMProvider validates the callable's output through StructuredEvent."""
    async def mock_fn(text: str) -> dict:
        return VALID_LLM_RESPONSE

    provider = CallableLLMProvider(function=mock_fn, provider="test", model="test-model")
    result = await provider.extract_event("article text")
    assert result.event.event_type == "MILITARY"
    assert result.metadata.provider == "test"


@pytest.mark.asyncio
async def test_callable_provider_rejects_invalid():
    """CallableLLMProvider rejects invalid output from callable."""
    async def bad_fn(text: str) -> dict:
        return {"event_type": "INVALID_TYPE", "severity": 999}

    provider = CallableLLMProvider(function=bad_fn, provider="test", model="test-model", retries=0)
    with pytest.raises(ValueError, match="extraction failed"):
        await provider.extract_event("article text")


# ---------------------------------------------------------------------------
# Extraction endpoint integration test (mocked provider)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_callable_provider_timeout():
    """CallableLLMProvider raises after timeout with retries exhausted."""
    async def slow_fn(text: str) -> dict:
        await asyncio.sleep(2)
        return VALID_LLM_RESPONSE

    provider = CallableLLMProvider(
        function=slow_fn, provider="test", model="test-model",
        timeout_seconds=0.05, retries=0,
    )
    with pytest.raises(ValueError, match="extraction failed"):
        await provider.extract_event("article text")


@pytest.mark.asyncio
async def test_callable_provider_rejects_missing_required_field():
    """Missing required StructuredEvent fields fail validation."""
    async def incomplete_fn(text: str) -> dict:
        return {"event_type": "ATTACK", "severity": 5}

    provider = CallableLLMProvider(
        function=incomplete_fn, provider="test", model="test-model", retries=0,
    )
    with pytest.raises(ValueError, match="extraction failed"):
        await provider.extract_event("article text")


@pytest.mark.asyncio
async def test_extraction_endpoint_success_with_entity_resolution():
    """POST /events/extract returns extraction + entity resolution when provider is mocked."""
    async def mock_extract(text: str):
        return VALID_LLM_RESPONSE

    provider = CallableLLMProvider(
        function=mock_extract, provider="test", model="openai/gpt-4o-mini",
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        app.state.llm_provider = provider
        response = await client.post(
            "/events/extract",
            json={"text": "Iran's military conducted exercises near the Strait of Hormuz on Monday, raising concerns for tanker traffic."},
        )
    assert response.status_code == 200
    body = response.json()
    assert body["event"]["event_type"] == "MILITARY"
    assert body["provider_metadata"]["provider"] == "test"
    assert any(c.get("name") == "Iran" for c in body["resolved"]["countries"])
    assert any(e.get("stage") == "extraction" for e in body["evidence"])


def test_create_llm_provider_unconfigured_without_key(monkeypatch):
    """Factory returns UnconfiguredLLMProvider when no API key is set."""
    from app.config.settings import Settings

    fake_settings = Settings(
        database_url="postgresql+asyncpg://u:p@localhost/db",
        openrouter_api_key="",
        llm_provider="openrouter",
    )
    monkeypatch.setattr("app.providers.factory.get_settings", lambda: fake_settings)
    provider = create_llm_provider()
    assert isinstance(provider, UnconfiguredLLMProvider)


@pytest.mark.asyncio
async def test_extraction_endpoint_returns_503_without_provider():
    """POST /events/extract returns 503 when no LLM is configured."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        app.state.llm_provider = UnconfiguredLLMProvider()
        response = await client.post("/events/extract", json={"text": "Iran deployed forces near the Strait of Hormuz on Monday."})
    assert response.status_code == 503
    assert "LLM provider" in response.json()["detail"]


@pytest.mark.asyncio
async def test_extraction_endpoint_rejects_short_text():
    """POST /events/extract rejects very short text."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/events/extract", json={"text": "too short"})
    assert response.status_code == 422
