from ..command import Command
import argparse

from backend.app.cli.commands.command_result import CommandResult
from backend.core.utils.datetimes import convert_date_format


class DisplayVendorOrders(Command):
    name = "display_vendor_orders"

    def arguments(self):
        parser = argparse.ArgumentParser(
            prog=self.name,
            description="Display the general information for each order for a given vendor.",
        )
        parser.add_argument(
            "--vendor",
            required=True,
            help="The vendor which the orders belong.",
        )
        parser.add_argument(
            "--stores",
            required=False,
            nargs="+",
            default=self.context.get_stores(),
            help="Limit the displayed orders to these stores.",
        )
        return parser

    def autocomplete(self, flag: str, text: str):
        flags = {
            "--vendor": self.context.get_vendors,
            "--stores": self.context.get_stores,
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

            orders = self.context.workbot.get_orders_by_vendor(
                parsed_args.vendor,
                parsed_args.stores,
            )

            if not orders:
                return CommandResult.error(
                    f"No orders found for vendor '{parsed_args.vendor}'."
                )

            total_cost = sum(order.total_cost for order in orders)
            total_items = sum(len(order.items) for order in orders)
            total_cases = sum(
                sum(item.quantity for item in order.items)
                for order in orders
            )

            rows = []
            for order in orders:
                rows.append([
                    order.store,
                    self._format_date(order.date),
                    len(order.items),
                    sum(item.quantity for item in order.items),
                    f"${self._get_total_cost(order.items):,.2f}",
                ])

            return CommandResult.table(
                columns=[
                    "Store",
                    "Date (dd-mm-yyyy)",
                    "Items",
                    "Cases",
                    "Total Cost",
                ],
                rows=rows,
                target="side",
                title=f"{parsed_args.vendor} Orders",
                summary=(
                    f"Loaded {len(orders)} orders for {parsed_args.vendor}. "
                    f"Items: {total_items}, Cases: {total_cases}, "
                    f"Total Cost: ${total_cost:,.2f}"
                ),
            )

        except SystemExit:
            return CommandResult.error("Invalid arguments provided.")

    def _get_total_cost(self, items):
        total = 0
        for item in items:
            total += item.total_cost
        return total

    def _format_date(self, date_str: str) -> str:
        try:
            return convert_date_format(date_str, "%Y%m%d", "%d-%m-%Y")
        except Exception:
            return str(date_str)