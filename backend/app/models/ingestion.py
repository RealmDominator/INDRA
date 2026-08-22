"""SQLAlchemy models for ingested business tables."""
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class GeopoliticalEvent(Base):
    __tablename__ = "geopolitical_events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    event_type: Mapped[str | None] = mapped_column(String(50))
    title: Mapped[str] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text)
    source_url: Mapped[str | None] = mapped_column(Text)
    source_name: Mapped[str | None] = mapped_column(String(100))
    affected_country_ids: Mapped[list[int] | None] = mapped_column(ARRAY(Integer))
    affected_corridor_ids: Mapped[list[int] | None] = mapped_column(ARRAY(Integer))
    affected_route_ids: Mapped[list[int] | None] = mapped_column(ARRAY(Integer))
    severity: Mapped[Decimal | None] = mapped_column(Numeric(5, 3))
    confidence: Mapped[Decimal | None] = mapped_column(Numeric(5, 3))
    occurred_at: Mapped[datetime | None] = mapped_column(DateTime)
    detected_at: Mapped[datetime | None] = mapped_column(DateTime)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    raw_text: Mapped[str | None] = mapped_column(Text)
    llm_model_used: Mapped[str | None] = mapped_column(String(100))
    is_simulated: Mapped[bool] = mapped_column(Boolean, default=False)


class CommodityPrice(Base):
    __tablename__ = "commodity_prices"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    grade_name: Mapped[str | None] = mapped_column(String(100))
    crude_grade_id: Mapped[int | None] = mapped_column(ForeignKey("crude_grades.id"))
    price_usd_per_barrel: Mapped[Decimal] = mapped_column(Numeric(10, 4))
    source: Mapped[str] = mapped_column(String(50))
    source_timestamp: Mapped[datetime | None] = mapped_column(DateTime)
    observed_at: Mapped[datetime | None] = mapped_column(DateTime)
    data_semantic: Mapped[str | None] = mapped_column(String(30))


class FxRate(Base):
    __tablename__ = "fx_rates"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    currency_pair: Mapped[str] = mapped_column(String(10))
    rate: Mapped[Decimal] = mapped_column(Numeric(10, 4))
    source: Mapped[str] = mapped_column(String(50))
    source_timestamp: Mapped[datetime | None] = mapped_column(DateTime)
    observed_at: Mapped[datetime | None] = mapped_column(DateTime)
    data_semantic: Mapped[str | None] = mapped_column(String(30))


class EvidenceRecord(Base):
    __tablename__ = "evidence_records"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    evidence_type: Mapped[str] = mapped_column(String(30))
    source_url: Mapped[str | None] = mapped_column(Text)
    source_name: Mapped[str | None] = mapped_column(String(100))
    timestamp: Mapped[datetime | None] = mapped_column(DateTime)
    related_entity_type: Mapped[str | None] = mapped_column(String(30))
    related_entity_id: Mapped[int | None] = mapped_column(Integer)
    model_or_method: Mapped[str | None] = mapped_column(String(100))
    input_summary: Mapped[dict | None] = mapped_column(JSONB)
    output_summary: Mapped[dict | None] = mapped_column(JSONB)
    data_semantic: Mapped[str | None] = mapped_column(String(30))
    confidence: Mapped[Decimal | None] = mapped_column(Numeric(5, 3))
    notes: Mapped[str | None] = mapped_column(Text)
