"""Step-8C intelligence API: deterministic engines + LLM extraction + full pipeline."""
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.intelligence import (
    RiskWeights, StructuredEvent, calculate_risk, classify_risk,
    scenario_supply_gap, rank_procurement, optimize_procurement, build_evidence_chain,
    UnconfiguredLLMProvider,
)
from app.database import get_db
from app.services.intelligence import resolve_structured_event
from app.services.pipeline import PipelineResult, process_event_by_id, ingest_and_process
from app.services.risk import recalculate_all_corridor_risks
from app.services.network import corridor_impact
from app.models import Corridor
from app.models.ingestion import GeopoliticalEvent

router = APIRouter(tags=["intelligence"])


# ---------------------------------------------------------------------------
# Event endpoints
# ---------------------------------------------------------------------------

@router.post("/events")
async def events(event: StructuredEvent, session=Depends(get_db)):
    resolution = await resolve_structured_event(session, event)
    return {"event": event, **resolution, "evidence": build_evidence_chain({"source_name": event.source_name, "source_url": event.source_url}, extraction=event.model_dump())}


@router.get("/events")
async def event_feed(session=Depends(get_db), limit: int = 50):
    rows = (await session.execute(
        select(GeopoliticalEvent).order_by(GeopoliticalEvent.detected_at.desc()).limit(limit)
    )).scalars().all()
    items = [
        {
            "id": row.id,
            "title": row.title,
            "event_type": row.event_type,
            "severity": float(row.severity) if row.severity else None,
            "confidence": float(row.confidence) if row.confidence else None,
            "source_name": row.source_name,
            "source_url": row.source_url,
            "occurred_at": row.occurred_at.isoformat() if row.occurred_at else None,
            "detected_at": row.detected_at.isoformat() if row.detected_at else None,
            "data_semantic": "OBSERVED" if not row.is_simulated else "SIMULATED",
            "has_raw_text": bool(row.raw_text),
            "llm_model_used": row.llm_model_used,
        }
        for row in rows
    ]
    return {
        "items": items,
        "data_semantic": "OBSERVED",
        "message": "Persisted ingested events" if items else "No persisted events are available yet",
    }


# ---------------------------------------------------------------------------
# Corridor risk
# ---------------------------------------------------------------------------

@router.get("/corridors/risk")
async def corridor_risk(session=Depends(get_db)):
    rows = (await session.execute(select(Corridor).order_by(Corridor.id))).scalars().all()
    return {"items": [{"id": row.id, "code": row.code, "name": row.name, "display_score": float(row.base_risk_score or 0) * 100, "risk_level": classify_risk(float(row.base_risk_score or 0)), "data_semantic": "OBSERVED"} for row in rows]}


@router.get("/corridors/risk/live")
async def corridor_risk_live(session=Depends(get_db)):
    """Recalculate corridor risk from recent events (event-driven risk)."""
    results = await recalculate_all_corridor_risks(session)
    return {
        "items": [
            {
                "corridor_id": r["corridor_id"],
                "corridor_code": r["corridor_code"],
                "corridor_name": r["corridor_name"],
                "display_score": r["risk"].display_score,
                "risk_level": r["risk"].risk_level,
                "components": r["risk"].components,
                "data_semantic": "DERIVED",
            }
            for r in results
        ],
        "data_semantic": "DERIVED",
    }


# ---------------------------------------------------------------------------
# Network impact
# ---------------------------------------------------------------------------

@router.get("/corridors/{corridor_id}/impact")
async def corridor_network_impact(corridor_id: int, session=Depends(get_db)):
    """Find affected routes and refineries for a corridor via NetworkX traversal."""
    corridor = await session.get(Corridor, corridor_id)
    if corridor is None:
        raise HTTPException(status_code=404, detail="Corridor not found")
    try:
        impact = await corridor_impact(session, [corridor_id])
        return impact
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Network impact analysis failed: {exc}") from exc


# ---------------------------------------------------------------------------
# Request/response models
# ---------------------------------------------------------------------------

class RiskRequest(BaseModel):
    features: dict[str, float]
    weights: RiskWeights | None = None


class ScenarioRequest(BaseModel):
    scenario_type: str
    duration_days: int = Field(ge=0, le=365)
    reduction_pct: float = Field(default=100, ge=0, le=100)


class RecommendationRequest(BaseModel):
    target_volume: float = Field(gt=0)
    candidates: list[dict]
    compatibility_threshold: float = Field(default=0.5, ge=0, le=1)
    max_transit_days: float | None = Field(default=None, ge=0)
    risk_aversion: float = Field(default=0.5, ge=0)
    transit_penalty_per_day: float = Field(default=0.01, ge=0)


class ExtractionRequest(BaseModel):
    text: str = Field(min_length=20, description="Article text to extract event from")


class ProcessRequest(BaseModel):
    event_id: int


class IngestRequest(BaseModel):
    text: str = Field(min_length=20, description="Article text to ingest and process")
    source_name: str = Field(default="manual", description="Source name for provenance")


# ---------------------------------------------------------------------------
# Deterministic engine endpoints (unchanged from Step 6B)
# ---------------------------------------------------------------------------

@router.post("/risk")
async def risk(request: RiskRequest):
    return calculate_risk(request.features, request.weights)


@router.get("/risk")
async def risk_summary():
    return {"status": "ready", "message": "Submit feature vectors to POST /risk", "data_semantic": "DERIVED"}


@router.post("/scenarios")
async def scenarios(request: ScenarioRequest):
    try:
        return scenario_supply_gap(request.scenario_type, request.duration_days, request.reduction_pct)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/recommendations")
async def recommendations(request: RecommendationRequest):
    return optimize_procurement(
        request.candidates,
        request.target_volume,
        request.compatibility_threshold,
        request.max_transit_days,
        request.risk_aversion,
        request.transit_penalty_per_day,
    )


# ---------------------------------------------------------------------------
# Step 8A — LLM extraction endpoint
# ---------------------------------------------------------------------------

@router.post("/events/extract")
async def extract_event(request: ExtractionRequest, req: Request, session: AsyncSession = Depends(get_db)):
    """
    Article text → LLM extraction → validation → entity resolution → persistence → evidence.

    Requires a configured LLM provider (OPENROUTER_API_KEY in environment).
    Returns 503 if no provider is configured.
    """
    provider = getattr(req.app.state, "llm_provider", None)
    if provider is None or isinstance(provider, UnconfiguredLLMProvider):
        raise HTTPException(
            status_code=503,
            detail="No LLM provider is configured. Set OPENROUTER_API_KEY in your environment.",
        )

    try:
        result = await provider.extract_event(request.text)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=f"Extraction failed: {exc}") from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=f"Provider error: {exc}") from exc

    resolution = await resolve_structured_event(session, result.event)

    return {
        "event": result.event,
        "provider_metadata": result.metadata,
        **resolution,
        "evidence": build_evidence_chain(
            {"source_text_length": len(request.text), "data_semantic": "OBSERVED"},
            extraction={**result.event.model_dump(), "data_semantic": "DERIVED"},
            entity_resolution={"data_semantic": "DERIVED", **resolution},
        ),
    }


# ---------------------------------------------------------------------------
# Step 8C — Full pipeline endpoints
# ---------------------------------------------------------------------------

@router.post("/events/process")
async def process_event(request: ProcessRequest, req: Request, session: AsyncSession = Depends(get_db)):
    """
    Process an existing event through the full pipeline:
    Event → Extraction → Entity Resolution → Risk → Network → Scenario → Procurement → Evidence
    """
    provider = getattr(req.app.state, "llm_provider", None)
    try:
        result = await process_event_by_id(session, request.event_id, llm_provider=provider)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Pipeline error: {exc}") from exc
    return result


@router.post("/events/ingest-and-process")
async def ingest_and_process_event(request: IngestRequest, req: Request, session: AsyncSession = Depends(get_db)):
    """
    Accept raw text → persist as event → run full pipeline.
    This is the primary entry point for manual event submission from the dashboard.
    """
    provider = getattr(req.app.state, "llm_provider", None)
    try:
        result = await ingest_and_process(session, request.text, request.source_name, llm_provider=provider)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Pipeline error: {exc}") from exc
    return result
