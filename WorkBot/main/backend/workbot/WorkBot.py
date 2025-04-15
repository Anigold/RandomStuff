from backend.logger.Logger import Logger

from backend.vendors.VendorManager import VendorManager
from backend.stores.StoreManager import StoreManager
from backend.ordering.OrderManager import OrderManager
from backend.ordering.Order import Order
from backend.transferring.TransferManager import TransferManager
from backend.transferring.Transfer import Transfer, TransferItem
from backend.craftable_bot.CraftableBot import CraftableBot
from backend.craftable_bot.helpers import generate_craftablebot_args
from backend.emailer.Emailer import Emailer, Email
from backend.emailer.Services.Gmail import GmailService
from backend.emailer.Services.Outlook import OutlookService

from backend.helpers.DatetimeFormattingHelper import string_to_datetime
import backend.config as config

from pathlib import Path
from datetime import datetime
import argparse
import json
import shlex
import sys
import subprocess
import socket
from collections import defaultdict

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

               # Establish host service
        
        # Establish emailer service based on which computer we're one.
        # We will move this to config later.
        email_host = socket.gethostname()
        if email_host == 'Purchasing':
            self.emailer = Emailer(OutlookService())
        else:
            self.emailer = Emailer(GmailService())   

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
        
        today = self._get_today_date_and_day()

        return f'''
{today[1]}, {today[0]}
'''
        print('Welcome!')
        print(f'Today is: {today[1]}, {today[0]}')

    def get_orders(self, stores: list, vendors: list = []) -> list:
        return self.order_manager.get_store_orders(stores=stores, vendors=vendors)

    def get_vendor_information(self, vendor_name: str) -> dict:
        return self.vendor_manager.get_vendor_information(vendor_name)

    def combine_orders(self, vendors: list) -> None:
        self.order_manager.combine_orders(vendors)

    def generate_vendor_order_emails(self, vendors: list[str], stores: list[str] = []) -> list[Email]:
        # print(f"\n🔍 Gathering orders for vendors: {vendors} and stores: {stores}...")
        orders = self.get_orders(stores=stores, vendors=vendors)

        if not orders:
            # print("⚠️  No orders found for the given vendors/stores.")
            return []

        # Group orders by vendor
        vendor_orders = defaultdict(list)
        for order in orders:
            vendor_orders[order.vendor].append(order)

        emails = []

        for vendor, orders in vendor_orders.items():
            # print(f"\n📦 Creating consolidated email for vendor: {vendor}")
            vendor_info = self.get_vendor_information(vendor)
            to_emails = vendor_info.get("email_contacts", ["default@vendor.com"])
            # print(f"📨 Sending to: {to_emails}")

            date_str = datetime.now().strftime("%B %d, %Y")
            subject = f"Orders for {vendor} ({date_str})"

            full_body = [f"Hello {vendor},", "", f"Please find below our orders for {date_str}:"]
            attachments = []

            for order in orders:
                full_body.append(f"\nStore: {order.store}")
                for item in order.items:
                    full_body.append(f"  - {item.quantity} x {item.name}")

                pdf_dir = self.order_manager.get_vendor_orders_directory(order.vendor)
                pdf_filename = f"{self.order_manager.generate_filename(order, file_extension='.pdf')}"
                pdf_path = pdf_dir / pdf_filename

                if pdf_path.exists():
                    # print(f"📎 Found PDF for {order.store}: {pdf_path}")
                    attachments.append(str(pdf_path))
                else:
                    pass
                    # print(f"⚠️  Missing PDF for {order.store}: {pdf_path}")

            full_body.extend((
                "", "Let us know if there are any issues.",
                "", "Thank you,", "Your Team"
            ))

            email = Email(
                to=tuple(to_emails),
                subject=subject,
                body="\n".join(full_body),
                attachments=tuple(attachments) if attachments else None
            )

            self.emailer.create_email(email)
            emails.append(email)
            # print("✅ Consolidated email created.")

        # print(f"\n📬 {len(emails)} consolidated email(s) generated.\n")

        for email in emails:
            # print("🧾 Displaying email:")
            self.emailer.display_email(email)

        return emails



    def shutdown(self) -> None:
        """Exits the CLI loop."""
        self.close_craftable_session()
        print("Exiting WorkBot CLI.")
        exit()





    def _get_today_date_and_day(self):
        today = datetime.today()
        day_of_week = today.strftime("%A")
        day = today.day
        suffix = "th" if 11 <= day <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
        long_date = today.strftime(f"%B {day}{suffix}, %Y")
        return long_date, day_of_week