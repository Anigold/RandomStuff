from ..command import Command
import argparse
from tabulate import tabulate
from backend.core.utils.datetimes import convert_date_format

class DisplayOrder(Command):

    name = 'display_order'

    def arguments(self):
        parser = argparse.ArgumentParser(prog=self.name, description='Display the general information for a single order.')
        parser.add_argument('--vendor', required=True, help='The vendor to which the order belongs.')
        parser.add_argument('--store', required=True, help='The store to which the order belongs.')
        return parser

    def autocomplete(self, flag: str, text: str):
        
        flags = {
            '--vendor': self.context.get_vendors,
            '--store': self.context.get_stores
        }
        
        return [option for option in flags.get(flag, [])() if option.startswith(text)]

    def command(self, args):
        try:
            parser = self.arguments()
            parsed_args = parser.parse_args(args)
            order = self.context.workbot.get_orders(stores=[parsed_args.store], vendors=[parsed_args.vendor])

            if not order:
                print('')
                print('No order found')
                print('')
            
            else: 
                order = order[0]  
                print("\nORDER SUMMARY")
                print("-------------")
                print(f"Vendor:      {order.vendor}")
                print(f"Store:       {order.store}")
                print()

                order_total = sum(item.total_cost for item in order.items)
                print(f"Order Total: ${order_total:,.2f}")

                total_cases = sum(item.quantity for item in order.items)
                print(f'Total Cases: {total_cases}\n')


                # -------------------------
                # Item Table
                # -------------------------
                if not order.items:
                    print("No items found on this order.\n")
                    return

                rows = []
                for item in order.items:
                    rows.append([
                        item.sku,
                        item.name,
                        item.quantity,
                        item.cost_per,
                        item.total_cost,
                    ])

                headers = ["SKU", "Item Name", "Qty", "Cost Per ($)", "Total ($)"]
                table = tabulate(rows, headers=headers, tablefmt="github", floatfmt=',.2f')
                print(table)
                print()

        except SystemExit:
            pass


    def _format_order_items_table(self, order_items: list):

        headers = ['Store', 'Date (dd-mm-yyyy)', 'Items', 'Total Cost']
        rows = []
        for o in order_items:
            rows.append([
                o.store,
                convert_date_format(o.date, '%Y%m%d', '%d-%m-%Y'),
                len(o.items),
                f'${self._get_total_cost(o.items):,.02f}'
            ])
        
        return tabulate(rows, headers=headers, tablefmt="github")