"""Small SQLAlchemy data-access boundary for reference/domain resources."""
from __future__ import annotations
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Country, Corridor, CrudeGrade, DataSource, Port, Refinery, RefinerySupplyMix, Route, Scenario, StrategicReserve, Supplier


class DomainRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list(self, model, *, limit: int = 100, offset: int = 0):
        result = await self.session.scalars(select(model).order_by(model.id).offset(offset).limit(limit))
        return list(result)

    async def get(self, model, entity_id: int):
        return await self.session.get(model, entity_id)

    async def list_routes(self, *, corridor_id: int | None = None, operational_only: bool = True, limit: int = 100, offset: int = 0):
        stmt = select(Route)
        if operational_only:
            stmt = stmt.where(Route.is_operational.is_(True))
        if corridor_id is not None:
            stmt = stmt.where(Route.corridor_ids.any(corridor_id))
        result = await self.session.scalars(stmt.order_by(Route.id).offset(offset).limit(limit))
        return list(result)

    async def compatible_grade_ids(self, refinery_id: int) -> list[int]:
        result = await self.session.scalars(
            select(RefinerySupplyMix.crude_grade_id)
            .where(RefinerySupplyMix.refinery_id == refinery_id)
            .order_by(RefinerySupplyMix.crude_grade_id)
        )
        return list(result)

MODEL_BY_RESOURCE = {
    "countries": Country,
    "corridors": Corridor,
    "crude-grades": CrudeGrade,
    "ports": Port,
    "refineries": Refinery,
    "suppliers": Supplier,
    "reserves": StrategicReserve,
    "data-sources": DataSource,
    "scenarios": Scenario,
}
