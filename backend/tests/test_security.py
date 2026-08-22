"""Focused Step-9A security and configuration regression checks."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.config.settings import Settings
from app.main import app


@pytest.mark.asyncio
async def test_cors_allows_configured_frontend_and_rejects_other_origin():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        allowed = await client.options(
            "/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "Content-Type",
            },
        )
        denied = await client.options(
            "/health",
            headers={
                "Origin": "https://not-approved.example",
                "Access-Control-Request-Method": "GET",
            },
        )

    assert allowed.status_code == 200
    assert allowed.headers.get("access-control-allow-origin") == "http://localhost:3000"
    assert "access-control-allow-origin" not in denied.headers


@pytest.mark.asyncio
async def test_invalid_input_returns_validation_error_without_traceback():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/scenarios",
            json={"scenario_type": "HORMUZ_FULL", "duration_days": 9999},
        )

    assert response.status_code == 422
    body = response.json()
    assert "traceback" not in str(body).lower()
    assert "File \"" not in str(body)


@pytest.mark.asyncio
async def test_unconfigured_provider_error_is_safe():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/events/extract",
            json={"text": "A sufficiently long article text for validation."},
        )

    assert response.status_code == 503
    detail = response.json().get("detail", "")
    assert "traceback" not in detail.lower()
    assert "sk-" not in detail


def test_production_debug_default_is_disabled_without_environment_file():
    settings = Settings(_env_file=None)
    assert settings.app_debug is False
