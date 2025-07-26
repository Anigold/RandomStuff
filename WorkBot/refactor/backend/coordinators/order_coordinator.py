from backend.storage.file.order_file_handler import OrderFileHandler
from backend.storage.file.download_handler import DownloadHandler
from backend.storage.database.order_database_handler import OrderDatabaseHandler
from backend.exporters.exporter import Exporter
from backend.exporters.adapters.exporter_adapter import ExportAdapter
from backend.parsers.order_parser import OrderParser
from backend.models.order import Order
from backend.utils.logger import Logger
from pathlib import Path

@Logger.attach_logger
class OrderCoordinator:
    def __init__(self):
        self.file_handler     = OrderFileHandler()
        self.db_handler       = OrderDatabaseHandler()
        self.parser           = OrderParser()
        self.download_handler = DownloadHandler()

    # def import_order(self, order: Order, save_excel=True, persist_db=True) -> None:
    #     if save_excel:
    #         self.file_handler.save_order(order)
    #     if persist_db:
    #         self.db_handler.upsert_order(order)


    def save_order_file(self, order: Order, format: str = 'excel'):
        self.file_handler.save_order(order, format)

    def get_orders_from_file(self, stores=None, vendors=None):
        return self.file_handler.get_order_files(stores, vendors)

    def get_orders_from_db(self, store, vendor):
        return self.db_handler.get_orders(store, vendor)

    def check_and_update_order(self, order: Order) -> bool:
        """
        If the given order differs from the existing one on file,
        remove the existing file and return False (new save required).
        Return True if the file already exists and is identical.
        """
        file_path = self.file_handler.get_order_file_path(order)

        if not file_path.exists():
            self.logger.info(f'[Order Update] No existing file at {file_path}. Proceeding with save.')
            return False

        try:
            existing_order = self.file_handler.read_order(file_path)
        except Exception as e:
            self.logger.warning(f'[Order Update] Failed to read existing order file: {e}. Proceeding with overwrite.')
            return False

        if self._orders_are_equal(existing_order, order):
            self.logger.info(f'[Order Update] Order is unchanged. Skipping overwrite.')
            return True

        self.logger.info(f'[Order Update] Order has changed. Removing old file.')
        self.file_handler.remove_file(file_path)
        self.file_handler.remove_file(file_path.with_suffix('.pdf'))

        return False

    def _orders_are_equal(self, order1: Order, order2: Order) -> bool:
        """
        Compares two Order objects by metadata and item content.
        - store, vendor, and date must match exactly
        - item lists must contain the same elements (ignoring order)
        """
        if (
            order1.store != order2.store or
            order1.vendor != order2.vendor or
            order1.date != order2.date
        ):
            return False

        def item_to_tuple(item):
            return (
                item.sku,
                item.name,
                float(item.quantity),
                float(item.cost_per),
                float(item.total_cost)
            )

        items1 = set(map(item_to_tuple, order1.items))
        items2 = set(map(item_to_tuple, order2.items))

        return items1 == items2

    def expect_downloaded_pdf(self, order: Order) -> None:
        """
        Registers a one-time callback for when the PDF download completes.
        """
        def handle_downloaded_file(file: Path):
            dest = self.file_handler.get_order_file_path(order, format='pdf')
            self.file_handler.move_file(file, dest, overwrite=True)
            self.logger.info(f"Moved downloaded PDF to: {dest}")

        self.download_handler.on_download_once(
            match_fn=lambda f: f.name == "Order.pdf",
            callback=handle_downloaded_file,
            timeout=10
        )

    def read_order_file(self, file_path: Path) -> Order:
        return self.file_handler.read_order(file_path)
    
    def generate_vendor_upload_file(self, order: Order) -> Path:
        """
        Generates and saves a vendor-specific upload file for the given order.
        Returns the path to the saved file.
        """
        adapter = ExportAdapter.get_adapter(order.vendor)
        format = adapter.preferred_format

        exporter = Exporter.get_exporter(Order, format)
        file_data = exporter.export(order, adapter=adapter)

        output_path = self.file_handler.get_upload_files_path(order, format)
        self.file_handler._write_data(format, file_data, output_path)

        return output_path
    
    def generate_vendor_upload_files(
        self,
        stores: list[str],
        vendors: list[str],
        start_date: str = None,
        end_date: str = None
    ) -> list[Path]:
        """
        Finds all matching orders and generates vendor-specific upload files for each.
        Returns the list of output file paths.
        """
        file_paths = self.file_handler.get_order_files(
            stores=stores,
            vendors=vendors,
            start_date=start_date,
            end_date=end_date
        )

        output_paths = []
        for file_path in file_paths:

            order = self.read_order_file(file_path)
            output_path = self.generate_vendor_upload_file(order)
            output_paths.append(output_path)

        return output_paths
    

    def archive_order_file(self, order: Order) -> None:
        self.file_handler.archive_order_file(order)