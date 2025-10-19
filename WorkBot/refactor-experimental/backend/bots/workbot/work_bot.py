from datetime import datetime
import socket
from collections import defaultdict
from pathlib import Path



from openpyxl import load_workbook



from backend.infra.logger import Logger




from backend.bots.craftable_bot.helpers import get_craftable_username_password



from backend.bots.craftable_bot.craftable_bot import CraftableBot

from backend.app.services import (
    OrderServices,
    VendorServices,
    StoreServices,
    EmailServices,
    FileLocator
)



from backend.domain.models import (
    Order,
    Transfer, TransferItem,
    Vendor,
    Store
)




from backend.adapters.emailer.emailer import Emailer, Email
from backend.adapters.emailer.services.gmail_service import GmailService
from backend.adapters.emailer.services.outlook_service import OutlookService
from backend.adapters.emailer.registry import EmailProviderRegistry


from backend.adapters.downloads.threaded_download_adapter import ThreadedDownloadAdapter


from backend.adapters.repos.order_file_repository import OrderFileRepository
from backend.adapters.repos.vendor_file_repository import VendorFileRepository
from backend.adapters.repos.store_file_repository import StoreFileRepository



from backend.infra.paths import (
    ORDER_FILES_DIR,
    DOWNLOADS_PATH,
    VENDOR_FILES_DIR,
    STORE_FILES_DIR,
    UPLOAD_FILES_DIR
    )

from typing import List


@Logger.attach_logger
class WorkBot:
 
    def __init__(self):
        self.logger.info('Initializing WorkBot...')

        self.orders, self.vendors, self.stores = self._init_domain_services()

        self.craft_bot = self._init_craftable_bot()

        self.locator = FileLocator(
            orders_repo=self.orders.repo,
            vendors_repo=self.vendors.repo,
            stores_repo=self.stores.repo
        )

        self.emails = self._init_email_services()

        self.logger.info('WorkBot initialized successfully.')

    def _init_domain_services(self) -> None:

        downloader = ThreadedDownloadAdapter(watch_dir=DOWNLOADS_PATH)

        orders = OrderServices(
            repo=OrderFileRepository(base_dir=ORDER_FILES_DIR, uploads_dir=UPLOAD_FILES_DIR),
            downloads=downloader
        )

        vendors = VendorServices(
            repo=VendorFileRepository(base_dir=VENDOR_FILES_DIR),
            downloads=downloader
        )

        stores = StoreServices(
            repo=StoreFileRepository(base_dir=STORE_FILES_DIR),
            downloads=downloader
        )

        return orders, vendors, stores

    def _init_craftable_bot(self) -> None:
        username, password = get_craftable_username_password()
        return CraftableBot(username, password, orders=self.orders)

    def _init_email_services(self) -> EmailServices:
        """Initialize email subsystem (emailer + service)."""
        try:
            provider = EmailProviderRegistry.get("outlook")
            emailer = Emailer(provider)
            self.logger.info("Emailer initialized using provider: outlook")
        except Exception as e:
            self.logger.warning(f"Emailer could not be initialized ({e}); continuing without email support.")
            emailer = None

        return EmailServices(
            emailer=emailer,
            orders=self.orders,
            vendors=self.vendors,
            locator=self.locator,
        )


    def download_craftable_orders(self, stores, vendors=[], download_pdf=True, update=True):
        return self.craft_bot.download_orders(stores, vendors, download_pdf=download_pdf, update=update)

    def delete_craftable_orders(self, stores, vendors=[]):
        return self.craft_bot.delete_orders(stores, vendors)

    def input_craftable_transfers(self):
        transfers = self.get_transfers()
        return self.craft_bot.input_transfers(transfers)

    def download_audits(self, stores: list[str], start_date: str, end_date: str) -> None:
        self.craft_bot.download_audits(stores, start_date, end_date)


    def get_orders(self, stores: list[str], vendors: list[str]) -> list[Order]:
        self.logger.info(f'Retrieving orders for: stores={stores}, vendors={vendors}')
        return self.orders.get_orders(stores=stores, vendors=vendors)

    def archive_all_current_orders(self, stores: list[str] = None, vendors: list[str] = None) -> None:
        vendors = vendors or []

        orders = self.get_orders(stores, vendors, formats=['xlsx'])

        for order in orders:
            try:
                self.orders.archive_order_file(order)
            except Exception as e:
                self.logger.warning(f'[Archive] Skipped {order}: {e}')

    def combine_orders(self, vendors: list) -> None:
        return self.orders.combine_orders(vendors)

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


    def generate_vendor_upload_files(
        self,
        stores: list[str],
        vendors: list[str],
        start_date: str = None,
        end_date: str = None
    ) -> list[Path]:

        self.logger.info(f'Generating vendor upload files for stores={stores}, vendors={vendors}, '
                         f'start_date={start_date}, end_date={end_date}')

        orders = self.get_orders(stores, vendors)
        self.logger.info(f'Found {len(orders)} orders to process.')

        context_map = {}
        for order in orders:
    
            vendor_info = self.vendors.get_vendor(order.vendor)

            context_map[order] = {
                'store':       order.store,
                'vendor_info': vendor_info,
                'date_str':    order.date,
            }

        self.logger.debug(f'Context map built with {len(context_map)} entries. Delegating to OrderServices.')

        result_paths = self.orders.generate_vendor_uploads(
            vendors=vendors,
            stores=stores,
            start_date=start_date,
            end_date=end_date,
            context_map=context_map
        )

        self.logger.info(f'Vendor upload file generation complete. {len(result_paths)} files created.')

        return result_paths

    def generate_vendor_order_emails(self, vendors: list[str], stores: list[str] = []) -> list[Email]:
        return self.emails.send_vendor_order_emails(stores=stores, vendors=vendors)

    def generate_store_order_emails(self, stores: list[str]):
        return self.emails.send_store_order_emails(stores=stores)


    def list_all_vendors(self) -> List[Vendor]:
        return self.vendors.list_vendors()
    
    def list_all_stores(self) -> List[Store]:
        return self.stores.list_stores()
    
    def get_vendor_information(self, vendor_name: str) -> Vendor:
        return self.vendors.get_vendor(vendor_name)

    def get_store_information(self, store_name: str) -> dict:
        return self.stores.get_store(store_name)

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
            for item in order.items:
                if 'Natalie' in item.name:
                    flavor = item.name.split(' - ')[1]
                    if flavor in flavors:
                        row = flavors.index(flavor) + 4
                        col = store_indices.get(order.store, None)
                        if col:
                            sheet.cell(row=row, column=col).value = item.quantity

        workbook.save('C:/Users/Will/Desktop/Natalies.xlsx')
