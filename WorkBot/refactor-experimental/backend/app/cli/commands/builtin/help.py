from ..command import Command
import argparse

class Help(Command):

    name = 'help'

    def arguments(self):
        parser = argparse.ArgumentParser(prog=self.name, description='Display the help screen.')
        return parser

    def autocomplete(self, flag: str, text: str):
        return []

    def command(self, args):
        '''Handles downloading orders.'''

        parser = self.arguments()
        parsed_args = parser.parse_args(args)
        try:
            self.context.workbot.download_craftable_orders(parsed_args.stores, parsed_args.vendors)
        except SystemExit:
            pass  # Prevent argparse from exiting CLI loop

        print('\nOrders downloaded successfully.\n') # You nasty little side effect you...


        '''Displays available commands'''
        self.logger.info("Help command invoked.")
        print('\nAvailable Commands:')
        for command in sorted(self.context.cli.commands.keys()):
            print(f'  {command}')
        print('\nType "command --help" for more details.\n')