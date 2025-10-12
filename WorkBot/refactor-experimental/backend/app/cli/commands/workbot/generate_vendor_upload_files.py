from ..command import Command
import argparse

class GenerateVendorUploadFiles(Command):

    name = 'generate_vendor_upload_files'

    def arguments(self):
        parser = argparse.ArgumentParser(prog='generate_vendor_upload_files', description='Generate a vendor-specific upload file.')
        parser.add_argument('--stores', nargs='+', help='List of store names (default: all).')       
        parser.add_argument('--vendors', nargs='+', help='List of vendors (default: all).')
        parser.add_argument('--start_date', help='Start of date range for lookup (yyyy-mm-dd)')
        parser.add_argument('--end_date', help='End of date range for lookup (yyyy-mm-dd)')
        return parser

    def autocomplete(self, flag: str, text: str):
        
        flags = {
            '--stores': self.context.get_stores,
            '--vendors': self.context.get_vendors
        }
        
        return [option for option in flags.get(flag, [])() if option.startswith(text)]

    def command(self, args):
        parser = self.arguments()
        try:
            parsed_args = parser.parse_args(args)

            paths = self.context.workbot.generate_vendor_upload_files(
                stores=parsed_args.stores,
                vendors=parsed_args.vendors,
                start_date=parsed_args.start_date,
                end_date=parsed_args.end_date
            )

            print('\nUpload files generated successfully.\n')
        except SystemExit:
            pass