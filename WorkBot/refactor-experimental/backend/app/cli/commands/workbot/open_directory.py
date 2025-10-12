from ..command import Command
import argparse
import sys, subprocess

class OpenDirectory(Command):

    name = 'open_directory'

    def arguments(self):
        parser = argparse.ArgumentParser(prog='open_directory', description='Open the directory of the specified vendor(s).')
        parser.add_argument('--vendors', nargs='+', required=True, help='List of vendors.')
        return parser

    def autocomplete(self, flag: str, text: str):
        
        flags = {
            '--vendors': self.context.get_vendors
        }
        
        return [option for option in flags.get(flag, [])() if option.startswith(text)]

    def command(self, args):
        parser = self.args_open_directory()
        try:

            parsed_args = parser.parse_args(args)

            for vendor in parsed_args.vendors:

                directory_path = str(self.workbot.order_manager.get_vendor_orders_directory(vendor))

                try:
                    self.logger.info(f'Attempting to open directory for: {vendor}')
                    if sys.platform.startswith('win'):
                        # subprocess.run(['explorer', directory_path], check=True)
                        subprocess.Popen(['explorer', directory_path], shell=True)
                    elif sys.platform.startswith('darwin'):  # macOS
                        subprocess.run(['open', directory_path], check=True)
                    else:  # Linux and other UNIX-like systems
                        subprocess.run(['xdg-open', directory_path], check=True)

                except Exception as e:
                    print(f'Error opening file explorer: {e}')

                self.logger.info(f'Directory opened.')
        except SystemExit:
            pass  # Prevent argparse from exiting CLI loop
