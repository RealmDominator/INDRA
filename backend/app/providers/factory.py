"""Create the configured application LLM provider."""
import logging

from app.config.settings import get_settings
from app.intelligence import UnconfiguredLLMProvider

logger = logging.getLogger("indra.providers")


def create_llm_provider():
    """Return OpenRouterProvider when configured, else UnconfiguredLLMProvider."""
    settings = get_settings()
    if settings.llm_provider == "openrouter" and settings.openrouter_api_key:
        from app.providers.openrouter import OpenRouterProvider

        logger.info("LLM provider configured: openrouter model=%s", settings.llm_model)
        return OpenRouterProvider(
            api_key=settings.openrouter_api_key,
            model=settings.llm_model,
            timeout_seconds=settings.llm_timeout_seconds,
            max_retries=settings.llm_max_retries,
        )
    logger.info("LLM provider: UnconfiguredLLMProvider (no API key set)")
    return UnconfiguredLLMProvider(model=settings.llm_model)
