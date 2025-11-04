from ..command import Command
import argparse

class Testing(Command):

    name = 'testing'

    def arguments(self):
        parser = argparse.ArgumentParser(prog=self.name, description="Testing the GoToOrder")
        parser.add_argument("--stores", nargs='+', default=self.context.get_stores(), help="A single store name.")
        parser.add_argument("--vendors", nargs='+', help="A single vendor name.")
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
            self.context.workbot.testing_function(parsed_args.stores, parsed_args.vendors)
        except SystemExit:
            pass  # Prevent argparse from exiting CLI loop

        print('\nTesting complete.\n') # You nasty little side effect you...