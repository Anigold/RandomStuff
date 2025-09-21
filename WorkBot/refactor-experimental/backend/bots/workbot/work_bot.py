# region ---- IMPORTS ----

# region Standard Library
from datetime import datetime
import socket
from collections import defaultdict
from pathlib import Path
# endregion

# region Third-Party
from openpyxl import load_workbook
# endregion

# region Utilities
from backend.infra.logger import Logger

# endregion

# region Helpers
from backend.bots.bot_mixins import SeleniumBotMixin
from backend.bots.craftable_bot.helpers import get_craftable_username_password
# endregion

# region Application Services
from backend.bots.craftable_bot.craftable_bot import CraftableBot
from backend.app.services.services_order import OrderServices
# endregion

# region Models
from backend.domain.models.order import Order
from backend.domain.models.transfer import Transfer
from backend.domain.models.transfer_item import TransferItem
# endregion

# from backend.depricated_coordinators.vendor_coordinator import VendorCoordinator
# from backend.depricated_coordinators.item_coordinator import ItemCoordinator
# from backend.depricated_coordinators.order_coordinator import OrderCoordinator
# from backend.depricated_coordinators.store_coordinator import StoreCoordinator
# from backend.depricated_coordinators.transfer_coordinator import TransferCoordinator

# region Email Services
from backend.adapters.emailer.emailer import Emailer, Email
from backend.adapters.emailer.services.gmail_service import GmailService
from backend.adapters.emailer.services.outlook_service import OutlookService
# endregion

from backend.adapters.files.order_file_adapter import OrderFileAdapter
# from backend.app.repos.order_repo_adapter import OrderRepositoryAdapter
from backend.adapters.downloads.threaded_download_adapter import ThreadedDownloadAdapter
# endregion

from backend.infra.paths import ORDER_FILES_DIR, DOWNLOADS_PATH

# region ---- WORKBOT CLASS ----

@Logger.attach_logger
class WorkBot:

    # region ---- Initialization ----
    
    def __init__(self):
        self.logger.info('Initializing WorkBot...')

        # These will be replaced by the Services
        # self.vendor_coordinator   = VendorCoordinator()
        # # self.order_coordinator    = OrderCoordinator()
        # self.store_coordinator    = StoreCoordinator()
        # self.transfer_coordinator = TransferCoordinator()

        files     = OrderFileAdapter(base_dir=ORDER_FILES_DIR)
        # repo      = OrderRepositoryAdapter()
        downloads = ThreadedDownloadAdapter(watch_dir=DOWNLOADS_PATH)

        self.orders = OrderServices(
            files=files,
            repo=None,
            downloads=downloads
        )

        username, password = get_craftable_username_password()

        self.craft_bot = CraftableBot(
            username,
            password,
            orders=self.orders

        )

        # Host-based conditional setup
        email_host = socket.gethostname()
        self.emailer = Emailer(OutlookService()) if email_host == 'Purchasing' else None  

        self.logger.info('WorkBot initialized successfully.')

    # endregion

    # region ---- Order Management ----

    def download_craftable_orders(self, stores, vendors=[], download_pdf=True, update=True):
        self.craft_bot.download_orders(stores, vendors, download_pdf=download_pdf, update=update)

    # def sort_orders(self):
    #     self.order_coordinator.sort_orders()

    def delete_craftable_orders(self, stores, vendors=[]):
        self.craft_bot.delete_orders(stores, vendors)

    def get_order_files(self, stores: list, vendors: list = [], formats: list[str] = None) -> list[Path]:
        self.logger.info(f'Retrieving order files for: stores=[{stores}], vendors=[{vendors}], formats=[{formats}]')
        return self.orders.get_order_files(stores=stores, vendors=vendors, formats=formats)

    def get_orders(self, stores: list[str], vendors: list[str], formats: list[str] = None) -> list[Order]:
        self.logger.info(f'Retrieving orders for: stores=[{stores}], vendors=[{vendors}], formats=[{formats}]')
        order_files = self.get_order_files(stores, vendors, formats=formats)
        return self.orders.read_orders_from_file(order_files)

    def archive_all_current_orders(self, stores: list[str] = None, vendors: list[str] = None) -> None:
        vendors = vendors or []

        orders = self.get_orders(stores, vendors, formats=['xlsx'])

        for order in orders:
            try:
                self.orders.archive_order_file(order)
            except Exception as e:
                self.logger.warning(f'[Archive] Skipped {order}: {e}')

    def combine_orders(self, vendors: list) -> None:
        self.orders.combine_orders(vendors)

    # endregion

    # region ---- Transfer Management ----

    def get_transfers(self, stores: list[str] = None, start_date: str = None, end_date: str = None) -> list[Transfer]:
        '''
        Retrieves saved transfer objects from file based on optional filters.

        Args:
            stores (list[str], optional): List of store names to filter by.
            start_date (str, optional): Start date filter in YYYY-MM-DD format.
            end_date (str, optional): End date filter in YYYY-MM-DD format.

        Returns:
            list[Transfer]: List of parsed transfer domain objects.
        '''
        return self.transfer_coordinator.get_transfers_from_file(
            stores=stores,
            start_date=start_date,
            end_date=end_date
        )
    
    def input_craftable_transfers(self):
        transfers = self.get_transfers()

        self.craft_bot.input_transfers(transfers)

    def convert_order_to_transfer(self, destination, vendor, origin):
        self.logger.info(f'Beginning order-transfer conversion: {destination}-{vendor} -> {origin}')
        order = self.get_orders([destination], [vendor], formats=['xlsx'])[0]
        origin = 'Bakery' if order.vendor == 'Ithaca Bakery' else order.vendor # YOU NEED TO FIX THIS FOR WHEN YOU HAVE TO DO IT FOR A DIFFERENT STORE

        transfer_items = [
            TransferItem(name=item.name, quantity=item.quantity)
            for item in order.items
        ]

        transfer = Transfer(
            transfer_items=transfer_items,
            origin=origin,
            destination=order.store,
            transfer_date=order.date
        )

        return self.transfer_coordinator.save_transfer(transfer=transfer)

    # endregion

    # region ---- Vendor Uploads ----

    def generate_vendor_upload_files(
        self,
        stores: list[str],
        vendors: list[str],
        start_date: str = None,
        end_date: str = None
    ) -> list[Path]:

        self.logger.info(f'Generating vendor upload files for stores={stores}, vendors={vendors}, '
                         f'start_date={start_date}, end_date={end_date}')

        order_file_paths = self.get_order_files(stores=stores, vendors=vendors, formats=['xlsx'])
        self.logger.info(f'Found {len(order_file_paths)} order files to process.')

        context_map = {}
        for file_path in order_file_paths:
            order = self.orders.read_order_from_file(file_path)
            vendor_info = self.vendor_coordinator.get_vendor_information(order.vendor)

            context_map[str(file_path)] = {
                'store':       order.store,
                'vendor_info': vendor_info,
                'date_str':    order.date,
            }

        self.logger.debug(f'Context map built with {len(context_map)} entries. Delegating to OrderCoordinator.')

        result_paths = self.orders.generate_vendor_uploads(
            stores=stores,
            vendors=vendors,
            start_date=start_date,
            end_date=end_date,
            context_map=context_map
        )

        self.logger.info(f'Vendor upload file generation complete. {len(result_paths)} files created.')

        return result_paths

    # endregion

    # region ---- Emailing: Vendor-Facing ----

    def generate_vendor_order_emails(self, vendors: list[str], stores: list[str] = []) -> list[Email]:
        orders = self.get_orders(stores=stores, vendors=vendors, formats=['xlsx'])
        if not orders:
            return []

        grouped_orders = self._group_orders_by_vendor(orders)
        emails = []

        for vendor_name, vendor_orders in grouped_orders.items():
            to_emails   = self._get_vendor_recipients(vendor_name)
            subject     = self._build_email_subject(vendor_name)
            body        = self._build_vendor_email_body(vendor_name, vendor_orders)
            attachments = self._get_email_attachments(vendor_orders)

            email = Email(
                to=tuple(to_emails),
                subject=subject,
                body=body,
                attachments=tuple(attachments) if attachments else None
            )

            self.emailer.create_email(email)
            self.emailer.display_email(email)
            emails.append(email)

        return emails

    def _group_orders_by_vendor(self, orders: list) -> dict:
        grouped = defaultdict(list)
        for order in orders:
            grouped[order.vendor].append(order)
        return grouped

    def _build_email_subject(self, vendor_name: str) -> str:
        date_str = datetime.now().strftime('%B %d, %Y')
        return f'Orders for {vendor_name} ({date_str})'

    def _get_vendor_recipients(self, vendor_name: str) -> list[str]:
        try:
            vendor_info = self.vendor_coordinator.get_vendor_info(vendor_name)
            if vendor_info.ordering.email:
                return [vendor_info.ordering.email]
        except Exception:
            pass
        return ['default@vendor.com']

    def _build_vendor_email_body(self, vendor_name: str, orders: list) -> str:
        date_str = datetime.now().strftime('%B %d, %Y')
        lines = [
            f'Hello {vendor_name},',
            '',
            f'Please find below our orders for {date_str}:'
        ]

        for order in orders:
            lines.append(f'\nStore: {order.store}')
            for item in order.items:
                lines.append(f'  - {item.quantity} x {item.name}')

        lines += [
            '', 'Let us know if there are any issues.',
            '', 'Thank you!', 
            '---',
            'Andrew Goldsmith', 
            'Purchasing Manager', 
            'Ithaca Bakery', 
            '(607) 273-7110'
        ]
        return '\n'.join(lines)

    def _get_email_attachments(self, orders: list[Order]) -> list[str]:
        attachments = []
        for order in orders:
            pdf_file_path = self.orders.get_order_files(order, format='pdf')

            if pdf_file_path.exists():
                attachments.append(str(pdf_file_path))

        return attachments

    # endregion

    # region ---- Emailing: Store-Facing ----

    def generate_store_order_emails(self, stores: list[str]):
        orders = self.get_order_files(stores=stores, vendors=[], formats=['pdf'])
   
        if not orders: return None

        emails = []
        store_orders_table = defaultdict(list)
        for order in orders:
            order_meta_data = self.orders.parse_filename_for_metadata(order.name)
            store_orders_table[order_meta_data['store']].append(order)

        for store, store_orders in store_orders_table.items():
            to_emails = [
                contact['email']
                for contact in self.get_store_information(store).contacts
                if contact['title'] == 'Inventory Clerk'
            ]

            subject = f'Orders for the Week: {store}'
            attachments = [store_order for store_order in store_orders]

            body = 'Hello, here are the orders you have placed for the week.'

            email = Email(
                to=tuple(to_emails),
                subject=subject,
                body=body,
                cc='jennithacabakery@gmail.com',
                attachments=tuple(attachments) if attachments else None
            )

            self.emailer.create_email(email)
            emails.append(email)

        
        for email in emails:
            self.emailer.display_email(email)

    # endregion

    # region ---- Utilities & Lifecycle ----

    def get_vendor_information(self, vendor_name: str) -> dict:
        return self.vendor_coordinator.get_vendor_information(vendor_name)

    def get_store_information(self, store_name: str) -> dict:
        return self.store_coordinator.find_store_by_name(store_name=store_name)

    def close_craftable_session(self):
        self.craft_bot.close_session()

    def welcome_to_work(self) -> str:
        today = self._get_today_date_and_day()
        return f'''\n{today[1]}, {today[0]}'''

    def shutdown(self) -> None:
        self.close_craftable_session()
        print('Exiting WorkBot CLI.')

    def _get_today_date_and_day(self):
        today = datetime.today()
        day_of_week = today.strftime('%A')
        day = today.day
        suffix = 'th' if 11 <= day <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
        long_date = today.strftime(f'%B {day}{suffix}, %Y')
        return long_date, day_of_week

    # endregion

    # region ---- Special Cases ----

    def split_natalies(self) -> None:
        natalies_excel_path = Path('C:/Users/Will/Desktop/Natalies.xlsx')
        workbook = load_workbook(natalies_excel_path)
        sheet = workbook.active

        flavors = [
            row[0].value for row in sheet.iter_rows()
            if row[0].value and row[0].value.strip()
        ]

        orders_files = self.orders.get_order_files(
            stores=['Bakery', 'Easthill', 'Collegetown', 'Triphammer', 'Downtown'],
            vendors=['Performance Food', 'FingerLakes Farms'],
            formats=['xlsx']
        )

        orders = [self.orders.read_order_from_file(order) for order in orders_files]

        store_indices = {
            'Collegetown': 2,
            'Downtown': 5,
            'Easthill': 8,
            'Triphammer': 11,
            'Bakery': 14
        }

        for order in orders:
            # order = self.order_coordinator.parse_filename_for_metadata(order_path.name)
            for item in order.items:
                if 'Natalie' in item.name:
                    flavor = item.name.split(' - ')[1]
                    if flavor in flavors:
                        row = flavors.index(flavor) + 4
                        col = store_indices.get(order.store, None)
                        if col:
                            sheet.cell(row=row, column=col).value = item.quantity

        workbook.save('C:/Users/Will/Desktop/Natalies.xlsx')

    # endregion





    def download_audits(self, stores: list[str], start_date: str, end_date: str) -> None:
        self.craft_bot.download_audits(stores, start_date, end_date)

        
# endregion