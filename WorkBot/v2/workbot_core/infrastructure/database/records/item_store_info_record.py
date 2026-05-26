from __future__ import annotations

from decimal import Decimal

from sqlalchemy import Boolean, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from workbot_core.infrastructure.database.base import Base, TimestampMixin


class ItemStoreInfoRecord(Base, TimestampMixin):
    __tablename__ = "item_store_info"

    __table_args__ = (
        UniqueConstraint(
            "item_id",
            "store_id",
            name="uq_item_store",
        ),
    )

    id: Mapped[str] = mapped_column(String(32), primary_key=True)

    item_id: Mapped[str] = mapped_column(
        String(32),
        ForeignKey("items.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    store_id: Mapped[str] = mapped_column(
        String(32),
        ForeignKey("stores.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    count_unit: Mapped[str | None] = mapped_column(String(64), nullable=True)
    par: Mapped[Decimal | None] = mapped_column(Numeric(10, 3), nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)