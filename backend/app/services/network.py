"""
Step-8C — Network impact analysis using NetworkX.

Given resolved corridor IDs from an event, traverses the supply graph
to find affected routes, refineries, and suppliers.
PostgreSQL remains the source of truth; NetworkX is traversal only.
"""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.graph import build_supply_graph, affected_refineries
from app.models import Corridor, Refinery, Route, Supplier
from app.models.domain import Port


async def _build_graph(session: AsyncSession):
    """Build the in-memory NetworkX graph from current DB state."""
    suppliers = (await session.execute(select(Supplier))).scalars().all()
    routes = (await session.execute(select(Route))).scalars().all()
    ports = (await session.execute(select(Port))).scalars().all()
    refineries = (await session.execute(select(Refinery))).scalars().all()
    return build_supply_graph(suppliers, routes, ports, refineries)


async def corridor_impact(
    session: AsyncSession,
    corridor_ids: list[int],
) -> dict:
    """
    For the given corridor IDs, find all affected routes, refineries, and suppliers
    using the NetworkX supply graph.

    Returns:
        {
            "affected_corridors": [...],
            "affected_routes": [...],
            "affected_refineries": [...],
            "data_semantic": "DERIVED"
        }
    """
    graph = await _build_graph(session)

    corridor_rows = (await session.execute(
        select(Corridor).where(Corridor.id.in_(corridor_ids))
    )).scalars().all()

    affected_refinery_ids = set()
    affected_route_ids = set()
    corridor_info = []

    for corridor in corridor_rows:
        # Find affected refineries via NetworkX traversal
        refinery_ids = affected_refineries(graph, corridor.id)
        affected_refinery_ids.update(refinery_ids)

        # Find affected routes (connected to this corridor)
        route_node_ids = [
            node for node in graph.successors(f"corridor:{corridor.id}")
            if node.startswith("route:")
        ]
        for rn in route_node_ids:
            affected_route_ids.add(int(rn.split(":", 1)[1]))

        corridor_info.append({
            "id": corridor.id,
            "code": corridor.code,
            "name": corridor.name,
            "affected_route_count": len(route_node_ids),
            "affected_refinery_count": len(refinery_ids),
        })

    # Fetch full details for affected entities
    refinery_details = []
    if affected_refinery_ids:
        rows = (await session.execute(
            select(Refinery).where(Refinery.id.in_(affected_refinery_ids))
        )).scalars().all()
        refinery_details = [
            {
                "id": r.id,
                "name": r.name,
                "owner": r.owner,
                "state": r.state,
                "capacity_mmtpa": float(r.capacity_mmtpa) if r.capacity_mmtpa else None,
            }
            for r in rows
        ]

    route_details = []
    if affected_route_ids:
        rows = (await session.execute(
            select(Route).where(Route.id.in_(affected_route_ids))
        )).scalars().all()
        route_details = [
            {
                "id": r.id,
                "name": r.name,
                "is_operational": r.is_operational,
                    "transit_days": float(r.avg_transit_days) if r.avg_transit_days is not None else None,
            }
            for r in rows
        ]

    return {
        "affected_corridors": corridor_info,
        "affected_routes": route_details,
        "affected_refineries": refinery_details,
        "data_semantic": "DERIVED",
    }
