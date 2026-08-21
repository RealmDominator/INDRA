"""API response schemas for the Step-6A reference/domain resources."""
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class CountryResponse(ORMModel):
    id: int
    name: str
    iso3: str | None = None
    base_risk_score: Decimal | None = None
    region: str | None = None
    is_hormuz_dependent: bool = False
    is_red_sea_dependent: bool = False


class CorridorResponse(ORMModel):
    id: int
    code: str
    name: str
    description: str | None = None
    corridor_type: str | None = None
    affected_countries: list[str] | None = None
    base_risk_score: Decimal | None = None
    india_dependency_share: Decimal | None = None
    is_active: bool = True


class CrudeGradeResponse(ORMModel):
    id: int
    name: str
    api_gravity: Decimal | None = None
    sulfur_content_pct: Decimal | None = None
    category: str | None = None
    origin_country_id: int | None = None
    notes: str | None = None


class SupplierResponse(ORMModel):
    id: int
    name: str
    country_id: int | None = None
    crude_grade_ids: list[int] | None = None
    annual_supply_capacity_mmtpa: Decimal | None = None
    current_sanctions_risk: Decimal | None = None
    is_sanctioned: bool = False
    sanction_source: str | None = None


class PortSummary(BaseModel):
    id: int
    name: str
    latitude: Decimal | None = None
    longitude: Decimal | None = None


class RouteResponse(ORMModel):
    id: int
    name: str
    origin_port_id: int | None = None
    dest_port_id: int | None = None
    corridor_ids: list[int] | None = None
    distance_nm: int | None = None
    avg_transit_days: Decimal | None = None
    current_risk_score: Decimal | None = Field(default=None, description="Internal 0.0-1.0 score")
    is_operational: bool = True


class RefineryResponse(ORMModel):
    id: int
    name: str
    owner: str | None = None
    state: str | None = None
    port_id: int | None = None
    capacity_mmtpa: Decimal | None = None
    throughput_current_mmtpa: Decimal | None = None
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    compatible_grades: list[int] = []


class ReserveResponse(ORMModel):
    id: int
    location_name: str | None = None
    operator: str | None = None
    state: str | None = None
    capacity_mmt: Decimal | None = None
    current_level_mmt: Decimal | None = None
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    data_classification: str | None = None
    days_coverage: Decimal | None = None


class ReservesResponse(BaseModel):
    locations: list[ReserveResponse]
    total_capacity_mmt: Decimal
    total_current_mmt: Decimal | None
    total_days_coverage: Decimal | None
    daily_consumption_mmt_used: Decimal | None


class ScenarioResponse(ORMModel):
    id: int
    name: str
    scenario_type: str | None = None
    parameters: dict[str, Any] | None = None


class EntityResolutionResponse(BaseModel):
    entity_type: str
    input_value: str
    resolved: bool
    entity_id: int | None = None
    canonical_name: str | None = None
    match_type: str | None = None
    confidence: float | None = None
