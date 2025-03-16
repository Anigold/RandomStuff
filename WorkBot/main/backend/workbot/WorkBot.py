from backend.logger.Logger import Logger

from backend.vendors.VendorManager import VendorManager
from backend.stores.StoreManager import StoreManager
from backend.ordering.OrderManager import OrderManager
from backend.ordering.Order import Order
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
import sys
import subprocess

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
            transfer_item = TransferItem(name=item.name, quantity=item.quantity)
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
            vendor_bot = self.vendor_manager.initialize_vendor(order.vendor, driver=self.craft_bot.driver)

            # Need to deconstruct the OrderItem objects to pass into the vendor bot
            order_items = [order_item.to_dict() for order_item in order.items]
            
            formatted_file_prefix = self.order_manager.FILE_PREFIXES['formatted']
            save_path = self.order_manager.get_vendor_orders_directory(order.vendor) / f'{formatted_file_prefix}{self.order_manager.generate_filename(order)}'
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

    def combine_orders(self, vendors: list) -> None:
        self.order_manager.combine_orders(vendors)

    def shutdown(self) -> None:
        """Exits the CLI loop."""
        self.close_craftable_session()
        print("Exiting WorkBot CLI.")
        exit()