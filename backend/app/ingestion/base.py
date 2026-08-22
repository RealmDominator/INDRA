"""Canonical records and adapter protocol for Step 8B ingestion."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any, Protocol


class FreshnessState(StrEnum):
    FRESH = "FRESH"
    STALE = "STALE"
    FAILED = "FAILED"
    NOT_CONFIGURED = "NOT_CONFIGURED"
    DEFERRED = "DEFERRED"
    PARTIAL = "PARTIAL"
    REQUIRES_ACCESS = "REQUIRES_ACCESS"


class IngestionStatus(StrEnum):
    SUCCESS = "SUCCESS"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


@dataclass
class SourceRecord:
    """Parsed record from a single source before normalization."""
    source_record_id: str
    payload: dict[str, Any]


@dataclass
class NormalizedEvent:
    """Canonical event observation compatible with geopolitical_events."""
    source_name: str
    source_record_id: str
    title: str
    description: str | None = None
    source_url: str | None = None
    raw_text: str | None = None
    occurred_at: datetime | None = None
    source_published_at: datetime | None = None
    event_type: str = "OTHER"
    severity: float | None = None
    confidence: float | None = None
    data_semantic: str = "OBSERVED"
    is_simulated: bool = False


@dataclass
class NormalizedPrice:
    grade_name: str
    price_usd_per_barrel: float
    source: str
    source_record_id: str
    source_timestamp: datetime | None
    data_semantic: str = "OBSERVED"
    crude_grade_id: int | None = None


@dataclass
class NormalizedFxRate:
    currency_pair: str
    rate: float
    source: str
    source_record_id: str
    source_timestamp: datetime | None
    data_semantic: str = "OBSERVED"


@dataclass
class NormalizedSanctionEntity:
    entity_name: str
    source_record_id: str
    aliases: list[str] = field(default_factory=list)
    program: str | None = None
    updated_at: datetime | None = None
    data_semantic: str = "OBSERVED"


@dataclass
class FetchResult:
    source_name: str
    fetched_at: datetime
    success: bool
    raw_payload: Any = None
    error: str | None = None
    http_status: int | None = None
    duration_ms: int | None = None


@dataclass
class IngestionRunResult:
    source_name: str
    source_type: str
    status: IngestionStatus
    fetched_at: datetime | None
    source_timestamp: datetime | None
    records_fetched: int = 0
    records_accepted: int = 0
    records_rejected: int = 0
    records_duplicate: int = 0
    error: str | None = None
    freshness: FreshnessState = FreshnessState.FAILED
    semantic_class: str = "OBSERVED"
    details: dict[str, Any] = field(default_factory=dict)


class SourceAdapter(Protocol):
    source_name: str
    source_type: str

    async def fetch(self) -> FetchResult: ...
    def parse(self, raw: Any) -> list[SourceRecord]: ...
    def normalize_events(self, records: list[SourceRecord]) -> list[NormalizedEvent]: ...
    def validate_events(self, events: list[NormalizedEvent]) -> tuple[list[NormalizedEvent], list[str]]: ...
