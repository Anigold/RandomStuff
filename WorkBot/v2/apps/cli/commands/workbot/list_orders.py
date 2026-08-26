from ..command import Command
import argparse
from tabulate import tabulate

class ListOrders(Command):

    name = 'list_orders'

    def arguments(self):
        parser = argparse.ArgumentParser(prog='list_orders', description='List the saved orders.')
        parser.add_argument('--stores', nargs='+', required=True, help='List of store names.')
        parser.add_argument('--vendors', nargs='+', help='List of vendors (default: all).')
        parser.add_argument('--show_pricing', action='store_true', help='Display the total estimated price of the order.')
        parser.add_argument('--show_minimums', action='store_true', help='Display the vendor order minimums.')
        return parser

    def autocomplete(self, flag: str, text: str):
        
        flags = {
            '--stores': self.context.get_stores,
            '--vendors': self.context.get_vendors
        }
        
        return [option for option in flags.get(flag, [])() if option.startswith(text)]

    def command(self, args):
        parser = self.arguments()
        try:

            parsed_args      = parser.parse_args(args)
            
            orders           = self.context.workbot.get_orders(parsed_args.stores, parsed_args.vendors)
            formatted_orders = self._format_order_list(orders, parsed_args.show_pricing, parsed_args.show_minimums)
            print(f'\n{formatted_orders}\n')
        except SystemExit:
            pass

    def _format_order_list(self, orders: list, show_pricing: bool = False, show_minimums: bool = False):

        if not orders: return tabulate([])

        orders.sort(key=lambda x: x.store)

        headers = ['Store', 'Vendor', 'Date', 'Items', 'Cases']

        formatted_orders = [[order.store, order.vendor, order.date, len(order.items), sum([int(i.quantity) for i in order.items])] for order in orders]

        if show_pricing:
            headers.append('Total Cost')
            for pos, order in enumerate(orders):
                total_cost = sum(float(item.total_cost) for item in order.items if item.total_cost) if show_pricing else 'N/A'
                formatted_orders[pos].append(f'${total_cost:.2f}')
        
        if show_minimums:
            headers.extend(['Min. Price', 'Min. Cases'])
            for pos, order in enumerate(orders):
                vendor_information = self.workbot.get_vendor_information(order.vendor)

                min_order_price = vendor_information['min_order_value'] if 'min_order_value' in vendor_information else ''
                min_order_cases = vendor_information['min_order_cases'] if 'min_order_cases' in vendor_information else ''
                
                total_cost = sum(float(item.total_cost) for item in order.items if item.total_cost) if show_pricing else 'N/A'
                
                # Check if the order meets vendor minimums
                # below_min_value = total_cost < min_order_price
                # below_min_cases = len(order.items) < min_order_cases

                # total_cost_str = colored(f'${total_cost:.2f}', 'red') if below_min_value else f'${total_cost:.2f}'
                # min_order_value_str = colored(f'${min_order_price:.2f}', 'red') if below_min_value else f'${min_order_price:.2f}'
                # min_order_cases_str = colored(str(min_order_cases), 'red') if below_min_cases else str(min_order_cases)

                formatted_orders[pos].extend([min_order_price, min_order_cases])

        return tabulate(formatted_orders, headers=headers, tablefmt='grid')
