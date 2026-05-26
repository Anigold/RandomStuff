from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP

from workbot_core.domain.models.order_line import OrderLine


MONEY_QUANT = Decimal("0.01")


class OrderLineCalculator:
    def line_total(self, line: OrderLine) -> Decimal | None:
        if line.unit_price_snapshot is None:
            return None

        return self.round_money(line.quantity * line.unit_price_snapshot)

    def round_money(self, value: Decimal) -> Decimal:
        return value.quantize(MONEY_QUANT, rounding=ROUND_HALF_UP)