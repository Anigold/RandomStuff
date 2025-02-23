from backend.logger.Logger import Logger
from backend.vendors.VendorManager import VendorManager
from backend.stores.StoreManager import StoreManager
from backend.orders.OrderManager import OrderManager
from backend.orders.Order import Order
from backend.transferring.TransferManager import TransferManager
from backend.transferring.Transfer import Transfer, TransferItem

from backend.craftable_bot.CraftableBot import CraftableBot
from backend.craftable_bot.helpers import generate_craftablebot_args

import backend.config as config

from pathlib import Path
from datetime import datetime
import argparse

from tabulate import tabulate



class WorkBot:

    logger = Logger.get_logger('WorkBot', log_file='logs/work_bot.log')

    def __init__(self):

        self.logger.info('Initializing WorkBot...')

        self.vendor_manager   = VendorManager()
        self.order_manager    = OrderManager()
        self.store_manager    = StoreManager()
        self.transfer_manager = TransferManager()

        driver, username, password = generate_craftablebot_args(config.get_full_path('downloads'))
        self.craft_bot = CraftableBot(driver, username, password, 
                                      order_manager=self.order_manager, 
                                      transfer_manager=self.transfer_manager
                                      )
        
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

        return Transfer(
            store_from=order.vendor,
            store_to=order.store,
            date=order.date,
            items=frozenset(order.items)
            )

    def close_craftable_session(self):
        self.craft_bot.close_session()

    def welcome_to_work(self) -> None:
        pass

    def get_orders(self, stores: list, vendors: list = []) -> list:
        return self.order_manager.get_store_orders(stores=stores, vendors=vendors)




class WorkBotCLI:
    ''' Interactive CLI for WorkBot '''

    logger = Logger.get_logger('WorkBot CLI', log_file='logs/work_bot_CLI.log')

    def __init__(self):
        self.workbot = WorkBot()
        self.commands = {
            "download_orders": self.download_orders,
            'list_orders': self.list_orders,
            "sort_orders": self.sort_orders,
            "shutdown": self.shutdown,
            "help": self.show_help,
            "exit": self.exit_cli,
        }

    def start(self):
        """Starts the interactive command loop."""
        print("\nWelcome to WorkBot CLI! Type 'help' to see available commands.\n")

        while True:
            try:
                user_input = input("WorkBot> ").strip()

                if not user_input: continue

                args         = user_input.split()
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
        parser.add_argument('--show_pricing', action='store_true', description='Display the total estimated price of the order.')
        parser.add_argument('--show_minimums', action='store_true', description='Display the vendor order minimums.')
        
        # parser.add_argument('--sort_by', nargs=)
        try:
            parsed_args      = parser.parse_args(args)
            orders           = self.workbot.get_orders(parsed_args.stores, parsed_args.vendors)
            formatted_orders = self._format_order_list(orders)
            print(formatted_orders)
        except SystemExit:
            pass
        
    def _format_order_list(self, orders: list):

        orders.sort(key=lambda x: x.store)

        formatted_orders = []
        for order in orders:
            formatted_orders.append([order.store, order.vendor, order.date, len(order.items)])

        return tabulate(formatted_orders, headers=["Store", "Vendor", "Date", "Items"], tablefmt="grid")


    def shutdown(self, args):
        """Shuts down WorkBot and all vendor sessions."""
        self.workbot.shutdown()
        print("WorkBot shut down successfully.")

    def show_help(self, args):
        """Displays available commands."""
        print("\nAvailable Commands:")
        print("  download_orders --stores [STORE_NAMES] --vendors [VENDORS] --sort   # Download orders for specific stores/vendors")
        print('  list_orders --stores [STORE_NAMES] --vendors [VENDORS]              # Display orders for specific stores/vendors')
        print('  sort_orders                                                         # Sort order files by vendor')
        print("  shutdown                                                            # Shut down WorkBot and close sessions")
        print("  help                                                                # Show available commands")
        print("  exit                                                                # Exit the CLI\n")

    def exit_cli(self, args):
        """Exits the CLI loop."""
        self.workbot.close_craftable_session()
        print("Exiting WorkBot CLI.")
        exit()