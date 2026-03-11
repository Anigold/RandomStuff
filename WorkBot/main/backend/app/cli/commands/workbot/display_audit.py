from ..command import Command
import argparse
from tabulate import tabulate
from backend.core.utils.datetimes import convert_date_format

class DisplayAudit(Command):

    name = 'display_audit'

    def arguments(self):
        parser = argparse.ArgumentParser(prog=self.name, description='Display the general information for a single store audit.')
        parser.add_argument('--store', required=True, help='The store to which the audit belongs.')
        return parser

    def autocomplete(self, flag: str, text: str):
        
        flags = {
            '--store': self.context.get_stores
        }
        
        return [option for option in flags.get(flag, [])() if option.startswith(text)]

    def command(self, args):
        try:
            parser = self.arguments()
            parsed_args = parser.parse_args(args)
            audit = self.context.workbot.get_audits(stores=[parsed_args.store])

            if not audit:
                print('')
                print('No audit found')
                print('')
            
            else: 
                audit = audit[0]  
                print("\nORDER SUMMARY")
                print("-------------")
                print(f"Vendor:      {audit.vendor}")
                print(f"Store:       {audit.store}")
                print()

                order_total = sum(item.total_cost for item in audit.items)
                print(f"Order Total: ${order_total:,.2f}")

                total_cases = sum(item.quantity for item in audit.items)
                print(f'Total Cases: {total_cases}\n')


                # -------------------------
                # Item Table
                # -------------------------
                if not audit.items:
                    print("No items found on this audit.\n")
                    return

                rows = []
                for pos, item in enumerate(audit.items):
                    rows.append([
                        pos+1,
                        item.sku,
                        item.name,
                        item.quantity,
                        item.cost_per,
                        item.total_cost,
                    ])

                headers = ["#", "SKU", "Item Name", "Qty", "Cost Per ($)", "Total ($)"]
                table = tabulate(rows, headers=headers, tablefmt="github", floatfmt=',.2f')
                print(table)
                print()

        except SystemExit:
            pass


    def _format_audit_items_table(self, audit_items: list):

        headers = ['Store', 'Date (dd-mm-yyyy)', 'Items', 'Total Cost']
        rows = []
        for o in audit_items:
            rows.append([
                o.store,
                convert_date_format(o.date, '%Y%m%d', '%d-%m-%Y'),
                len(o.items),
                f'${self._get_total_cost(o.items):,.02f}'
            ])
        
        return tabulate(rows, headers=headers, tablefmt="github")