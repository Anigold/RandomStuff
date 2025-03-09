from backend.logger.Logger import Logger
from backend.workbot.WorkBot import WorkBot
from backend.ordering.OrderManager import OrderManager

import argparse
import shlex
import sys
import subprocess
import readline
# import rlcompleter as readline

from tabulate import tabulate
from termcolor import colored

from typing import Optional
from config.paths import CLI_HISTORY_FILE


class CLI:

    def __init__(self) -> None:

        self.commands = {}

        self._register_commands()
        self._setup_autocomplete()

    def _register_commands(self) -> None:
        for function_name in dir(self):
            if function_name.startswith('cmd_'):
                command_name = function_name[4:]
                self.commands[command_name] = getattr(self, function_name)

    def _setup_autocomplete(self) -> None:

        # Autocomplete
        readline.set_completer(self._completer)
        readline.parse_and_bind('tab: complete')
        
        # Command History
        if CLI_HISTORY_FILE.exists():
            readline.read_history_file(str(CLI_HISTORY_FILE))
        readline.set_history_length(100)

    # def save_command_history(self) -> None:
    #     readline.write_history_file(self.history_file_path)

    def _completer(self, text: str, state: int) -> Optional[str]:
        
        buffer = readline.get_line_buffer().split()
       
        if not buffer:
            options = list(self.commands.keys())
        if len(buffer) == 1:
            options = [cmd for cmd in self.commands.keys() if cmd.startswith(text)]
        else:
            command = buffer[0]
            if command in self.commands and hasattr(self, f'args_{command}'):
                parser = getattr(self, f'args_{command}')()
                options = [arg for arg in parser._option_string_actions.keys() if arg.startswith(text)]
            else:
                options = []
        return options[state] if state < len(options) else None
    
    def start(self) -> None:
        """Starts the interactive command loop."""
        print("\nWelcome to WorkBot CLI! Type 'help' to see available commands.\n")

        while True:
            try:
                user_input = input("WorkBot> ").strip()

                if not user_input: continue

                args         = shlex.split(user_input)
                command      = args[0]
                command_args = args[1:]

                if command in self.commands:
                    self.commands[command](command_args)
                else:
                    print(f"Unknown command: '{command}'. Type 'help' for available commands.")

                readline.write_history_file(str(CLI_HISTORY_FILE))
                
            except KeyboardInterrupt:
                print("\nExiting WorkBot CLI.")
                self._exit(0)
                break
    
    def cmd_help(self, args) -> None:
        '''Displays available commands'''
        print("\nAvailable Commands:")
        for command in sorted(self.commands.keys()):
            print(f"  {command}")
        print('\nType "command --help" for more details.\n')

    def cmd_clear_history(self, args) -> None:
        try:
            open(CLI_HISTORY_FILE, "w").close()  # Overwrite history file
            readline.clear_history()  # Clear in-memory history
            print("Command history cleared.")
        except Exception as e:
            print(f"Error: Failed to clear history ({e})")

    def _exit(self):
        '''Place holder for later shutdown needs.'''

        # Save command history before exit
      
        try:
            readline.write_history_file(str(CLI_HISTORY_FILE))
        except Exception as e:
            print(f"Warning: Failed to save history ({e})")

        sys.exit(0)


@Logger.attach_logger
class WorkBotCLI(CLI):
    ''' Interactive CLI for WorkBot '''
    
    def __init__(self, workbot = None):

        self.workbot = workbot or WorkBot()
        super().__init__()

    def cmd_download_orders(self, args):
        """Handles downloading orders."""
        parser = argparse.ArgumentParser(prog="download_orders", description="Download orders from vendors.")
        parser.add_argument("--stores", nargs="+", required=True, help="List of store names.")
        parser.add_argument("--vendors", nargs="+", help="List of vendors (default: all).")
        parser.add_argument('--sort', action='store_true', help='Sort orders by vendor after downloading.')

        parser = self.args_download_orders()
        parsed_args = parser.parse_args(args)
        try:
            self.workbot.download_orders(parsed_args.stores, parsed_args.vendors)

            if parsed_args.sort: self.workbot.sort_orders()
            
            print('\nOrders downloaded successfully.\n')
        except SystemExit:
            pass  # Prevent argparse from exiting CLI loop
    
    def args_download_orders(self):
        parser = argparse.ArgumentParser(prog="download_orders", description="Download orders from vendors.")
        parser.add_argument("--stores", nargs="+", required=True, help="List of store names.")
        parser.add_argument("--vendors", nargs="+", help="List of vendors (default: all).")
        parser.add_argument('--sort', action='store_true', help='Sort orders by vendor after downloading.')
        return parser
    
    def args_sort_orders(self) -> None:
        return argparse.ArgumentParser(prog='sort_orders', description='Sort the saved orders by vendor.')
    
    def cmd_sort_orders(self, args):
        parser = self.args_sort_orders()

        try:    
            self.workbot.sort_orders()
            print('Orders sorted successfully.')
        except SystemExit:
            pass

    def args_list_orders(self) -> None:
        parser = argparse.ArgumentParser(prog='list_orders', description='List the saved orders.')
        parser.add_argument('--stores', nargs='+', required=True, help='List of store names.')
        parser.add_argument('--vendors', nargs='+', help='List of vendors (default: all).')
        parser.add_argument('--show_pricing', action='store_true', help='Display the total estimated price of the order.')
        parser.add_argument('--show_minimums', action='store_true', help='Display the vendor order minimums.')
        return parser
        
    def cmd_list_orders(self, args):

        parser = self.args_list_orders()
        try:

            parsed_args      = parser.parse_args(args)
            
            orders           = self.workbot.get_orders(parsed_args.stores, parsed_args.vendors)
            formatted_orders = self._format_order_list(orders, parsed_args.show_pricing, parsed_args.show_minimums)
            print(formatted_orders)
        except SystemExit:
            pass

    def args_generate_vendor_upload_files(self):
        parser = argparse.ArgumentParser(prog='generate_vendor_upload_files', description='Generate a vendor-specific upload file.')
        parser.add_argument('--vendors', nargs='+', help='List of vendors (default: all).')
        return parser
    
    def cmd_generate_vendor_upload_files(self, args):
        parser = self.args_generate_vendor_upload_files()
        try:
            parsed_args = parser.parse_args(args)

            for vendor in parsed_args.vendors:
                vendor_order_paths = self.workbot.order_manager.get_vendor_orders(vendor)

                orders = [OrderManager.create_order_from_excel(vendor_order_path) for vendor_order_path in vendor_order_paths]

                self.workbot.generate_vendor_upload_files(orders)

        except SystemExit:
            pass

    def args_delete_orders(self) -> None:
        parser = argparse.ArgumentParser(prog='delete_orders', description='Download orders from vendors.')
        parser.add_argument('--stores', nargs='+', required=True, help='List of store names.')
        parser.add_argument('--vendors', nargs='+', help='List of vendors (default: all).')
        return
    
    def cmd_delete_orders(self, args):
        parser = self.args_delete_orders()
        try:
            parsed_args = parser.parse_args(args)
            self.workbot.delete_orders(parsed_args.stores, parsed_args.vendors)
            
            print("Orders deleted successfully.")
        except SystemExit:
            pass  # Prevent argparse from exiting CLI loop

    def _format_order_list(self, orders: list, show_pricing: bool = False, show_minimums: bool = False):

        orders.sort(key=lambda x: x.store)

        headers = ['Store', 'Vendor', 'Date', 'Items']

        formatted_orders = [[order.store, order.vendor, order.date, len(order.items)] for order in orders]

        if show_pricing:
            headers.append('Total Cost')
            for pos, order in enumerate(orders):
                total_cost = sum(float(item.total_cost) for item in order.items if item.total_cost) if show_pricing else "N/A"
                formatted_orders[pos].append(f'${total_cost:.2f}')
        
        if show_minimums:
            headers.extend(['Min. Price', 'Min. Cases'])
            for pos, order in enumerate(orders):
                vendor_information = self.workbot.get_vendor_information(order.vendor)
                min_order_price = vendor_information['min_order_value']
                min_order_cases = vendor_information['min_order_cases']
                
                total_cost = sum(float(item.total_cost) for item in order.items if item.total_cost) if show_pricing else "N/A"
                
                # Check if the order meets vendor minimums
                below_min_value = total_cost < min_order_price
                below_min_cases = len(order.items) < min_order_cases

                total_cost_str = colored(f"${total_cost:.2f}", "red") if below_min_value else f"${total_cost:.2f}"
                min_order_value_str = colored(f"${min_order_price:.2f}", "red") if below_min_value else f"${min_order_price:.2f}"
                min_order_cases_str = colored(str(min_order_cases), "red") if below_min_cases else str(min_order_cases)

                formatted_orders[pos].extend([min_order_value_str, min_order_cases_str])

        return tabulate(formatted_orders, headers=headers, tablefmt="grid")

    def args_open_directory(self) -> None:
        parser = argparse.ArgumentParser(prog='open_directory', description='Open the directory of the specified vendor(s).')
        parser.add_argument('--vendors', nargs='+', required=True, help='List of vendors.')
        return parser

    def cmd_open_directory(self, args) -> None:

        parser = self.args_open_directory()
        try:

            parsed_args = parser.parse_args(args)

            for vendor in parsed_args.vendors:

                directory_path = str(self.workbot.order_manager.get_vendor_orders_directory(vendor))

                try:
                    self.logger.info(f'Attempting to open directory for: {vendor}')
                    if sys.platform.startswith("win"):
                        # subprocess.run(["explorer", directory_path], check=True)
                        subprocess.Popen(['explorer', directory_path], shell=True)
                    elif sys.platform.startswith("darwin"):  # macOS
                        subprocess.run(["open", directory_path], check=True)
                    else:  # Linux and other UNIX-like systems
                        subprocess.run(["xdg-open", directory_path], check=True)

                except Exception as e:
                    print(f"Error opening file explorer: {e}")

                self.logger.info(f'Directory opened.')
        except SystemExit:
            pass  # Prevent argparse from exiting CLI loop

    def cmd_shutdown(self, args):
        """Shuts down WorkBot and all vendor sessions."""
        self.workbot.shutdown()
        print("WorkBot shut down successfully.")
        super()._exit()
        

    # def show_help(self, args):
    #     """Displays available commands."""
    #     print("\nAvailable Commands:")
    #     print("  download_orders --stores [STORE_NAMES] --vendors [VENDORS] --sort   # Download orders from Craftable for specific stores/vendors")
    #     print('  open_directory --vendors [VENDORS]                                  # Open the directory of the specified vendor(s).')
    #     print('  list_orders --stores [STORE_NAMES] --vendors [VENDORS]              # Display orders for specific stores/vendors')
    #     print('  sort_orders                                                         # Sort order files by vendor')
    #     print('  delete_orders --stores [STORE NAMES] --vendors [VENDORS]            # Delete orders from Craftable for specific stores/vendors.')
    #     print('  generate_vendor_upload_files --vendors [VENDORS]                    # Generate vendor-specific upload files in the vendors\' order directory.')
    #     print("  help                                                                # Show available commands")
    #     print("  exit                                                                # Exit the CLI\n")
