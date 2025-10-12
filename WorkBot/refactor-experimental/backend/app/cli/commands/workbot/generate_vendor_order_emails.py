from ..command import Command
import argparse

class GenerateVendorOrderEmails(Command):

    name = 'generate_vendor_order_emails'

    def arguments(self):
        parser = argparse.ArgumentParser(prog=self.name, description='Create an order email for the specified vendors and stores.')
        parser.add_argument('--stores', nargs='+', required=True, help='List of stores.')
        parser.add_argument('--vendors', nargs='+', required=True, help='List of vendors.')
        return parser

    def autocomplete(self, flag: str, text: str):
        
        flags = {
            '--vendors': self.context.get_vendors,
            '--stores': self.context.get_stores
        }
        
        return [option for option in flags.get(flag, [])() if option.startswith(text)]

    def command(self, args):
        try:
            parser = self.arguments()
            parsed_args = parser.parse_args(args)
            self.context.workbot.generate_vendor_order_emails(stores=parsed_args.stores, vendors=parsed_args.vendors)
            # print('THIS COMMAND HAS NOT BEEN IMPLEMENTED.')
        except SystemExit:
            pass