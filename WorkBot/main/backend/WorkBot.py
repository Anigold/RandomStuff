from backend.logger.Logger import Logger

from backend.vendors.VendorManager import VendorManager
from backend.stores.StoreManager import StoreManager
from backend.orders.OrderManager import OrderManager
from backend.orders.Order import Order
from backend.transferring.TransferManager import TransferManager
from backend.transferring.Transfer import Transfer, TransferItem
from backend.craftable_bot.CraftableBot import CraftableBot
from backend.craftable_bot.helpers import generate_craftablebot_args

from backend.helpers.DatetimeFormattingHelper import string_to_datetime
import backend.config as config

from pathlib import Path
from datetime import datetime
import argparse
import json
import shlex

from tabulate import tabulate
from termcolor import colored

from pprint import pprint

@Logger.attach_logger
class WorkBot:
    
    def __init__(self):

        self.logger.info('Initializing WorkBot...')
        
        self.vendor_manager   = VendorManager()
        self.order_manager    = OrderManager()
        self.store_manager    = StoreManager()
        self.transfer_manager = TransferManager()

        driver, username, password = generate_craftablebot_args(config.get_full_path('downloads'))
        self.craft_bot = CraftableBot(driver, username, password, 
                                      order_manager=self.order_manager, 
                                      transfer_manager=self.transfer_manager)
       
        self.logger.info('WorkBot initialized successfully.')

    def download_orders(self, stores, vendors=[], download_pdf=True, update=True):
        self.craft_bot.download_orders(stores, vendors, download_pdf=download_pdf, update=update)
    
    def sort_orders(self):
        self.order_manager.sort_orders()

    def delete_orders(self, stores, vendors=[]):
        self.craft_bot.delete_orders(stores, vendors)

    def input_transfers(self, transfers: list):
        self.craft_bot.input_transfers(transfers)

    def convert_order_to_transfer(self, order: Order) -> Transfer:
        '''This is so niche that we only need to use it once a week, but it removes tedium from my life so it stays.'''
        # print(order.items, flush=True)

        if order.vendor == 'Ithaca Bakery': 
            store_from = 'BAKERY'
        else:
            store_from = order.vendor

        transfer_items = []
        for item in order.items:
            transfer_item = TransferItem(name=item['Item'], quantity=float(item['Quantity']))
            transfer_items.append(transfer_item)

        order_datetime = string_to_datetime(order.date)

        return Transfer(
            store_from=store_from,
            store_to=order.store,
            date=order_datetime,
            items=transfer_items
            )

    def generate_vendor_upload_files(self, orders: list):

        for order in orders:
            vendor_bot = self.vendor_manager.initialize_vendor(order.vendor)

            # Need to deconstruct the OrderItem objects to pass into the vendor bot
            order_items = [order_item.to_dict() for order_item in order.items]
            
            save_path = self.order_manager.get_vendor_orders_directory('UNFI') / f'Formatted-{self.order_manager.generate_filename(order)}'
            vendor_bot.format_for_file_upload(order_items, save_path, order.store)

        return

    def close_craftable_session(self):
        self.craft_bot.close_session()

    def welcome_to_work(self) -> None:
        pass

    def get_orders(self, stores: list, vendors: list = []) -> list:
        return self.order_manager.get_store_orders(stores=stores, vendors=vendors)

    def get_vendor_information(self, vendor_name: str) -> dict:
        return self.vendor_manager.get_vendor_information(vendor_name)

@Logger.attach_logger
class WorkBotCLI:
    ''' Interactive CLI for WorkBot '''
    
    def __init__(self):

        self.workbot = WorkBot()

        self.commands = {
            "download_orders":              self.download_orders,
            'list_orders':                  self.list_orders,
            "sort_orders":                  self.sort_orders,
            'delete_orders':                self.delete_orders,
            'generate_vendor_upload_files': self.generate_vendor_upload_files,
            "shutdown":                     self.shutdown,
            "help":                         self.show_help,
            "exit":                         self.exit_cli,
        }

    def start(self):
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

            except KeyboardInterrupt:
                print("\nExiting WorkBot CLI.")
                self.exit_cli([])

    def download_orders(self, args):
        """Handles downloading orders."""
        parser = argparse.ArgumentParser(prog="download_orders", description="Download orders from vendors.")
        parser.add_argument("--stores", nargs="+", required=True, help="List of store names.")
        parser.add_argument("--vendors", nargs="+", help="List of vendors (default: all).")
        parser.add_argument('--sort', action='store_true', help='Sort orders by vendor after downloading.')
        try:
            parsed_args = parser.parse_args(args)
            self.workbot.download_orders(parsed_args.stores, parsed_args.vendors)

            if parsed_args.sort: self.workbot.sort_orders()
            
            print("Orders downloaded successfully.")
        except SystemExit:
            pass  # Prevent argparse from exiting CLI loop
    
    def sort_orders(self, args):
        parser = argparse.ArgumentParser(prog="sort_orders", description="Sort the saved orders by vendor.")

        try:    
            self.workbot.sort_orders()
            print('Orders sorted successfully.')
        except SystemExit:
            pass

    def list_orders(self, args):

        parser = argparse.ArgumentParser(prog='list_orders', description='List the saved orders.')
        parser.add_argument('--stores', nargs='+', required=True, help='List of store names.')
        parser.add_argument('--vendors', nargs='+', help='List of vendors (default: all).')
        parser.add_argument('--show_pricing', action='store_true', help='Display the total estimated price of the order.')
        parser.add_argument('--show_minimums', action='store_true', help='Display the vendor order minimums.')
        
        try:

            parsed_args      = parser.parse_args(args)
            
            orders           = self.workbot.get_orders(parsed_args.stores, parsed_args.vendors)
            formatted_orders = self._format_order_list(orders, parsed_args.show_pricing, parsed_args.show_minimums)
            print(formatted_orders)
        except SystemExit:
            pass

    def generate_vendor_upload_files(self, args):
        parser = argparse.ArgumentParser(prog='format_orders_for_upload', description='Generate a vendor-specific upload file.')
        parser.add_argument('--vendors', nargs='+', help='List of vendors (default: all).')

        try:
            parsed_args = parser.parse_args(args)

            for vendor in parsed_args.vendors:
                vendor_order_paths = self.workbot.order_manager.get_vendor_orders(vendor)

                orders = [OrderManager.create_order_from_excel(vendor_order_path) for vendor_order_path in vendor_order_paths]

                self.workbot.generate_vendor_upload_files(orders)

        except SystemExit:
            pass

    def delete_orders(self, args):
        parser = argparse.ArgumentParser(prog="download_orders", description="Download orders from vendors.")
        parser.add_argument("--stores", nargs="+", required=True, help="List of store names.")
        parser.add_argument("--vendors", nargs="+", help="List of vendors (default: all).")
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
                total_cost = sum(float(item['Total Cost']) for item in order.items if item['Total Cost']) if show_pricing else "N/A"
                formatted_orders[pos].append(f'${total_cost:.2f}')
        
        if show_minimums:
            headers.extend(['Min. Price', 'Min. Cases'])
            for pos, order in enumerate(orders):
                vendor_information = self.workbot.get_vendor_information(order.vendor)
                min_order_price = vendor_information['min_order_value']
                min_order_cases = vendor_information['min_order_cases']
                
                total_cost = sum(float(item['Total Cost']) for item in order.items if item['Total Cost']) if show_pricing else "N/A"
                
                # Check if the order meets vendor minimums
                below_min_value = total_cost < min_order_price
                below_min_cases = len(order.items) < min_order_cases

                total_cost_str = colored(f"${total_cost:.2f}", "red") if below_min_value else f"${total_cost:.2f}"
                min_order_value_str = colored(f"${min_order_price:.2f}", "red") if below_min_value else f"${min_order_price:.2f}"
                min_order_cases_str = colored(str(min_order_cases), "red") if below_min_cases else str(min_order_cases)

                formatted_orders[pos].extend([min_order_value_str, min_order_cases_str])

        return tabulate(formatted_orders, headers=headers, tablefmt="grid")

    def shutdown(self, args):
        """Shuts down WorkBot and all vendor sessions."""
        self.workbot.shutdown()
        print("WorkBot shut down successfully.")

    def show_help(self, args):
        """Displays available commands."""
        print("\nAvailable Commands:")
        print("  download_orders --stores [STORE_NAMES] --vendors [VENDORS] --sort   # Download orders from Craftable for specific stores/vendors")
        print('  list_orders --stores [STORE_NAMES] --vendors [VENDORS]              # Display orders for specific stores/vendors')
        print('  sort_orders                                                         # Sort order files by vendor')
        print('  delete_orders --stores [STORE NAMES] --vendors [VENDORS]            # Delete orders from Craftable for specific stores/vendors.')
        print('  generate_vendor_upload_files --vendors [VENDORS]                    # Generate vendor-specific upload files in the vendors\' order directory.')
        print("  help                                                                # Show available commands")
        print("  exit                                                                # Exit the CLI\n")

    def exit_cli(self, args):
        """Exits the CLI loop."""
        self.workbot.close_craftable_session()
        print("Exiting WorkBot CLI.")
        exit()