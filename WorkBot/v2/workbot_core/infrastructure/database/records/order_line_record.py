from __future__ import annotations

from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from workbot_core.infrastructure.database.base import Base, TimestampMixin


class OrderLineRecord(Base, TimestampMixin):
    __tablename__ = "order_lines"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)

    order_id: Mapped[str] = mapped_column(
        String(32),
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    item_id: Mapped[str | None] = mapped_column(
        String(32),
        ForeignKey("items.id"),
        nullable=True,
        index=True,
    )

    item_vendor_info_id: Mapped[str | None] = mapped_column(
        String(32),
        ForeignKey("item_vendor_info.id"),
        nullable=True,
        index=True,
    )

    source_item_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source_vendor_sku: Mapped[str | None] = mapped_column(String(255), nullable=True)
    
    item_name_snapshot: Mapped[str | None] = mapped_column(String(255), nullable=True)
    vendor_sku_snapshot: Mapped[str | None] = mapped_column(String(255), nullable=True)
    unit_price_snapshot: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2),
        nullable=True,
    )

    quantity: Mapped[Decimal] = mapped_column(Numeric(10, 3), nullable=False)
    unit: Mapped[str | None] = mapped_column(String(64), nullable=True)

    status: Mapped[str] = mapped_column(String(32), nullable=False)
    status_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    moved_to_order_id: Mapped[str | None] = mapped_column(
        String(32),
        ForeignKey("orders.id"),
        nullable=True,
        index=True,
    )

    notes: Mapped[str] = mapped_column(Text, default="", nullable=False)

    order: Mapped["OrderRecord"] = relationship(
        "OrderRecord",
        foreign_keys=[order_id],
        back_populates="lines",
    )