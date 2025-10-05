from .command import Command
import argparse
from tabulate import tabulate

class VendorInformation(Command):

    name = 'vendor_information'

    def arguments(self):
        parser = argparse.ArgumentParser(prog=self.name, description='Display the saved information for the specified vendor, if any.')
        parser.add_argument('--vendor', required=True, help='A single vendor name.')
        return parser

    def autocomplete(self, flag: str, text: str):
        
        flags = {
            '--vendors': self.context.get_vendors
        }
        
        return [option for option in flags.get(flag, [])() if option.startswith(text)]

    def command(self, args):
        try:
            parser = self.arguments()
            parsed_args = parser.parse_args(args)
            vendor_info = self.context.workbot.get_vendor_information(parsed_args.vendor)
            print(f'\n{parsed_args.vendor}')
            print(f'{self._format_vendor_info(vendor_info)}\n')
        except SystemExit:
            pass


    def _format_vendor_info(self, data: dict) -> str:
        # Prepare the top-level vendor info
        summary_table = [
            ['Minimum Order Value', f'${data.min_order_value:,.2f}'],
            ['Minimum Order Cases', data.min_order_cases],
            ['Special Notes', data.special_notes or 'None']
        ]

        # Prepare internal contacts, if any
        contacts = data.internal_contacts
        if contacts:
            contact_table = [
                [c.name, c.title, c.email, c.phone] for c in contacts
            ]
            contact_headers = ['Name', 'Title', 'Email', 'Phone']
            contact_output = tabulate(contact_table, headers=contact_headers, tablefmt='fancy_grid')
        else:
            contact_output = '[No internal contacts listed.]'

        return f'''
===================

{tabulate(summary_table, tablefmt='plain')}

Internal Contacts:
{contact_output}
'''.strip()