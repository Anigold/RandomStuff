from backend.logger.Logger import Logger
from backend.workbot.WorkBot import WorkBot
from backend.ordering.OrderManager import OrderManager

import argparse
import shlex
import sys
import subprocess

try:
    import readline
except ImportError:
    import pyreadline3 as pry
    import sys
    sys.modules['readline'] = pry
    import readline

# import rlcompleter as readline

from tabulate import tabulate
from termcolor import colored

from typing import Optional
from config.paths import CLI_HISTORY_FILE

import re

from pprint import pprint

class CLI:

    FLAG_REGEX_PATTERN = r'(--\w[\w-]*)(?:\s+([^\s-][^\s]*))?'

    def __init__(self) -> None:

        self.commands = {}

        self._register_commands()

        self.autocomplete_registry = {}
        self._setup_autocomplete()


    def _register_commands(self) -> None:
        for function_name in dir(self):
            if function_name.startswith('cmd_'):
                command_name = function_name[4:]
                self.commands[command_name] = getattr(self, function_name)

    def _setup_autocomplete(self) -> None:

        # Autocomplete
        readline.set_completer(self._completer)

        # We need to remove the hyphen as a word delimiter to enable the usage of flags (e.g. "command --flag 'Flag value').
        delimiters = readline.get_completer_delims().replace('-', '')
        readline.set_completer_delims(delimiters + ' ') # Possible Bug: on startup there is a chance the blank space is not present in the default delims.
        

        readline.parse_and_bind("set completion-ignore-case on")        # Ignore case sensitivity
        readline.parse_and_bind("set show-all-if-ambiguous on")         # List all matches if ambiguous
        readline.parse_and_bind("set menu-complete-display-prefix on")  # Show common prefix in list
        readline.parse_and_bind("set skip-completed-text on")
        readline.parse_and_bind("TAB: complete")

        # Command History
        if CLI_HISTORY_FILE.exists():
            readline.read_history_file(str(CLI_HISTORY_FILE))
        readline.set_history_length(100)





        # ADD NEWLINE PLACES AT TOP AND BOTTOM OF AUTOCOMPLETE RESULTS
        # Save the original method
        # _original_display_matches = readline.get_completer_delims

        # def patched_display_matches(substitution, matches, longest_match_length):
        #     print("\n")  # newline BEFORE suggestions
        #     for match in matches:
        #         print(match)
        #     print()  # newline AFTER suggestions

        # readline.set_completion_display_matches_hook(patched_display_matches)
        


        self._register_autocomplete()
        
    # REGISTER AUTOCOMPLETES
    def _register_autocomplete(self) -> None:
        for function_name in dir(self):
            prefix = '_autocomplete_'
            if function_name.startswith(prefix):
                autocomplete_name = function_name[len(prefix):]
                self.autocomplete_registry[autocomplete_name] = getattr(self, function_name)


    def _completer(self, text: str, state: int) -> Optional[str]:
        buffer = readline.get_line_buffer().strip()


        FLAG_REGEX = re.compile(self.FLAG_REGEX_PATTERN)

        if not buffer:  # Nothing typed
            options = list(self.commands.keys())
        elif " " not in buffer:  # Typing command
            options = [cmd for cmd in self.commands.keys() if cmd.startswith(buffer)]
        else:
            command = buffer.split()[0]
            if command not in self.commands:
                return None

            possible_flags = self._get_command_args(command, "")

            # Find all flag matches
            matches = FLAG_REGEX.findall(buffer)

            if matches:
                last_flag = None  # Track the most recent flag

                # Iterate over matches to determine the last flag in the buffer
                for flag, _ in matches:  
                    if flag in possible_flags:
                        last_flag = flag  # Store last valid flag

                last_token = buffer.split()[-1]

                # Case 1: Typing a new flag (`--`)
                if last_token.startswith("--"):
                    options = [f for f in possible_flags if f.startswith(text)]

                # Case 2: Pressing TAB **after** a flag (should show values)
                elif last_flag and (last_token == last_flag or buffer.endswith(" ")):
                    if last_flag in possible_flags and command in self.autocomplete_registry:
                        handler = self.autocomplete_registry[command]
                        options = handler(last_flag, text)

                # Case 3: Typing within a flag value (autocomplete values)
                elif last_flag and last_token not in possible_flags:
                    if command in self.autocomplete_registry:
                        handler = self.autocomplete_registry[command]
                        options = handler(last_flag, text)

                # Case 4: Something weird happens and Cases 1 - 3 aren't reached
                else:
                    options = []
            else:
                options = possible_flags if buffer.count(" ") == 1 else []

        return options[state] if state < len(options) else None
   
    def _get_command_args(self, command: str, text: str):
        if hasattr(self, f'args_{command}'):
            parser = getattr(self, f'args_{command}')()
            return [arg for arg in parser._option_string_actions.keys() if arg.startswith(text)]
        return []

    def register_autocomplete(self, command: str, handler):
        self.autocomplete_registry[command] = handler

    def start(self, welcome_screen: str = '\nWelcome to your CLI. Type "help" to see available commands.\n') -> None:
        print(welcome_screen)
        self._run()
    
    def cmd_shutdown(self, args):
        '''Shuts down CLI.'''
        self._exit()

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
      
        # try:
        #     readline.write_history_file(str(CLI_HISTORY_FILE))
        # except Exception as e:
        #     print(f"Warning: Failed to save history ({e})")

        sys.exit(0)

    def _run(self):
        while True:
            try:
                user_input = input('WorkBot> ').strip()

                if not user_input: continue

                args         = shlex.split(user_input)
                command      = args[0]
                command_args = args[1:]

                if command in self.commands:
                    self.commands[command](command_args)
                else:
                    print(f'Unknown command: "{command}". Type "help" for available commands.')

                readline.write_history_file(str(CLI_HISTORY_FILE))
                
            except KeyboardInterrupt:
                print('\nExiting CLI.')
                self._exit(0)
                break


@Logger.attach_logger
class WorkBotCLI(CLI):
    ''' Interactive CLI for WorkBot '''
    
    def __init__(self, workbot = None):

        self.workbot = workbot or WorkBot()
        super().__init__()

        # self.context = CommandContext(workbot=self.workbot)

# DOWNLOAD ORDERS
    def cmd_download_orders(self, args):
        """Handles downloading orders."""

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
    
    def _autocomplete_download_orders(self, flag: str, text: str):

        
        flags = {
            '--stores': self._get_stores,
            '--vendors': self._get_vendors
        }
        
        return [option for option in flags.get(flag, [])() if option.startswith(text)]


# SORT ORDERS
    def args_sort_orders(self) -> None:
        return argparse.ArgumentParser(prog='sort_orders', description='Sort the saved orders by vendor.')
    
    def cmd_sort_orders(self, args):
        parser = self.args_sort_orders()

        try:    
            self.workbot.sort_orders()
            print('Orders sorted successfully.')
        except SystemExit:
            pass


# LIST ORDERS
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
            print(f'\n{formatted_orders}\n')
        except SystemExit:
            pass

    def _format_order_list(self, orders: list, show_pricing: bool = False, show_minimums: bool = False):

        if not orders: return tabulate([])

        orders.sort(key=lambda x: x.store)

        headers = ['Store', 'Vendor', 'Date', 'Items', 'Cases']

        formatted_orders = [[order.store, order.vendor, order.date, len(order.items), sum([int(i.quantity) for i in order.items])] for order in orders]

        if show_pricing:
            headers.append('Total Cost')
            for pos, order in enumerate(orders):
                total_cost = sum(float(item.total_cost) for item in order.items if item.total_cost) if show_pricing else "N/A"
                formatted_orders[pos].append(f'${total_cost:.2f}')
        
        if show_minimums:
            headers.extend(['Min. Price', 'Min. Cases'])
            for pos, order in enumerate(orders):
                vendor_information = self.workbot.get_vendor_information(order.vendor)

                min_order_price = vendor_information['min_order_value'] if 'min_order_value' in vendor_information else ''
                min_order_cases = vendor_information['min_order_cases'] if 'min_order_cases' in vendor_information else ''
                
                total_cost = sum(float(item.total_cost) for item in order.items if item.total_cost) if show_pricing else "N/A"
                
                # Check if the order meets vendor minimums
                # below_min_value = total_cost < min_order_price
                # below_min_cases = len(order.items) < min_order_cases

                # total_cost_str = colored(f"${total_cost:.2f}", "red") if below_min_value else f"${total_cost:.2f}"
                # min_order_value_str = colored(f"${min_order_price:.2f}", "red") if below_min_value else f"${min_order_price:.2f}"
                # min_order_cases_str = colored(str(min_order_cases), "red") if below_min_cases else str(min_order_cases)

                formatted_orders[pos].extend([min_order_price, min_order_cases])

        return tabulate(formatted_orders, headers=headers, tablefmt="grid")

    def _autocomplete_list_orders(self, flag: str, text: str):
        
        flags = {
            '--stores': self._get_stores,
            '--vendors': self._get_vendors
        }
        
        return [option for option in flags.get(flag, [])() if option.startswith(text)]


# GENERATE VENDOR UPLOAD FILES
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

    def _autocomplete_generate_vendor_upload_files(self, flag: str, text: str):
        
        flags = {
            '--vendors': self._get_vendors
        }
        
        return [option for option in flags.get(flag, [])() if option.startswith(text)]


# DELETE ORDERS
    def args_delete_orders(self) -> None:
        parser = argparse.ArgumentParser(prog='delete_orders', description='Download orders from vendors.')
        parser.add_argument('--stores', nargs='+', required=True, help='List of store names.')
        parser.add_argument('--vendors', nargs='+', help='List of vendors (default: all).')
        return parser
    
    def cmd_delete_orders(self, args):
        parser = self.args_delete_orders()
        try:
            parsed_args = parser.parse_args(args)
            self.workbot.delete_orders(parsed_args.stores, parsed_args.vendors)
            
            print("Orders deleted successfully.")
        except SystemExit:
            pass  # Prevent argparse from exiting CLI loop

    def _autocomplete_delete_orders(self, flag: str, text: str):

        
        flags = {
            '--stores': self._get_stores,
            '--vendors': self._get_vendors
        }
        
        return [option for option in flags.get(flag, [])() if option.startswith(text)]


# OPEN DIRECTORY
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

    def _autocomplete_open_directory(self, flag: str, text: str):
        
        flags = {
            '--vendors': self._get_vendors
        }
        
        return [option for option in flags.get(flag, [])() if option.startswith(text)]


# COMBINE ORDERS
    def args_combine_orders(self):
        parser = argparse.ArgumentParser(prog='combine_orders', description='Merge all orders in a specific vendor order directory into a single file.')
        parser.add_argument('--vendors', nargs='+', required=True, help='List of vendors.')
        return parser
    
    def cmd_combine_orders(self, args) -> None:

        parser = self.args_combine_orders()
        parsed_args = parser.parse_args(args)
        try:
            self.workbot.order_manager.combine_orders(parsed_args.vendors)
        except SystemExit:
            pass

    def _autocomplete_combine_orders(self, flag: str, text: str):

        flags = {
            '--vendors': self._get_vendors
        }
        
        return [option for option in flags.get(flag, [])() if option.startswith(text)]


# VENDOR INFORMATION
    def args_vendor_information(self):
        parser = argparse.ArgumentParser(prog='vendor_information', description='Display the saved information for the specified vendor, if any.')
        parser.add_argument('--vendor', required=True, help='A single vendor name.')
        return parser

    def cmd_vendor_information(self, args):
        
        try:
            parser = self.args_vendor_information()
            parsed_args = parser.parse_args(args)
            vendor_info = self.workbot.get_vendor_information(parsed_args.vendor)
            print(f'\n{parsed_args.vendor}')
            print(f'{self._format_vendor_info(vendor_info)}\n')
        except SystemExit:
            pass
    
    from tabulate import tabulate

    def _format_vendor_info(self, data: dict) -> str:
        # Prepare the top-level vendor info
        summary_table = [
            ["Minimum Order Value", f"${data.get('min_order_value', 0):,.2f}"],
            ["Minimum Order Cases", data.get("min_order_cases", 0)],
            ["Special Notes", data.get("special_notes") or "None"]
        ]

        # Prepare internal contacts, if any
        contacts = data.get("internal_contacts", [])
        if contacts:
            contact_table = [
                [c["name"], c["title"], c["email"], c["phone"]] for c in contacts
            ]
            contact_headers = ["Name", "Title", "Email", "Phone"]
            contact_output = tabulate(contact_table, headers=contact_headers, tablefmt="fancy_grid")
        else:
            contact_output = "[No internal contacts listed.]"

        return f"""
===================

{tabulate(summary_table, tablefmt="plain")}

Internal Contacts:
{contact_output}
""".strip()

    def _autocomplete_vendor_information(self, flag: str, text: str):

        flags = {
            '--vendor': self._get_vendors
        }

        return [option for option in flags.get(flag, [])() if option.startswith(text)]

    
# GENERATE ORDER EMAILS
    def args_generate_vendor_order_emails(self):
        parser = argparse.ArgumentParser(prog='generate_vendor_email', description='Create an order email for the specified vendors and stores.')
        parser.add_argument('--stores', nargs='+', required=True, help='List of stores.')
        parser.add_argument('--vendors', nargs='+', required=True, help='List of vendors.')
        return parser

    def cmd_generate_vendor_order_emails(self, args):
        try:
            parser = self.args_generate_vendor_order_emails()
            parsed_args = parser.parse_args(args)
            self.workbot.generate_vendor_order_emails(stores=parsed_args.stores, vendors=parsed_args.vendors)
            # print("THIS COMMAND HAS NOT BEEN IMPLEMENTED.")
        except SystemExit:
            pass
    
    def _autocomplete_generate_vendor_order_emails(self, flag: str, text: str):
        flags = {
            '--stores': self._get_stores,
            '--vendors': self._get_vendors
        }
        
        return [option for option in flags.get(flag, [])() if option.startswith(text)]


    def _get_stores(self):
        return [store.name for store in self.workbot.store_manager.list_stores()]
    
    def _get_vendors(self):
        return sorted(self.workbot.vendor_manager.list_vendors())

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
