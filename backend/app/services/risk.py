"""
Step-8C — Corridor risk recalculation from persisted events.

Uses the frozen Phase-1 deterministic formula. The LLM never touches risk.
"""
from __future__ import annotations

import math
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.intelligence import RiskWeights, RiskResult, calculate_risk, classify_risk
from app.models import Corridor
from app.models.ingestion import GeopoliticalEvent


def _recency_score(occurred_at: datetime | None, now: datetime | None = None) -> float:
    """Decay recency: 1.0 if today, 0.0 after 30 days.  Internal 0.0–1.0."""
    if occurred_at is None:
        return 0.0
    now = now or datetime.now(timezone.utc)
    naive_now = now.replace(tzinfo=None) if now.tzinfo else now
    naive_occ = occurred_at.replace(tzinfo=None) if occurred_at.tzinfo else occurred_at
    age_days = max(0, (naive_now - naive_occ).total_seconds() / 86400)
    return max(0.0, 1.0 - age_days / 30.0)


async def corridor_risk_from_events(
    session: AsyncSession,
    corridor_id: int,
    window_days: int = 30,
    weights: RiskWeights | None = None,
) -> RiskResult:
    """
    Recalculate risk for a corridor using persisted events + seed baseline.

    Features used (all 0.0–1.0):
      event_severity   — max severity of recent events affecting this corridor
      event_recency    — recency decay of most recent event
      chokepoint_exposure — from corridor seed (base_risk_score)
      conflict_sanctions — 0.0 (no live sanctions integration yet)
      historical_rate  — from corridor seed (base_risk_score * 0.5 as proxy)
      india_dependency — from corridor seed (india_dependency_share)
    """
    corridor = await session.get(Corridor, corridor_id)
    if corridor is None:
        raise ValueError(f"Corridor {corridor_id} not found")

    # Query recent events that affect this corridor
    from sqlalchemy import or_, cast
    from sqlalchemy.dialects.postgresql import ARRAY as PG_ARRAY, array

    cutoff = datetime.now(timezone.utc).replace(tzinfo=None)
    cutoff_start = cutoff - __import__("datetime").timedelta(days=window_days)

    # Events where affected_corridor_ids contains this corridor_id
    # or events that have no corridor assignment yet (we'll match by title later if needed)
    stmt = (
        select(GeopoliticalEvent)
        .where(
            GeopoliticalEvent.affected_corridor_ids.any(corridor_id),
            GeopoliticalEvent.detected_at >= cutoff_start,
        )
        .order_by(GeopoliticalEvent.detected_at.desc())
        .limit(50)
    )
    events = (await session.execute(stmt)).scalars().all()

    # Feature extraction
    base_risk = float(corridor.base_risk_score or 0)
    india_dep = float(getattr(corridor, "india_dependency_share", 0) or 0)

    if events:
        max_severity = max(float(e.severity or 0) / 10.0 for e in events)
        most_recent = events[0]
        recency = _recency_score(most_recent.occurred_at or most_recent.detected_at)
    else:
        max_severity = 0.0
        recency = 0.0

    features = {
        "event_severity": min(1.0, max_severity),
        "event_recency": recency,
        "chokepoint_exposure": base_risk,
        "conflict_sanctions": 0.0,       # no live sanctions scoring yet
        "historical_rate": base_risk * 0.5,  # proxy from seed baseline
        "india_dependency": india_dep,
    }

    return calculate_risk(features, weights)


async def recalculate_all_corridor_risks(
    session: AsyncSession,
    weights: RiskWeights | None = None,
) -> list[dict]:
    """Recalculate risk for all corridors. Returns list of {corridor, risk}."""
    corridors = (await session.execute(
        select(Corridor).order_by(Corridor.id)
    )).scalars().all()

    results = []
    for c in corridors:
        risk = await corridor_risk_from_events(session, c.id, weights=weights)
        results.append({
            "corridor_id": c.id,
            "corridor_code": c.code,
            "corridor_name": c.name,
            "risk": risk,
        })
    return results
