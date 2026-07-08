from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from workbot_core.infrastructure.database.base import Base


class InventoryCountRecord(Base):
    __tablename__ = "inventory_counts"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    store_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("stores.id"),
        nullable=False,
        index=True,
    )
    count_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    lines: Mapped[list[InventoryCountLineRecord]] = relationship(
        "InventoryCountLineRecord",
        back_populates="count",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class InventoryCountLineRecord(Base):
    __tablename__ = "inventory_count_lines"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    inventory_count_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("inventory_counts.id"),
        nullable=False,
        index=True,
    )
    item_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("items.id"),
        nullable=False,
        index=True,
    )
    quantity: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    unit: Mapped[str] = mapped_column(String, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    count: Mapped[InventoryCountRecord] = relationship(
        "InventoryCountRecord",
        back_populates="lines",
    )