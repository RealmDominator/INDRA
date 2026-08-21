"""Exact-alias-first and RapidFuzz fallback entity resolution."""
from rapidfuzz import fuzz, process
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import get_settings
from app.models import Country, Corridor, CrudeGrade, EntityAlias, Port, Refinery, Supplier


class ResolutionResult:
    def __init__(self, entity_type, input_value, entity_id=None, canonical_name=None, match_type=None, confidence=None):
        self.entity_type, self.input_value = entity_type, input_value
        self.entity_id, self.canonical_name = entity_id, canonical_name
        self.match_type, self.confidence = match_type, confidence

    @property
    def resolved(self):
        return self.entity_id is not None


ENTITY_MODELS = {"country": Country, "corridor": Corridor, "crude_grade": CrudeGrade, "port": Port, "refinery": Refinery, "supplier": Supplier}


async def resolve_entity(session: AsyncSession, entity_type: str, value: str, threshold: int | None = None) -> ResolutionResult:
    if entity_type not in ENTITY_MODELS:
        return ResolutionResult(entity_type, value)
    threshold = threshold if threshold is not None else get_settings().entity_resolution_threshold
    normalized = value.strip()
    alias = await session.scalar(select(EntityAlias).where(EntityAlias.canonical_entity_type == entity_type, EntityAlias.alias.ilike(normalized)))
    if alias:
        return ResolutionResult(entity_type, value, alias.canonical_entity_id, normalized, "EXACT", 100.0)
    model = ENTITY_MODELS[entity_type]
    field = model.code if entity_type == "corridor" else model.name
    direct = await session.scalar(select(model).where(field.ilike(normalized)))
    if direct:
        return ResolutionResult(entity_type, value, direct.id, getattr(direct, "name", getattr(direct, "code", normalized)), "EXACT", 100.0)
    aliases = list((await session.scalars(select(EntityAlias).where(EntityAlias.canonical_entity_type == entity_type))).all())
    alias_choices = {row.alias: row for row in aliases}
    alias_match = process.extractOne(normalized, alias_choices.keys(), scorer=fuzz.ratio) if alias_choices else None
    if alias_match and alias_match[1] >= threshold:
        alias_row = alias_choices[alias_match[0]]
        return ResolutionResult(entity_type, value, alias_row.canonical_entity_id, alias_match[0], "FUZZY", float(alias_match[1]))
    rows = list((await session.scalars(select(model))).all())
    choices = {getattr(row, "name", getattr(row, "code", "")): row for row in rows}
    # Human-facing short names (for example "Red Sea") should resolve to
    # canonical descriptive names ("Red Sea / Bab el-Mandeb") without
    # weakening the configured fuzzy threshold globally.
    normalized_lower = normalized.casefold()
    for canonical, row in choices.items():
        if normalized_lower in canonical.casefold() or canonical.casefold() in normalized_lower:
            return ResolutionResult(entity_type, value, row.id, canonical, "CONTAINS", 95.0)
    match = process.extractOne(normalized, choices.keys(), scorer=fuzz.ratio)
    if match and match[1] >= threshold:
        row = choices[match[0]]
        return ResolutionResult(entity_type, value, row.id, match[0], "FUZZY", float(match[1]))
    return ResolutionResult(entity_type, value)
