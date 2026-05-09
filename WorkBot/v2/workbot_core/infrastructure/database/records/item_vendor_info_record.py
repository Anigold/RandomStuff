from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy import Boolean, Date, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from workbot_core.infrastructure.database.base import Base, TimestampMixin


class ItemVendorInfoRecord(Base, TimestampMixin):
    __tablename__ = "item_vendor_info"

    __table_args__ = (
        UniqueConstraint(
            "item_id",
            "vendor_id",
            "vendor_sku",
            name="uq_item_vendor_sku",
        ),
    )

    id: Mapped[str] = mapped_column(String(32), primary_key=True)

    item_id: Mapped[str] = mapped_column(
        String(32),
        ForeignKey("items.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    vendor_id: Mapped[str] = mapped_column(
        String(32),
        ForeignKey("vendors.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    vendor_sku: Mapped[str | None] = mapped_column(String(255), nullable=True)
    vendor_item_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    purchase_unit: Mapped[str | None] = mapped_column(String(64), nullable=True)
    pack_size: Mapped[Decimal | None] = mapped_column(Numeric(10, 3), nullable=True)

    price: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    last_purchase_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)