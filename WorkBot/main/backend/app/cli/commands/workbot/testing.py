from ..command import Command
import argparse

class Testing(Command):

    name = 'testing'

    def arguments(self):
        parser = argparse.ArgumentParser(prog=self.name, description="Testing the ArchiveTransfers")

        parser.add_argument(
            "--item",
            required=True,
            help="The vendor to which the order belongs.",
        )
        
        return parser

    def autocomplete(self, flag: str, text: str):
        
        flags = {
            '--item': self.context.get_items
        }
        
        return [option for option in flags.get(flag, [])() if option.startswith(text)]

    def command(self, args):
        '''Handles downloading orders.'''
        parser = self.arguments()
        parsed_args = parser.parse_args(args)
        try:
            self.context.workbot.testing_function()
        except SystemExit:
            pass  # Prevent argparse from exiting CLI loop

        print('\nTesting complete.\n') # You nasty little side effect you...