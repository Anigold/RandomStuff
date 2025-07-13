from command import Command
import argparse

class DownloadOrders(Command):

    def arguments(self):
        parser = argparse.ArgumentParser(prog="download_orders", description="Download orders from vendors.")
        parser.add_argument("--stores", nargs="+", required=True, help="List of store names.")
        parser.add_argument("--vendors", nargs="+", help="List of vendors (default: all).")
        parser.add_argument('--sort', action='store_true', help='Sort orders by vendor after downloading.')
        return parser

    def autocomplete(self, flag: str, text: str):
        
        flags = {
            '--stores': self._get_stores,
            '--vendors': self._get_vendors
        }
        
        return [option for option in flags.get(flag, [])() if option.startswith(text)]

    def command(self, args):
        """Handles downloading orders."""

        parser = self.arguments()
        parsed_args = parser.parse_args(args)
        try:
            self.workbot.download_orders(parsed_args.stores, parsed_args.vendors)

            if parsed_args.sort: self.workbot.sort_orders()
            
            print('\nOrders downloaded successfully.\n')
        except SystemExit:
            pass  # Prevent argparse from exiting CLI loop
