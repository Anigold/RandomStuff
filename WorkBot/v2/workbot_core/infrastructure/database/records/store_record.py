# workbot_core/infrastructure/database/records/store_record.py

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from workbot_core.infrastructure.database.base import Base


class StoreRecord(Base):
    __tablename__ = "stores"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    general_manager: Mapped[str | None] = mapped_column(String, nullable=True)
    inventory_clerk: Mapped[str | None] = mapped_column(String, nullable=True)

    address: Mapped[str | None] = mapped_column(String, nullable=True)
    phone_number: Mapped[str | None] = mapped_column(String, nullable=True)
    special_notes: Mapped[str] = mapped_column(String, default="", nullable=False)

    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)