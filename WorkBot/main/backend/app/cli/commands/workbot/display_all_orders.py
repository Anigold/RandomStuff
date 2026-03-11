from ..command import Command
import argparse
from tabulate import tabulate
from collections import defaultdict
from backend.core.utils.datetimes import convert_date_format


class DisplayAllOrders(Command):

    name = 'display_all_orders'

    def arguments(self):
        parser = argparse.ArgumentParser(
            prog=self.name,
            description='Display general information for all current orders.'
        )
        parser.add_argument(
            '--stores',
            nargs='+',
            default=self.context.get_stores(),
            help='Store(s) whose orders should be displayed.'
        )
        parser.add_argument(
            '--vendors',
            nargs='+',
            default=self.context.get_vendors(),
            help='Limit displayed orders to these vendors.'
        )
        parser.add_argument(
            '--sort_by',
            choices=['store', 'vendor'],
            default='store',
            help='Group orders by store or vendor.'
        )
        return parser

    def autocomplete(self, flag: str, text: str):
        flags = {
            '--vendors': self.context.get_vendors,
            '--stores': self.context.get_stores,
            '--sort_by': lambda: ['store', 'vendor'],
        }
        return [opt for opt in flags.get(flag, lambda: [])() if opt.startswith(text)]

    def command(self, args):
        try:
            parser = self.arguments()
            parsed = parser.parse_args(args)

            # Fetch all matching orders
            orders = self.context.workbot.get_orders(
                stores=parsed.stores,
                vendors=parsed.vendors
            )

            if not orders:
                print("\nNo orders found.\n")
                return

            grouped = self._group_orders(orders, parsed.sort_by)

            for group_key, group_orders in grouped.items():
                print("\n" + "=" * len(group_key))
                print(group_key)
                print("=" * len(group_key))
                print(self._format_orders_table(group_orders))

                total_cost = sum(o.total_cost for o in group_orders)
                total_cases = sum(
                    sum(item.quantity for item in o.items) for o in group_orders
                )

                print(f"\nTotal Cases: {total_cases:,.2f}")
                print(f"Total Cost:  ${total_cost:,.2f}\n")

        except SystemExit:
            pass

    # -------------------------
    # Helpers
    # -------------------------

    def _group_orders(self, orders, sort_by):
        grouped = defaultdict(list)
        for order in orders:
            key = order.store if sort_by == 'store' else order.vendor
            grouped[key].append(order)
        return dict(sorted(grouped.items()))

    def _get_total_cost(self, items):
        return sum(i.total_cost for i in items)

    def _format_orders_table(self, orders: list):
        rows = []
        for o in sorted(orders, key=lambda x: x.date):
            rows.append([
                o.vendor,
                convert_date_format(o.date, '%Y%m%d', '%d-%m-%Y'),
                len(o.items),
                sum(item.quantity for item in o.items),
                f'${self._get_total_cost(o.items):,.2f}',
            ])

        headers = ['Vendor', 'Date (dd-mm-yyyy)', 'Items', 'Cases', 'Total Cost']
        return tabulate(rows, headers=headers, tablefmt='github')
