from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import StrEnum

from workbot_core.domain.models.order_line import OrderLine


class OrderStatus(StrEnum):
    PENDING    = "pending"    # Raw, downloaded order
    PROCESSED  = "processed"  # Line items have been removed or added as needed
    EXPORTED   = "exported"   # Order was exported to secondary upload file format
    FULFILLED  = "fulfilled"  # Order was placed
    CANCELLED  = "cancelled"  # Order was cancelled
    ERROR      = "error"      # Unresolvable error occurred during processing


@dataclass(frozen=True, slots=True)
class Order:
    id: str

    store_id: str
    vendor_id: str

    order_date: date
    delivery_date: date | None = None

    status: OrderStatus = OrderStatus.PENDING

    source: str | None = None
    source_reference: str | None = None

    notes: str | None = None

    lines: list[OrderLine] = field(default_factory=list)

    created_at: datetime | None = None
    updated_at: datetime | None = None

    # @property
    # def line_count(self) -> int:
    #     return len(self.lines)

    # def add_line(self, line: OrderLine) -> None:
    #     if line.order_id != self.id:
    #         raise ValueError(
    #             f"OrderLine order_id '{line.order_id}' does not match Order id '{self.id}'."
    #         )

    #     self.lines.append(line)

    # def active_lines(self) -> list[OrderLine]:
    #     return [line for line in self.lines if line.is_active]

    # def mark_processed(self) -> None:
    #     self.status = OrderStatus.PROCESSED

    # def mark_fulfilled(self) -> None:
    #     self.status = OrderStatus.FULFILLED

    # def cancel(self) -> None:
    #     self.status = OrderStatus.CANCELLED