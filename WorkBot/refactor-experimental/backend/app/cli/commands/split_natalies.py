from .command import Command
import argparse

class SplitNatalies(Command):

    name = 'split_natalies'

    def arguments(self):
        return argparse.ArgumentParser(prog=self.name, description='Look at the Natalies from each order (FingerLakes Farms and Performance) and load them into the hardcoded (FIX THIS) spreadsheet.')
    

    def autocomplete(self, flag: str, text: str):
        
        flags = {
            '--stores': self.context.get_stores,
            '--vendors': self.context.get_vendors
        }
        
        return [option for option in flags.get(flag, [])() if option.startswith(text)]

    def command(self, args):
        try:    
            self.context.workbot.split_natalies()
            print('All Natalie Juices split.')
        except SystemExit:
            pass