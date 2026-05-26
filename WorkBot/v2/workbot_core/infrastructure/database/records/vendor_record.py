from __future__ import annotations

from decimal import Decimal

from sqlalchemy import Boolean, Integer, JSON, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from workbot_core.infrastructure.database.base import Base, TimestampMixin


class VendorRecord(Base, TimestampMixin):
    __tablename__ = "vendors"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)

    name: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    order_format: Mapped[str] = mapped_column(
        String(64),
        default="",
        nullable=False,
    )

    special_notes: Mapped[str] = mapped_column(
        Text,
        default="",
        nullable=False,
    )

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

    internal_contacts_json: Mapped[list[dict]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )

    ordering_json: Mapped[dict] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
    )

    store_ids_json: Mapped[list[str]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )