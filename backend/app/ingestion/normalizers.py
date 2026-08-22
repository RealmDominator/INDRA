"""Shared normalization helpers."""
from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal


def parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    text = value.strip()
    try:
        if len(text) == 14 and text.isdigit():
            return datetime.strptime(text, "%Y%m%d%H%M%S").replace(tzinfo=timezone.utc)
        if len(text) == 8 and text.isdigit():
            return datetime.strptime(text, "%Y%m%d").replace(tzinfo=timezone.utc)
        normalized = text.replace("Z", "+00:00")
        if "T" in normalized or "+" in normalized:
            dt = datetime.fromisoformat(normalized)
        elif len(normalized) >= 10:
            dt = datetime.strptime(normalized[:10], "%Y-%m-%d")
        else:
            return None
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except ValueError:
        return None


def truncate_text(text: str | None, limit: int = 4000) -> str | None:
    if text is None:
        return None
    return text if len(text) <= limit else text[: limit - 3] + "..."


def to_decimal(value: float | str | Decimal) -> Decimal:
    return Decimal(str(value))
