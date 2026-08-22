"""
INDRA — OpenRouter LLM Provider

Implements the LLMProvider protocol using the OpenRouter API.
Supports any model accessible through OpenRouter (GPT-4o-mini, Claude,
Gemini Flash, Llama, etc.) via a single API key.

Configuration via environment variables:
    OPENROUTER_API_KEY  — required for live extraction
    LLM_MODEL           — OpenRouter model ID (default: openai/gpt-4o-mini)
    LLM_TIMEOUT_SECONDS — per-call timeout (default: 15)
    LLM_MAX_RETRIES     — retries on malformed output (default: 2)

The LLM extracts structured event data ONLY. It must NOT:
    - generate database IDs
    - calculate risk scores
    - perform scenario arithmetic
    - optimize procurement
    - invent prices or supply data
"""
from __future__ import annotations

import json
import logging
import time
from typing import Any

import httpx

from app.intelligence import ExtractionResult, ProviderMetadata, StructuredEvent

logger = logging.getLogger("indra.providers.openrouter")

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# System prompt instructs the model to act as a geopolitical event extractor
# for India's energy supply chain. Temperature 0 for determinism.
SYSTEM_PROMPT = """\
You are a structured event extractor for the INDRA India energy supply-chain \
disruption monitoring system. Given a news article, extract a single JSON object \
with EXACTLY these fields:

{
  "title": "concise event title",
  "event_type": "SANCTION" | "MILITARY" | "PORT_CLOSURE" | "ATTACK" | "DIPLOMATIC" | "OTHER",
  "severity": <integer 1-10>,
  "country_names": ["list of country names mentioned"],
  "corridor_names": ["HORMUZ" | "RED_SEA" | "SUEZ" | "MALACCA" | "RUSSIA" | "CAPE"],
  "route_names": [],
  "disruption_description": "one sentence describing the disruption",
  "confidence": <float 0.0 to 1.0>
}

Rules:
- Use ONLY human-readable country names and corridor codes. NEVER output database IDs.
- severity: 1 = negligible, 5 = moderate disruption, 10 = catastrophic
- corridor_names: only include corridors directly affected. Use empty list if none.
- confidence: your confidence that this is a real energy supply-chain event
- Return ONLY the JSON object. No markdown, no explanation, no code fences.
"""


class OpenRouterProvider:
    """
    LLM provider using the OpenRouter API for structured event extraction.

    Implements the LLMProvider protocol from app.intelligence.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "openai/gpt-4o-mini",
        timeout_seconds: float = 15.0,
        max_retries: int = 2,
        app_name: str = "INDRA",
        app_url: str = "",
    ):
        if not api_key:
            raise ValueError(
                "OpenRouter API key is required. "
                "Set OPENROUTER_API_KEY in your environment."
            )
        self._api_key = api_key
        self.model = model
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self._app_name = app_name
        self._app_url = app_url

    async def extract_event(self, text: str) -> ExtractionResult:
        """
        Send article text to OpenRouter, validate the structured output,
        and return an ExtractionResult with provider metadata.

        Retries up to max_retries times on malformed JSON or validation errors.
        Raises ValueError after all retries are exhausted.
        """
        started = time.perf_counter()
        last_error: Exception | None = None

        for attempt in range(1, self.max_retries + 2):
            try:
                payload = await self._call_api(text)
                event = StructuredEvent.model_validate(payload)
                latency_ms = int((time.perf_counter() - started) * 1000)

                logger.info(
                    "extraction_success model=%s attempt=%d latency_ms=%d event_type=%s",
                    self.model, attempt, latency_ms, event.event_type,
                )

                return ExtractionResult(
                    event=event,
                    metadata=ProviderMetadata(
                        provider="openrouter",
                        model=self.model,
                        attempts=attempt,
                        latency_ms=latency_ms,
                    ),
                )
            except Exception as exc:
                last_error = exc
                logger.warning(
                    "extraction_retry model=%s attempt=%d error=%s",
                    self.model, attempt, str(exc)[:200],
                )

        raise ValueError(
            f"Structured extraction failed after {self.max_retries + 1} attempts: "
            f"{last_error}"
        )

    async def _call_api(self, text: str) -> dict[str, Any]:
        """Make a single API call to OpenRouter and parse the response JSON."""
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": self._app_url or "https://github.com/indra-project",
            "X-Title": self._app_name,
        }

        request_body = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Extract structured event data from this article:\n\n{text}"},
            ],
            "temperature": 0,
            "max_tokens": 300,
            "response_format": {"type": "json_object"},
        }

        # Log request without secrets
        logger.debug(
            "openrouter_request model=%s text_length=%d",
            self.model, len(text),
        )

        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            response = await client.post(
                OPENROUTER_URL,
                headers=headers,
                json=request_body,
            )

        if response.status_code != 200:
            error_detail = response.text[:300] if response.text else "no body"
            raise RuntimeError(
                f"OpenRouter API error {response.status_code}: {error_detail}"
            )

        data = response.json()

        # Extract the content from the OpenAI-compatible response format
        choices = data.get("choices", [])
        if not choices:
            raise ValueError("OpenRouter response contained no choices")

        content = choices[0].get("message", {}).get("content", "")
        if not content:
            raise ValueError("OpenRouter response contained empty content")

        # Strip markdown fences if the model wraps output
        content = content.strip()
        if content.startswith("```"):
            # Remove ```json ... ``` wrapping
            lines = content.split("\n")
            content = "\n".join(
                line for line in lines
                if not line.strip().startswith("```")
            ).strip()

        try:
            return json.loads(content)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"LLM returned invalid JSON: {content[:200]}"
            ) from exc

    def get_model_info(self) -> dict[str, str]:
        """Return model metadata for the evidence trail."""
        return {
            "provider": "openrouter",
            "model": self.model,
            "timeout_seconds": str(self.timeout_seconds),
            "max_retries": str(self.max_retries),
        }
