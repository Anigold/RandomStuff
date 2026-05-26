from __future__ import annotations

from datetime import date

from sqlalchemy import Date, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from workbot_core.infrastructure.database.base import Base, TimestampMixin


class OrderRecord(Base, TimestampMixin):
    __tablename__ = "orders"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)

    store_id: Mapped[str] = mapped_column(
        String(32),
        ForeignKey("stores.id"),
        nullable=False,
        index=True,
    )

    vendor_id: Mapped[str] = mapped_column(
        String(32),
        ForeignKey("vendors.id"),
        nullable=False,
        index=True,
    )

    order_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    delivery_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    status: Mapped[str] = mapped_column(String(32), nullable=False)

    source: Mapped[str | None] = mapped_column(String(64), nullable=True)
    source_reference: Mapped[str | None] = mapped_column(String(255), nullable=True)

    notes: Mapped[str] = mapped_column(Text, default="", nullable=False)

    lines: Mapped[list["OrderLineRecord"]] = relationship(
        "OrderLineRecord",
        back_populates="order",
        cascade="all, delete-orphan",
        passive_deletes=True,
        foreign_keys="OrderLineRecord.order_id",
    )