from ..command import Command
import argparse
from tabulate import tabulate

from backend.app.cli.commands.command_result import CommandResult
from backend.core.utils.datetimes import convert_date_format


class DisplayOrder(Command):
    name = "display_order"

    def arguments(self):
        parser = argparse.ArgumentParser(
            prog=self.name,
            description="Display the general information for a single order.",
        )
        parser.add_argument(
            "--vendor",
            required=True,
            help="The vendor to which the order belongs.",
        )
        parser.add_argument(
            "--store",
            required=True,
            help="The store to which the order belongs.",
        )
        return parser

    def autocomplete(self, flag: str, text: str):
        flags = {
            "--vendor": self.context.get_vendors,
            "--store": self.context.get_stores,
        }

        return [
            option
            for option in flags.get(flag, [])()
            if option.startswith(text)
        ]

    def command(self, args):
        try:
            parser = self.arguments()
            parsed_args = parser.parse_args(args)

            orders = self.context.workbot.get_orders(
                stores=[parsed_args.store],
                vendors=[parsed_args.vendor],
            )

            if not orders:
                return CommandResult(
                    kind="error",
                    payload="No order found.",
                    target="console",
                )

            order = orders[0]

            if not order.items:
                return CommandResult(
                    kind="text",
                    payload=self._format_order_summary(order),
                    target="side",
                    title="Order Summary",
                    summary="Order found, but no items were present.",
                )

            detail_text = self._format_order_detail(order)

            return CommandResult(
                kind="text",
                payload=detail_text,
                target="side",
                title=f"Order: {order.store} / {order.vendor}",
                summary=(
                    f"Loaded order for {order.store} / {order.vendor} "
                    f"with {len(order.items)} items."
                ),
            )

        except SystemExit:
            return CommandResult(
                kind="error",
                payload="Invalid arguments provided.",
                target="console",
            )

    def _format_order_detail(self, order) -> str:
        order_total = sum(item.total_cost for item in order.items)
        total_cases = sum(item.quantity for item in order.items)

        summary_lines = [
            "ORDER SUMMARY",
            "-------------",
            f"Vendor:      {order.vendor}",
            f"Store:       {order.store}",
        ]

        if getattr(order, "date", None):
            summary_lines.append(
                f"Date:        {self._format_date(order.date)}"
            )

        summary_lines.extend(
            [
                "",
                f"Order Total: ${order_total:,.2f}",
                f"Total Cases: {total_cases}",
                "",
            ]
        )

        rows = []
        for pos, item in enumerate(order.items, start=1):
            rows.append([
                pos,
                item.sku,
                item.name,
                item.quantity,
                item.cost_per,
                item.total_cost,
            ])

        headers = ["#", "SKU", "Item Name", "Qty", "Cost Per ($)", "Total ($)"]
        table = tabulate(
            rows,
            headers=headers,
            tablefmt="github",
            floatfmt=",.2f",
        )

        return "\n".join(summary_lines) + table

    def _format_order_summary(self, order) -> str:
        order_total = sum(item.total_cost for item in order.items) if order.items else 0
        total_cases = sum(item.quantity for item in order.items) if order.items else 0

        lines = [
            "ORDER SUMMARY",
            "-------------",
            f"Vendor:      {order.vendor}",
            f"Store:       {order.store}",
        ]

        if getattr(order, "date", None):
            lines.append(f"Date:        {self._format_date(order.date)}")

        lines.extend(
            [
                "",
                f"Order Total: ${order_total:,.2f}",
                f"Total Cases: {total_cases}",
            ]
        )

        return "\n".join(lines)

    def _format_date(self, date_str: str) -> str:
        try:
            return convert_date_format(date_str, "%Y%m%d", "%d-%m-%Y")
        except Exception:
            return str(date_str)

    def _format_order_items_table(self, order_items: list):
        headers = ["Store", "Date (dd-mm-yyyy)", "Items", "Total Cost"]
        rows = []

        for o in order_items:
            rows.append([
                o.store,
                convert_date_format(o.date, "%Y%m%d", "%d-%m-%Y"),
                len(o.items),
                f"${self._get_total_cost(o.items):,.02f}",
            ])

        return tabulate(rows, headers=headers, tablefmt="github")