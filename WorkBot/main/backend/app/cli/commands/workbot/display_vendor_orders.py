from ..command import Command
import argparse
from tabulate import tabulate
from backend.core.utils.datetimes import convert_date_format

class DisplayVendorOrders(Command):

    name = 'display_vendor_orders'

    def arguments(self):
        parser = argparse.ArgumentParser(prog=self.name, description='Display the general information for each order for a given vendor.')
        parser.add_argument('--vendor', required=True, help='The vendor which the orders belong.')
        parser.add_argument('--stores', required=False, nargs='+', default=self.context.get_stores(), help='Limit the displayed orders to these stores.')
        return parser

    def autocomplete(self, flag: str, text: str):
        
        flags = {
            '--vendor': self.context.get_vendors,
            '--stores': self.context.get_stores
        }
        
        return [option for option in flags.get(flag, [])() if option.startswith(text)]

    def command(self, args):
        try:
            parser = self.arguments()
            parsed_args = parser.parse_args(args)
            orders = self.context.workbot.get_orders_by_vendor(parsed_args.vendor, parsed_args.stores)
            print('')
            print(f'{parsed_args.vendor}')
            print('')
            print(self._format_orders_table(orders))
            print('')
            total = sum(order.total_cost for order in orders)
            print(f'Total Cost: ${total:,.2f}')
            print('')
        except SystemExit:
            pass

    def _get_total_cost(self, items):
        total = 0
        for i in items:
            total += i.total_cost
        return total
    

    def _format_orders_table(self, orders: list):

        rows = []
        for o in orders:
            rows.append([
                o.store,
                convert_date_format(o.date, '%Y%m%d', '%d-%m-%Y'),
                len(o.items),
                sum(item.quantity for item in o.items),
                f'${self._get_total_cost(o.items):,.02f}'
            ])
        headers = ['Store', 'Date (dd-mm-yyyy)', 'Items', 'Cases', 'Total Cost']
        return tabulate(rows, headers=headers, tablefmt="github")