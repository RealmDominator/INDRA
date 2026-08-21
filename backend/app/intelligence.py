"""Deterministic Step-6B intelligence primitives; no external provider calls."""
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, Protocol, Awaitable, Callable
import asyncio
import time

from pydantic import BaseModel, Field, field_validator


class EventType(StrEnum):
    SANCTION = "SANCTION"
    MILITARY = "MILITARY"
    PORT_CLOSURE = "PORT_CLOSURE"
    ATTACK = "ATTACK"
    DIPLOMATIC = "DIPLOMATIC"
    OTHER = "OTHER"


class StructuredEvent(BaseModel):
    title: str
    event_type: EventType
    severity: int = Field(ge=1, le=10)
    country_names: list[str] = []
    corridor_names: list[str] = []
    route_names: list[str] = []
    disruption_description: str | None = None
    occurred_at: datetime | None = None
    source_url: str | None = None
    source_name: str | None = None
    confidence: float = Field(ge=0, le=1)

    @field_validator("country_names", "corridor_names", "route_names")
    @classmethod
    def names_only(cls, values):
        if any(isinstance(value, int) for value in values):
            raise ValueError("LLM output must contain names/codes, not database IDs")
        return values


class ProviderMetadata(BaseModel):
    provider: str
    model: str
    attempts: int
    latency_ms: int | None = None


class ExtractionResult(BaseModel):
    event: StructuredEvent
    metadata: ProviderMetadata


class LLMProvider(Protocol):
    async def extract_event(self, text: str) -> ExtractionResult: ...


class UnconfiguredLLMProvider:
    """Explicitly safe provider: extraction requires a configured adapter."""
    def __init__(self, model: str = "not_configured"):
        self.model = model

    async def extract_event(self, text: str) -> ExtractionResult:
        raise RuntimeError("No application LLM provider is configured; external calls are disabled")


class CallableLLMProvider:
    """Adapter for a caller-supplied structured-output function with bounded retries."""
    def __init__(self, function: Callable[[str], Awaitable[dict]], provider: str, model: str, timeout_seconds: float = 15, retries: int = 2):
        self.function, self.provider, self.model = function, provider, model
        self.timeout_seconds, self.retries = timeout_seconds, retries

    async def extract_event(self, text: str) -> ExtractionResult:
        started = time.perf_counter()
        last_error = None
        for attempt in range(1, self.retries + 2):
            try:
                payload = await asyncio.wait_for(self.function(text), timeout=self.timeout_seconds)
                event = StructuredEvent.model_validate(payload)
                return ExtractionResult(event=event, metadata=ProviderMetadata(provider=self.provider, model=self.model, attempts=attempt, latency_ms=int((time.perf_counter() - started) * 1000)))
            except Exception as exc:
                last_error = exc
        raise ValueError(f"structured extraction failed after {self.retries + 1} attempts: {last_error}")


class RiskWeights(BaseModel):
    event_severity: float = 0.25
    event_recency: float = 0.20
    chokepoint_exposure: float = 0.20
    conflict_sanctions: float = 0.15
    historical_rate: float = 0.10
    india_dependency: float = 0.10

    @field_validator("event_severity", "event_recency", "chokepoint_exposure", "conflict_sanctions", "historical_rate", "india_dependency")
    @classmethod
    def nonnegative(cls, value):
        if value < 0:
            raise ValueError("risk weights must be non-negative")
        return value


class RiskResult(BaseModel):
    score: float
    display_score: float
    risk_level: str
    components: dict[str, dict[str, float]]
    data_semantic: str = "DERIVED"
    calculation_method: str = "weighted_rule_v1"


def build_evidence_chain(source: dict[str, Any] | None = None, *, extraction: dict[str, Any] | None = None,
                         entity_resolution: dict[str, Any] | None = None, risk: dict[str, Any] | None = None,
                         scenario: dict[str, Any] | None = None, optimization: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    chain = []
    for stage, payload in (("source", source), ("extraction", extraction), ("entity_resolution", entity_resolution),
                           ("risk", risk), ("scenario", scenario), ("optimization", optimization)):
        if payload is not None:
            chain.append({"stage": stage, "data_semantic": payload.get("data_semantic", "OBSERVED" if stage == "source" else "DERIVED"), "payload": payload})
    return chain


def classify_risk(score: float) -> str:
    if score < 0.30: return "LOW"
    if score < 0.50: return "MODERATE"
    if score < 0.70: return "HIGH"
    if score < 0.85: return "CRITICAL"
    return "EXTREME"


def calculate_risk(features: dict[str, float], weights: RiskWeights | None = None) -> RiskResult:
    weights = weights or RiskWeights()
    values = {name: max(0.0, min(1.0, float(features.get(name, 0.0)))) for name in RiskWeights.model_fields}
    components = {name: {"value": values[name], "weight": getattr(weights, name), "contribution": values[name] * getattr(weights, name)} for name in values}
    score = sum(item["contribution"] for item in components.values())
    return RiskResult(score=score, display_score=score * 100, risk_level=classify_risk(score), components=components)


def scenario_supply_gap(scenario_type: str, duration_days: int, reduction_pct: float = 100.0) -> dict[str, Any]:
    if duration_days < 0 or duration_days > 365:
        raise ValueError("duration_days must be between 0 and 365")
    shares = {"HORMUZ_FULL": 0.42, "HORMUZ_PARTIAL": 0.42, "RED_SEA": 0.05, "RUSSIA_LOSS": 0.37}
    share = shares.get(scenario_type, 0.0)
    affected_per_day = 0.56 * share * (reduction_pct / 100)
    gap = affected_per_day * duration_days
    return {"scenario_type": scenario_type, "duration_days": duration_days, "affected_volume_per_day_mmt": affected_per_day, "supply_gap_mmt": gap, "data_semantic": "DERIVED"}


def rank_procurement(candidates: list[dict[str, Any]], target_volume: float, compatibility_threshold: float = 0.5) -> dict[str, Any]:
    usable = [c for c in candidates if not c.get("is_sanctioned") and c.get("is_operational", True) and c.get("compatibility_score", 0) >= compatibility_threshold]
    usable.sort(key=lambda c: (float(c.get("unit_cost", 0)) + float(c.get("risk_score", 0)) * 10, float(c.get("transit_days", 0)), c.get("id", 0)))
    selected, remaining = [], target_volume
    for candidate in usable:
        volume = min(remaining, float(candidate.get("available_volume", 0)))
        if volume > 0:
            selected.append({"candidate_id": candidate.get("id"), "volume": volume, "data_semantic": "DERIVED"})
            remaining -= volume
    return {"selected": selected, "feasible": remaining <= 1e-9, "unmet_volume": max(0.0, remaining), "method": "deterministic_ranking"}
