from ..command import Command
import argparse

class CombineOrders(Command):

    name = 'combine_orders'

    def arguments(self):
        parser = argparse.ArgumentParser(prog=self.name, description='Merge all orders in a specific vendor order directory into a single file.')
        parser.add_argument('--vendors', nargs='+', required=True, help='List of vendors.')
        return parser

    def autocomplete(self, flag: str, text: str):
        
        flags = {
            '--vendors': self.context.get_vendors
        }
        
        return [option for option in flags.get(flag, [])() if option.startswith(text)]

    def command(self, args):
        parser = self.arguments()
        parsed_args = parser.parse_args(args)
        try:
            self.context.workbot.combine_orders(parsed_args.vendors)
        except SystemExit:
            pass