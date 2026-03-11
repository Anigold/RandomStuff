from ..command import Command
import argparse

class ArchiveOrders(Command):

    name = 'archive_orders'

    def arguments(self):
        parser = argparse.ArgumentParser(prog=self.name, description='Archives all current, un-archived orders.')
        parser.add_argument('--stores', nargs='+', default=self.context.get_stores(), help='List of stores.')
        parser.add_argument('--vendors', nargs='+', default=self.context.get_vendors(), help='List of vendors.')
        return parser

    def autocomplete(self, flag: str, text: str):
        
        flags = {
            '--stores': self.context.get_stores,
            '--vendors': self.context.get_vendors
        }
        
        return [option for option in flags.get(flag, [])() if option.startswith(text)]

    def command(self, args):
        try:
            parser = self.arguments()
            parsed_args = parser.parse_args(args)
            self.context.workbot.archive_all_current_orders(parsed_args.stores, parsed_args.vendors)
        except SystemExit:
            pass