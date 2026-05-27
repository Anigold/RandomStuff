from __future__ import annotations

from decimal import Decimal

from sqlalchemy import Boolean, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from workbot_core.infrastructure.database.base import Base, TimestampMixin


class ItemRecord(Base, TimestampMixin):
    __tablename__ = "items"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)

    name: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )

    category: Mapped[str | None] = mapped_column(String(255), nullable=True)
    subcategory: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Legacy: will be phased out
    count_unit: Mapped[str | None] = mapped_column(String(64), nullable=True)

    count_unit_quantity: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 3),
        nullable=True,
    )

    count_unit_measure: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )

    custom_each_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    each_quantity: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 3),
        nullable=True,
    )

    each_measure: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )

    weight_quantity: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 3),
        nullable=True,
    )

    weight_measure: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )

    volume_quantity: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 3),
        nullable=True,
    )

    volume_measure: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )