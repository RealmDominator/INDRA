"""Narrow Step-6B deterministic API surface."""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from app.intelligence import RiskWeights, StructuredEvent, calculate_risk, scenario_supply_gap, rank_procurement, build_evidence_chain
from app.database import get_db
from app.services.intelligence import resolve_structured_event
from app.models import Corridor

router = APIRouter(tags=["intelligence"])

@router.post("/events")
async def events(event: StructuredEvent, session=Depends(get_db)):
    resolution = await resolve_structured_event(session, event)
    return {"event": event, **resolution, "evidence": build_evidence_chain({"source_name": event.source_name, "source_url": event.source_url}, extraction=event.model_dump())}

@router.get("/events")
async def event_feed():
    return {"items": [], "data_semantic": "OBSERVED", "message": "No persisted events are available yet"}

@router.get("/corridors/risk")
async def corridor_risk(session=Depends(get_db)):
    rows = (await session.execute(__import__("sqlalchemy").select(Corridor).order_by(Corridor.id))).scalars().all()
    return {"items": [{"id": row.id, "code": row.code, "name": row.name, "display_score": float(row.base_risk_score or 0) * 100, "risk_level": "DERIVED", "data_semantic": "OBSERVED"} for row in rows]}


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
    return rank_procurement(request.candidates, request.target_volume, request.compatibility_threshold)
