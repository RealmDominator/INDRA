"""Domain services keep route handlers free of data-access logic."""
from decimal import Decimal

from app.repositories.domain import DomainRepository


class DomainService:
    def __init__(self, repository: DomainRepository):
        self.repository = repository

    async def list_resource(self, model, limit: int, offset: int):
        return await self.repository.list(model, limit=limit, offset=offset)

    async def list_routes(self, corridor_id: int | None, operational_only: bool, limit: int, offset: int):
        return await self.repository.list_routes(corridor_id=corridor_id, operational_only=operational_only, limit=limit, offset=offset)

    async def reserves(self, daily_consumption_mmt: Decimal | None):
        from app.models import StrategicReserve
        rows = await self.repository.list(StrategicReserve, limit=100, offset=0)
        total_capacity = sum((row.capacity_mmt or Decimal("0") for row in rows), Decimal("0"))
        current_values = [row.current_level_mmt for row in rows]
        total_current = sum(current_values, Decimal("0")) if all(value is not None for value in current_values) else None
        locations = []
        for row in rows:
            coverage = (row.current_level_mmt / daily_consumption_mmt if row.current_level_mmt is not None and daily_consumption_mmt else None)
            locations.append({**{column: getattr(row, column) for column in ("id", "location_name", "operator", "state", "capacity_mmt", "current_level_mmt", "latitude", "longitude", "data_classification")}, "days_coverage": coverage})
        total_coverage = total_current / daily_consumption_mmt if total_current is not None and daily_consumption_mmt else None
        return {"locations": locations, "total_capacity_mmt": total_capacity, "total_current_mmt": total_current, "total_days_coverage": total_coverage, "daily_consumption_mmt_used": daily_consumption_mmt}
