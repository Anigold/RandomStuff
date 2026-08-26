from ..command import Command
import argparse

from backend.app.cli.commands.command_result import CommandResult
from backend.core.utils.datetimes import convert_date_format


class DisplayStoreOrders(Command):
    name = "display_store_orders"

    def arguments(self):
        parser = argparse.ArgumentParser(
            prog=self.name,
            description="Display the general information for the orders for a given store.",
        )
        parser.add_argument(
            "--store",
            required=True,
            help="The store which the orders belong.",
        )
        parser.add_argument(
            "--vendors",
            required=False,
            nargs="+",
            default=self.context.get_vendors(),
            help="Limit the displayed orders to these vendors.",
        )
        return parser

    def autocomplete(self, flag: str, text: str):
        flags = {
            "--vendors": self.context.get_vendors,
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

            orders = self.context.workbot.get_orders_by_store(
                parsed_args.store,
                parsed_args.vendors,
            )

            if not orders:
                return CommandResult.error(
                    f"No orders found for store '{parsed_args.store}'."
                )

            rows = []
            total_cost = 0.0
            total_items = 0
            total_cases = 0

            for order in orders:
                item_count = len(order.items)
                case_count = sum(item.quantity for item in order.items)
                order_total = self._get_total_cost(order.items)

                total_items += item_count
                total_cases += case_count
                total_cost += order_total

                rows.append([
                    order.vendor,
                    self._format_date(order.date),
                    item_count,
                    case_count,
                    f"${order_total:,.2f}",
                ])

            vendor_count = len({order.vendor for order in orders})

            return CommandResult.table(
                columns=[
                    "Vendor",
                    "Date (dd-mm-yyyy)",
                    "Items",
                    "Cases",
                    "Total Cost",
                ],
                rows=rows,
                target="side",
                title=f"{parsed_args.store} Orders",
                summary=(
                    f"Loaded {len(orders)} orders for {parsed_args.store} "
                    f"across {vendor_count} vendors. "
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