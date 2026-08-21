"""Step-6A read-only reference/domain API."""
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Corridor, CrudeGrade, Country, Refinery, Route, StrategicReserve, Supplier
from app.repositories.domain import DomainRepository
from app.schemas.domain import CorridorResponse, CountryResponse, CrudeGradeResponse, RefineryResponse, ReservesResponse, RouteResponse, ReserveResponse, SupplierResponse
from app.services.domain import DomainService

router = APIRouter(tags=["domain"])


def service(session: AsyncSession = Depends(get_db)) -> DomainService:
    return DomainService(DomainRepository(session))


def paging(limit: int = Query(100, ge=1, le=100), offset: int = Query(0, ge=0)):
    return limit, offset


@router.get("/countries", response_model=list[CountryResponse])
async def list_countries(svc: DomainService = Depends(service), page=Depends(paging)):
    return await svc.list_resource(Country, *page)


@router.get("/corridors", response_model=list[CorridorResponse])
async def list_corridors(svc: DomainService = Depends(service), page=Depends(paging)):
    return await svc.list_resource(Corridor, *page)


@router.get("/crude-grades", response_model=list[CrudeGradeResponse])
async def list_crude_grades(svc: DomainService = Depends(service), page=Depends(paging)):
    return await svc.list_resource(CrudeGrade, *page)


@router.get("/suppliers", response_model=list[SupplierResponse])
async def list_suppliers(svc: DomainService = Depends(service), page=Depends(paging)):
    return await svc.list_resource(Supplier, *page)


@router.get("/routes", response_model=list[RouteResponse])
async def list_routes(
    corridor: str | None = Query(None),
    operational_only: bool = Query(True),
    svc: DomainService = Depends(service),
    session: AsyncSession = Depends(get_db),
    page=Depends(paging),
):
    corridor_id = None
    if corridor:
        corridor_row = await session.scalar(select(Corridor).where(Corridor.code.ilike(corridor)).limit(1))
        if corridor_row is None:
            raise HTTPException(status_code=404, detail="Unknown corridor")
        corridor_id = corridor_row.id
    return await svc.list_routes(corridor_id, operational_only, *page)


@router.get("/refineries", response_model=list[RefineryResponse])
async def list_refineries(svc: DomainService = Depends(service), session: AsyncSession = Depends(get_db), page=Depends(paging)):
    rows = await svc.list_resource(Refinery, *page)
    repo = DomainRepository(session)
    return [{**{field: getattr(row, field) for field in ("id", "name", "owner", "state", "port_id", "capacity_mmtpa", "throughput_current_mmtpa", "latitude", "longitude")}, "compatible_grades": await repo.compatible_grade_ids(row.id)} for row in rows]


@router.get("/reserves", response_model=ReservesResponse)
async def list_reserves(svc: DomainService = Depends(service)):
    # Current levels are NULL in the verified seed; no coverage is fabricated.
    return await svc.reserves(None)
