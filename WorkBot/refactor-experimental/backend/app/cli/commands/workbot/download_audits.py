from ..command import Command
import argparse

class DownloadAudits(Command):

    name = 'download_audits'

    def arguments(self):
        parser = argparse.ArgumentParser(
            prog=self.name,
            description='Downloads audits from Craftable.'
        )
        parser.add_argument('--stores', nargs='+', default=['Bakery', 'Collegetown', 'Triphammer', 'Downtown', 'Easthill'], help='An active store.')
        parser.add_argument('--start_date', help='Date in mm/dd/yyyy format.')
        parser.add_argument('--end_date', help='Date in mm/dd/yyyy format.')
        return parser

    def autocomplete(self, flag: str, text: str):
        
        flags = {
            '--stores': self.context.get_stores,
        }
        
        return [option for option in flags.get(flag, [])() if option.startswith(text)]

    def command(self, args):
        parser = self.arguments()
        parsed_args = parser.parse_args(args)
        try:
            self.context.workbot.download_audits(parsed_args.stores, parsed_args.start_date, parsed_args.end_date)
        except:
            print('oops')