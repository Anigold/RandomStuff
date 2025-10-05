from .command import Command
import argparse

class DownloadOrders(Command):

    name = 'download_orders'

    def arguments(self):
        parser = argparse.ArgumentParser(prog="download_orders", description="Download orders from vendors.")
        parser.add_argument("--stores", nargs="+", required=True, help="List of store names.")
        parser.add_argument("--vendors", nargs="+", help="List of vendors (default: all).")
        parser.add_argument('--sort', action='store_true', help='Sort orders by vendor after downloading.')
        return parser

    def autocomplete(self, flag: str, text: str):
        
        flags = {
            '--stores': self.context.get_stores,
            '--vendors': self.context.get_vendors
        }
        
        return [option for option in flags.get(flag, [])() if option.startswith(text)]

    def command(self, args):
        '''Handles downloading orders.'''

        parser = self.arguments()
        parsed_args = parser.parse_args(args)
        try:
            self.context.workbot.download_craftable_orders(parsed_args.stores, parsed_args.vendors)
        except SystemExit:
            pass  # Prevent argparse from exiting CLI loop

        print('\nOrders downloaded successfully.\n') # You nasty little side effect you...