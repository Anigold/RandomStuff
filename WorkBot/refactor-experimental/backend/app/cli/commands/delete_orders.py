from .command import Command
import argparse

class DeleteOrders(Command):

    name = 'delete_orders'

    def arguments(self):
        parser = argparse.ArgumentParser(prog='delete_orders', description='Delete orders from craftable based on store(s) and vendor(s).')
        parser.add_argument('--stores', nargs='+', required=True, help='List of store names.')
        parser.add_argument('--vendors', nargs='+', help='List of vendors (default: all).')
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
            parsed_args = parser.parse_args(args)
            self.context.workbot.delete_craftable_orders(parsed_args.stores, parsed_args.vendors)
            
            print('Orders deleted successfully.')
        except SystemExit:
            pass  # Prevent argparse from exiting CLI loop
