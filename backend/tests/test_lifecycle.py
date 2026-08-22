"""Step-12B lifecycle governance regression checks; no live credentials needed."""
from __future__ import annotations

import json
from pathlib import Path

from app.intelligence import StructuredEvent
from app.providers.openrouter import PROMPT_VERSION, SYSTEM_PROMPT, OpenRouterProvider


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_dataset_manifest_has_versioned_provenance_for_current_assets():
    manifest = json.loads((PROJECT_ROOT / "data" / "metadata" / "data_manifest.json").read_text(encoding="utf-8"))
    assert manifest["manifest_version"]
    assert manifest["datasets"]
    for dataset in manifest["datasets"]:
        assert dataset["dataset_id"]
        assert dataset["filename"]
        assert dataset["source_name"]
        # Legacy entries retain unknown acquisition dates as null rather than
        # fabricating timestamps; future entries must supply acquired_at.
        assert "downloaded_at" in dataset
        assert dataset["semantic_class"]
        assert dataset["transformation"]
        assert dataset["checksum"]


def test_prompt_is_versioned_and_preserves_structured_event_contract():
    assert PROMPT_VERSION == "indra-event-extraction/v1"
    for field in StructuredEvent.model_fields:
        assert field in SYSTEM_PROMPT
    assert OpenRouterProvider(api_key="test-key").get_model_info()["prompt_version"] == PROMPT_VERSION
