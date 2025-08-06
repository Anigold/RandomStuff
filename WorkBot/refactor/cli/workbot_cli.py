from backend.utils.logger import Logger
from backend.bots.workbot.work_bot import WorkBot
import argparse
import sys
import subprocess
from tabulate import tabulate
try:
    import readline
except ImportError:
    import pyreadline3 as pry
    sys.modules['readline'] = pry
    import readline
from cli.cli import CLI

@Logger.attach_logger
class WorkBotCLI(CLI):
    ''' Interactive CLI for WorkBot '''
    
    def __init__(self, workbot = None):

        self.workbot = workbot or WorkBot()
        super().__init__()

        # self.context = CommandContext(workbot=self.workbot)

# SHUTDOWN OVERRIDE
    def cmd_shutdown(self, args):
        self.workbot.craft_bot.close_session()
        super().cmd_shutdown()


# DOWNLOAD ORDERS
    def cmd_download_orders(self, args):
        """Handles downloading orders."""

        parser = self.args_download_orders()
        parsed_args = parser.parse_args(args)
        try:
            self.workbot.download_craftable_orders(parsed_args.stores, parsed_args.vendors)

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
        parser.add_argument('--stores', nargs='+', help='List of store names (default: all).')       
        parser.add_argument('--vendors', nargs='+', help='List of vendors (default: all).')
        parser.add_argument('--start_date', help='Start of date range for lookup (yyyy-mm-dd)')
        parser.add_argument('--end_date', help='End of date range for lookup (yyyy-mm-dd)')
        return parser
    
    def cmd_generate_vendor_upload_files(self, args):
        parser = self.args_generate_vendor_upload_files()
        try:
            parsed_args = parser.parse_args(args)

            paths = self.workbot.generate_vendor_upload_files(
                stores=parsed_args.stores,
                vendors=parsed_args.vendors,
                start_date=parsed_args.start_date,
                end_date=parsed_args.end_date
            )

            print('\nUpload files generated successfully.\n')
        except SystemExit:
            pass

    def _autocomplete_generate_vendor_upload_files(self, flag: str, text: str):
        
        flags = {
            '--stores': self._get_stores,
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
            self.workbot.delete_craftable_orders(parsed_args.stores, parsed_args.vendors)
            
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
            self.workbot.combine_orders(parsed_args.vendors)
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


# CONVERT ORDER TO TRANSFER
    def args_convert_order_to_transfer(self):
        parser = argparse.ArgumentParser(prog='convert_order_to_transfer', description='Find an order active order with the given store and vendor, and then convert it to a transfer.')
        parser.add_argument('--order_store', required=True, help='The store which the order belongs to.')
        parser.add_argument('--vendor', required=True, help='A single vendor name.')
        parser.add_argument('--store_from', required=True, help='The store the transfer should be sent from.')
        return parser
    
    def cmd_convert_order_to_transfer(self, args):

        try:
            parser = self.args_convert_order_to_transfer()
            parsed_args = parser.parse_args(args)
            self.workbot.convert_order_to_transfer(parsed_args.order_store, parsed_args.vendor, parsed_args.store_from)
        except SystemExit:
            pass

    def _autocomplete_convert_order_to_transfer(self, flag: str, text: str):
        flags = {
            '--order_store': self._get_stores,
            '--vendor': self._get_vendors,
            '--store_from': self._get_stores
        }
        
        return [option for option in flags.get(flag, [])() if option.startswith(text)]

    
# INPUT TRANSFERS
    def args_input_transfers(self):
        parser = argparse.ArgumentParser(prog='input_transfers', description='Input into Craftable all the transfers found in the Transfers Directory.')
        return parser

    def cmd_input_transfers(self, args):

        try:
            self.workbot.input_craftable_transfers()
        except SystemExit:
            pass

# ARCHIVE ORDERS
    def args_archive_orders(self):
        parser = argparse.ArgumentParser(prog='archive_orders', description='Archives all current, un-archived orders.')
        parser.add_argument('--stores', nargs='+', required=True, help='List of stores.')
        parser.add_argument('--vendors', nargs='+', help='List of vendors.')
        return parser
    
    def cmd_archive_orders(self, args):

        try:
            parser = self.args_archive_orders()
            parsed_args = parser.parse_args(args)
            self.workbot.archive_all_current_orders(parsed_args.stores, parsed_args.vendors)
        except SystemExit:
            pass

    def _autocomplete_archive_orders(self, flag: str, text: str):
        flags = {
            '--stores': self._get_stores,
            '--vendors': self._get_vendors
        }
        
        return [option for option in flags.get(flag, [])() if option.startswith(text)]


    
# PRIVATE FUNCTIONS    
    def _get_stores(self):
        return [store.name for store in self.workbot.store_coordinator.list_stores()]
    
    def _get_vendors(self):
        return sorted(self.workbot.store_coordinator.list_vendors())

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


# UPDATE SMALLWARES PICKLIST
    def args_update_smallwares_picklist(self):
        parser = argparse.ArgumentParser(prog='update_smallwares_picklist', description='Pull orders from Webstaurant history and update pick list.')
        return parser

    def cmd_update_smallwares_picklist(self, args):

        try:
            webstaurant_bot = self.workbot.vendor_manager.initialize_vendor('Webstaurant', driver=self.workbot.craft_bot.driver)
            undocumented_orders = webstaurant_bot.get_all_undocumented_orders()

            for order in reversed(undocumented_orders): # Go backwards to implicitly sort by ascending date
                order_info = webstaurant_bot.get_order_info(order, download_invoice=True)
                webstaurant_bot.update_pick_list(order_info)
            
            print('\nPicklist updated successfully.\n')

        except SystemExit:
            pass
        except Exception as e:
            print('Something went wrong...')
            print(f'Here\'s a hint: {e}')

# GENERATE ORDER EMAILS FOR STORES
    def args_generate_store_order_emails(self):
        parser = argparse.ArgumentParser(prog='generate_store_order_emails', description='Create an email to send to stores listing out their orders for the week.')
        parser.add_argument('--stores', nargs='+', required=True, help='List of stores.')
        return parser

    def cmd_generate_store_order_emails(self, args):
        try:
            parser = self.args_generate_store_order_emails()
            parsed_args = parser.parse_args(args)
            self.workbot.generate_store_order_emails(stores=parsed_args.stores)
            print('\nDisplaying Emails\n')
        except SystemExit:
            pass
        except Exception as e:
            print(e)
    
    def _autocomplete_generate_store_order_emails(self, flag: str, text: str):
        flags = {
            '--stores': self._get_stores,
        }
        
        return [option for option in flags.get(flag, [])() if option.startswith(text)]

# PRINT WEEKLY SCHEDULE
    def args_print_weekly_schedule(self):
        parser = argparse.ArgumentParser(prog='print_weekly_schedule', description='Print the standard weekly schedule (1 sheet per day).')
        return parser

    def cmd_print_weekly_schedule(self, args):
        pass



    def args_split_natalies(self) -> None:
        return argparse.ArgumentParser(prog='sort_orders', description='Sort the saved orders by vendor.')
    
    def cmd_split_natalies(self, args):
        parser = self.args_sort_orders()

        try:    
            self.workbot.split_natalies()
            print('All Natalie Juices split.')
        except SystemExit:
            pass
