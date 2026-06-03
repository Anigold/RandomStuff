from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import DateTime, Integer, JSON, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from workbot_core.infrastructure.database.base import Base


class VendorRecord(Base):
    __tablename__ = "vendors"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    order_format: Mapped[str] = mapped_column(String, default="", nullable=False)
    special_notes: Mapped[str] = mapped_column(Text, default="", nullable=False)

    min_order_value: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        default=Decimal("0"),
        nullable=False,
    )
    min_order_cases: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    internal_contacts_json: Mapped[list[dict[str, str]]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )
    ordering_json: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
    )
    store_references_json: Mapped[list[dict[str, str]]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )

    created_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )