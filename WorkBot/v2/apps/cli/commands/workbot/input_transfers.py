from ..command import Command
import argparse

class InputTransfers(Command):

    name = 'input_transfers'

    def arguments(self):
        parser = argparse.ArgumentParser(prog=self.name, description='Input into Craftable all the transfers found in the Transfers Directory.')
        return parser

    def autocomplete(self, flag: str, text: str):
        
        flags = {
            '--stores': self.context.get_stores,
        }
        
        return [option for option in flags.get(flag, [])() if option.startswith(text)]

    def command(self, args):
        try:
            self.context.workbot.input_craftable_transfers()
        except SystemExit:
            pass