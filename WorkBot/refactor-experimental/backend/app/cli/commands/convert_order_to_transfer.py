from .command import Command
import argparse

class ConvertOrderToTransfer(Command):

    name = 'convert_order_to_transfer'

    def arguments(self):
        parser = argparse.ArgumentParser(prog=self.name, description='Find an active order with the given store and vendor, and then convert it to a transfer.')
        parser.add_argument('--destination', required=True, help='The store which the order belongs to.')
        parser.add_argument('--vendor', required=True, help='A single vendor name.')
        parser.add_argument('--origin', required=True, help='The store the transfer should be sent from.')
        return parser

    def autocomplete(self, flag: str, text: str):
        
        flags = {
            '--destination': self.context.get_stores,
            '--origin': self.context.get_stores,
            '--vendor': self.context.get_vendors
        }
        
        return [option for option in flags.get(flag, [])() if option.startswith(text)]

    def command(self, args):
        try:
            parser = self.arguments()
            parsed_args = parser.parse_args(args)
            self.context.workbot.convert_order_to_transfer(parsed_args.destination, parsed_args.vendor, parsed_args.origin)
        except SystemExit:
            pass
