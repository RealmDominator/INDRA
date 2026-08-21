"""SQLAlchemy mappings for the persisted Step-6A domain/reference layer."""
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Country(Base):
    __tablename__ = "countries"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    iso3: Mapped[str | None] = mapped_column(String(3), unique=True)
    base_risk_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 3))
    region: Mapped[str | None] = mapped_column(String(50))
    is_hormuz_dependent: Mapped[bool] = mapped_column(Boolean, default=False)
    is_red_sea_dependent: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime | None] = mapped_column(DateTime)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime)


class Corridor(Base):
    __tablename__ = "corridors"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(20), unique=True)
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text)
    corridor_type: Mapped[str | None] = mapped_column(String(30))
    affected_countries: Mapped[list[str] | None] = mapped_column(ARRAY(String))
    base_risk_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 3))
    india_dependency_share: Mapped[Decimal | None] = mapped_column(Numeric(5, 3))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime)


class CrudeGrade(Base):
    __tablename__ = "crude_grades"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    api_gravity: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    sulfur_content_pct: Mapped[Decimal | None] = mapped_column(Numeric(5, 3))
    category: Mapped[str | None] = mapped_column(String(20))
    origin_country_id: Mapped[int | None] = mapped_column(ForeignKey("countries.id"))
    notes: Mapped[str | None] = mapped_column(Text)


class Supplier(Base):
    __tablename__ = "suppliers"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    country_id: Mapped[int | None] = mapped_column(ForeignKey("countries.id"))
    crude_grade_ids: Mapped[list[int] | None] = mapped_column(ARRAY(Integer))
    annual_supply_capacity_mmtpa: Mapped[Decimal | None] = mapped_column(Numeric(8, 2))
    current_sanctions_risk: Mapped[Decimal | None] = mapped_column(Numeric(5, 3))
    is_sanctioned: Mapped[bool] = mapped_column(Boolean, default=False)
    sanction_source: Mapped[str | None] = mapped_column(String(50))
    created_at: Mapped[datetime | None] = mapped_column(DateTime)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime)


class Port(Base):
    __tablename__ = "ports"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    un_locode: Mapped[str | None] = mapped_column(String(10))
    country_id: Mapped[int | None] = mapped_column(ForeignKey("countries.id"))
    is_indian: Mapped[bool] = mapped_column(Boolean, default=False)
    latitude: Mapped[Decimal | None] = mapped_column(Numeric(9, 6))
    longitude: Mapped[Decimal | None] = mapped_column(Numeric(9, 6))
    annual_crude_throughput_mmtpa: Mapped[Decimal | None] = mapped_column(Numeric(8, 2))
    current_operational_status: Mapped[str | None] = mapped_column(String(20))
    created_at: Mapped[datetime | None] = mapped_column(DateTime)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime)


class Refinery(Base):
    __tablename__ = "refineries"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    owner: Mapped[str | None] = mapped_column(String(100))
    state: Mapped[str | None] = mapped_column(String(100))
    port_id: Mapped[int | None] = mapped_column(ForeignKey("ports.id"))
    capacity_mmtpa: Mapped[Decimal | None] = mapped_column(Numeric(8, 2))
    throughput_current_mmtpa: Mapped[Decimal | None] = mapped_column(Numeric(8, 2))
    latitude: Mapped[Decimal | None] = mapped_column(Numeric(9, 6))
    longitude: Mapped[Decimal | None] = mapped_column(Numeric(9, 6))
    created_at: Mapped[datetime | None] = mapped_column(DateTime)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime)


class RefinerySupplyMix(Base):
    __tablename__ = "refinery_supply_mix"
    __table_args__ = (UniqueConstraint("refinery_id", "crude_grade_id"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    refinery_id: Mapped[int] = mapped_column(ForeignKey("refineries.id"))
    crude_grade_id: Mapped[int] = mapped_column(ForeignKey("crude_grades.id"))
    compatibility: Mapped[str] = mapped_column(String(10))
    compatibility_score: Mapped[Decimal | None] = mapped_column(Numeric(3, 2))
    current_share_pct: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    max_share_pct: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    source_type: Mapped[str | None] = mapped_column(String(30))
    notes: Mapped[str | None] = mapped_column(Text)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime)


class Route(Base):
    __tablename__ = "routes"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    origin_port_id: Mapped[int | None] = mapped_column(ForeignKey("ports.id"))
    dest_port_id: Mapped[int | None] = mapped_column(ForeignKey("ports.id"))
    corridor_ids: Mapped[list[int] | None] = mapped_column(ARRAY(Integer))
    distance_nm: Mapped[int | None] = mapped_column(Integer)
    avg_transit_days: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    base_freight_rate_per_mt: Mapped[Decimal | None] = mapped_column(Numeric(8, 2))
    current_risk_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 3))
    is_operational: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime)


class StrategicReserve(Base):
    __tablename__ = "strategic_reserves"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    location_name: Mapped[str | None] = mapped_column(String(200))
    operator: Mapped[str | None] = mapped_column(String(100))
    state: Mapped[str | None] = mapped_column(String(100))
    capacity_mmt: Mapped[Decimal | None] = mapped_column(Numeric(8, 3))
    current_level_mmt: Mapped[Decimal | None] = mapped_column(Numeric(8, 3))
    last_updated: Mapped[datetime | None] = mapped_column(DateTime)
    latitude: Mapped[Decimal | None] = mapped_column(Numeric(9, 6))
    longitude: Mapped[Decimal | None] = mapped_column(Numeric(9, 6))
    data_classification: Mapped[str | None] = mapped_column(String(20))


class DataSource(Base):
    __tablename__ = "data_sources"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    url: Mapped[str | None] = mapped_column(Text)
    update_frequency: Mapped[str | None] = mapped_column(String(50))
    last_fetched_at: Mapped[datetime | None] = mapped_column(DateTime)
    status: Mapped[str | None] = mapped_column(String(20))
    classification: Mapped[str | None] = mapped_column(String(30))


class Scenario(Base):
    __tablename__ = "scenarios"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    scenario_type: Mapped[str | None] = mapped_column(String(50))
    parameters: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_by: Mapped[str | None] = mapped_column(String(100))


class EntityAlias(Base):
    __tablename__ = "entity_aliases"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    alias: Mapped[str] = mapped_column(String(200))
    canonical_entity_type: Mapped[str] = mapped_column(String(30))
    canonical_entity_id: Mapped[int] = mapped_column(Integer)
    match_type: Mapped[str | None] = mapped_column(String(20))
    created_at: Mapped[datetime | None] = mapped_column(DateTime)
