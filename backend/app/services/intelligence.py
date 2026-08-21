"""Step-6B orchestration helpers joining extraction output to Step-6A resolution."""
from app.intelligence import StructuredEvent
from app.services.entity_resolution import resolve_entity


async def resolve_structured_event(session, event: StructuredEvent) -> dict:
    resolved = {"countries": [], "corridors": [], "routes": []}
    unresolved = {"countries": [], "corridors": [], "routes": []}
    plural = {"country": "countries", "corridor": "corridors", "route": "routes"}
    for kind, names in (("country", event.country_names), ("corridor", event.corridor_names), ("route", event.route_names)):
        for name in names:
            result = await resolve_entity(session, kind, name)
            if result.resolved:
                resolved[plural[kind]].append({"name": name, "id": result.entity_id, "confidence": result.confidence})
            else:
                unresolved[plural[kind]].append(name)
    return {"resolved": resolved, "unresolved": unresolved}
