from ..command import Command
import argparse
from tabulate import tabulate
from backend.core.utils.datetimes import convert_date_format

class DisplayStoreOrders(Command):

    name = 'display_store_orders'

    def arguments(self):
        parser = argparse.ArgumentParser(prog=self.name, description='Display the general information for the orders for a given store.')
        parser.add_argument('--store', required=True, help='The store which the orders belong.')
        parser.add_argument('--vendors', required=False, nargs='+', default=self.context.get_vendors(), help='Limit the displayed orders to these vendors.')
        return parser

    def autocomplete(self, flag: str, text: str):
        
        flags = {
            '--vendors': self.context.get_vendors,
            '--store': self.context.get_stores
        }
        
        return [option for option in flags.get(flag, [])() if option.startswith(text)]

    def command(self, args):
        try:
            parser = self.arguments()
            parsed_args = parser.parse_args(args)
            orders = self.context.workbot.get_orders_by_store(parsed_args.store, parsed_args.vendors)
            print('')
            print(f'{parsed_args.store}')
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
                o.vendor,
                convert_date_format(o.date, '%Y%m%d', '%d-%m-%Y'),
                len(o.items),
                sum(item.quantity for item in o.items),
                f'${self._get_total_cost(o.items):,.02f}'
            ])
        headers = ['Store', 'Date (dd-mm-yyyy)', 'Items', 'Cases', 'Total Cost']
        return tabulate(rows, headers=headers, tablefmt="github")