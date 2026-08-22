"""
Step-8C — Full event processing pipeline.

Orchestrates: Event → LLM Extraction → Entity Resolution → Persistence
→ Risk → Network Impact → Scenario → Procurement → Evidence

Both ingestion-triggered and manual events use this single path.
The LLM handles extraction ONLY. All downstream is deterministic.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.ingestion.base import NormalizedEvent
from app.ingestion.persistence import persist_event
from app.ingestion.provenance import create_source_evidence
from app.intelligence import (
    ExtractionResult,
    StructuredEvent,
    UnconfiguredLLMProvider,
    build_evidence_chain,
    calculate_risk,
    classify_risk,
    optimize_procurement,
    scenario_supply_gap,
)
from app.models import Corridor, Supplier
from app.models.ingestion import GeopoliticalEvent
from app.services.intelligence import resolve_structured_event
from app.services.network import corridor_impact
from app.services.risk import corridor_risk_from_events

logger = logging.getLogger("indra.pipeline")


class PipelineResult(BaseModel):
    """Complete result of the event processing pipeline."""
    event_id: int | None = None
    event_title: str | None = None
    extraction: dict | None = None
    entity_resolution: dict | None = None
    risk: dict | None = None
    network_impact: dict | None = None
    scenario: dict | None = None
    procurement: dict | None = None
    evidence: list[dict] = []
    provider_metadata: dict | None = None
    data_semantic: str = "DERIVED"
    pipeline_stages: list[str] = []
    errors: list[str] = []


async def process_event_by_id(
    session: AsyncSession,
    event_id: int,
    llm_provider=None,
) -> PipelineResult:
    """
    Process an already-persisted event through the full pipeline.

    Steps:
    1. Load event from DB
    2. If raw_text exists + LLM available → extract structured fields
    3. Entity resolution → resolve country/corridor/route names
    4. Update event with resolved entity IDs
    5. Calculate risk for affected corridors
    6. NetworkX impact → affected routes/refineries
    7. Scenario for most-affected corridor
    8. Procurement alternatives
    9. Evidence chain
    """
    result = PipelineResult()

    # 1. Load event
    event = await session.get(GeopoliticalEvent, event_id)
    if event is None:
        result.errors.append(f"Event {event_id} not found")
        return result
    result.event_id = event.id
    result.event_title = event.title
    result.pipeline_stages.append("event_loaded")

    # 2. LLM extraction (if raw text available and LLM configured)
    structured_event = None
    if event.raw_text and llm_provider and not isinstance(llm_provider, UnconfiguredLLMProvider):
        try:
            extraction_result = await llm_provider.extract_event(event.raw_text)
            structured_event = extraction_result.event
            result.extraction = extraction_result.event.model_dump()
            result.provider_metadata = extraction_result.metadata.model_dump()
            result.pipeline_stages.append("llm_extraction")

            # Update event with extracted fields
            if structured_event.event_type:
                event.event_type = structured_event.event_type.value
            if structured_event.severity:
                event.severity = Decimal(str(structured_event.severity / 10.0))
            if structured_event.confidence:
                event.confidence = Decimal(str(structured_event.confidence))
            event.llm_model_used = extraction_result.metadata.model
        except Exception as exc:
            logger.warning("pipeline_extraction_failed event_id=%d error=%s", event_id, str(exc)[:200])
            result.errors.append(f"LLM extraction failed: {exc}")
    elif not event.raw_text:
        result.pipeline_stages.append("no_raw_text_skip_extraction")
    else:
        result.pipeline_stages.append("no_llm_provider_skip_extraction")

    # 3. Entity resolution
    if structured_event:
        resolution = await resolve_structured_event(session, structured_event)
    else:
        # Build a minimal StructuredEvent from DB fields for resolution
        stored_severity = float(event.severity) if event.severity is not None else 0.5
        structured_event = StructuredEvent(
            title=event.title or "Unknown",
            event_type=event.event_type or "OTHER",
            severity=max(1, min(10, int(round(stored_severity * 10)))),
            confidence=float(event.confidence or 0.5),
            country_names=[],
            corridor_names=[],
            route_names=[],
        )
        resolution = {"resolved": {"countries": [], "corridors": [], "routes": []},
                       "unresolved": {"countries": [], "corridors": [], "routes": []}}
    result.entity_resolution = resolution
    result.pipeline_stages.append("entity_resolution")

    # 4. Update event with resolved IDs
    resolved_corridor_ids = [c["id"] for c in resolution["resolved"].get("corridors", [])]
    resolved_country_ids = [c["id"] for c in resolution["resolved"].get("countries", [])]
    resolved_route_ids = [c["id"] for c in resolution["resolved"].get("routes", [])]

    if resolved_corridor_ids:
        event.affected_corridor_ids = resolved_corridor_ids
    if resolved_country_ids:
        event.affected_country_ids = resolved_country_ids
    if resolved_route_ids:
        event.affected_route_ids = resolved_route_ids
    await session.flush()

    # 5. Risk calculation for affected corridors
    risk_results = {}
    if resolved_corridor_ids:
        for cid in resolved_corridor_ids:
            try:
                risk = await corridor_risk_from_events(session, cid)
                risk_results[cid] = risk.model_dump()
            except Exception as exc:
                logger.warning("pipeline_risk_failed corridor_id=%d error=%s", cid, str(exc)[:100])
        if risk_results:
            # Use the highest-risk corridor as the primary risk
            max_risk = max(risk_results.values(), key=lambda r: r["score"])
            result.risk = max_risk
        result.pipeline_stages.append("risk_calculation")

    # 6. Network impact
    if resolved_corridor_ids:
        try:
            impact = await corridor_impact(session, resolved_corridor_ids)
            result.network_impact = impact
            result.pipeline_stages.append("network_impact")
        except Exception as exc:
            logger.warning("pipeline_network_failed error=%s", str(exc)[:200])
            result.errors.append(f"Network impact failed: {exc}")

    # 7. Scenario for most-affected corridor
    if resolved_corridor_ids:
        corridor = await session.get(Corridor, resolved_corridor_ids[0])
        if corridor:
            corridor_code = corridor.code
            scenario_type_map = {
                "HORMUZ": "HORMUZ_FULL",
                "RED_SEA": "RED_SEA",
                "RUSSIA": "RUSSIA_LOSS",
            }
            scenario_type = scenario_type_map.get(corridor_code)
            if scenario_type:
                try:
                    severity_val = float(event.severity or 0.5)
                    duration = max(7, int(severity_val * 30))
                    reduction = min(100, max(10, int(severity_val * 100)))
                    scenario = scenario_supply_gap(scenario_type, duration, reduction)
                    result.scenario = scenario
                    result.pipeline_stages.append("scenario")
                except Exception as exc:
                    logger.warning("pipeline_scenario_failed error=%s", str(exc)[:100])

    # 8. Procurement
    if result.scenario and result.scenario.get("supply_gap_mmt", 0) > 0:
        try:
            # Fetch real suppliers from DB
            from sqlalchemy import select
            suppliers = (await session.execute(
                select(Supplier).limit(20)
            )).scalars().all()

            candidates = []
            for s in suppliers:
                candidates.append({
                    "id": s.id,
                    "name": s.name,
                    "available_volume": float(s.annual_supply_capacity_mmtpa or 0),
                    "unit_cost": 70 + float(s.current_sanctions_risk or 0) * 10,
                    "risk_score": float(s.current_sanctions_risk or 0.3),
                    "transit_days": 15,
                    "compatibility_score": 0.8,
                    "is_operational": True,
                    "is_sanctioned": bool(s.is_sanctioned),
                })

            if candidates:
                target = result.scenario["supply_gap_mmt"]
                procurement = optimize_procurement(candidates, target)
                result.procurement = procurement
                result.pipeline_stages.append("procurement")
        except Exception as exc:
            logger.warning("pipeline_procurement_failed error=%s", str(exc)[:200])
            result.errors.append(f"Procurement failed: {exc}")

    # 9. Evidence chain
    source_semantic = "SIMULATED" if event.is_simulated else "OBSERVED"
    evidence = build_evidence_chain(
        source={"source_name": event.source_name, "source_url": event.source_url, "data_semantic": source_semantic} if event.source_name else None,
        extraction=result.extraction,
        entity_resolution={"data_semantic": "DERIVED", **(result.entity_resolution or {})},
        risk=result.risk,
        scenario=result.scenario,
        optimization=result.procurement,
    )
    result.evidence = evidence
    result.pipeline_stages.append("evidence")

    await session.commit()
    logger.info(
        "pipeline_complete event_id=%d stages=%s errors=%d",
        event_id, ",".join(result.pipeline_stages), len(result.errors),
    )
    return result


async def ingest_and_process(
    session: AsyncSession,
    text: str,
    source_name: str = "manual",
    llm_provider=None,
) -> PipelineResult:
    """
    Accept raw article text, persist as event, then run the full pipeline.

    This is the primary entry point for manual event submission.
    """
    # Persist as a new event
    normalized = NormalizedEvent(
        source_name=source_name,
        source_record_id=f"manual-{datetime.now(timezone.utc).isoformat()}",
        title=text[:120] if text else "Manual event",
        description=text[:500] if text else None,
        raw_text=text,
        event_type="OTHER",
        source_published_at=datetime.now(timezone.utc),
        data_semantic="OBSERVED" if source_name != "manual" else "SIMULATED",
        is_simulated=source_name == "manual",
    )

    outcome, event_id = await persist_event(session, normalized)
    await session.commit()

    if event_id is None:
        result = PipelineResult()
        result.errors.append(f"Event persistence failed: {outcome}")
        return result

    return await process_event_by_id(session, event_id, llm_provider)
