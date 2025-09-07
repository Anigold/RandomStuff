from __future__ import annotations
from pathlib import Path
from typing import List, Optional, Callable
from backend.app.ports import OrderFilePort, OrderRepository, DownloadPort, DownloadCallback
from backend.storage.file.order_file_handler import OrderFileHandler
from backend.storage.database.order_database_handler import OrderDatabaseHandler
from backend.storage.file.download_handler import DownloadHandler
from backend.models.order import Order

class OrderFileAdapter(OrderFilePort):

    def __init__(self, impl: OrderFileHandler | None=None) -> None:
        self.impl = impl or OrderFileHandler()

    def get_order_directory(self) -> Path:
        return self.impl.get_order_directory()
    
    def get_order_file_path(self, order: Order, format: str="excel") -> Path:
        return self.impl.get_order_file_path(order, format=format)
    
    def parse_filename_for_metadata(self, file_name: str) -> dict:
        return self.impl.parse_filename_for_metadata(file_name=file_name)
    
    def get_order_files(
        self,
        stores: List[str],
        vendors: List[str],
        formats: Optional[List[str]]=None
    ) -> List[Path]:
        return self.impl.get_order_files(stores, vendors, formats=formats)
    
    def save_order(self, order: Order, format: str="excel") -> None:
        self.impl.save_order(order, format)
    
    def archive_order_file(self, order: Order) -> None:
        self.impl.archive_order_file(order)
    
    def get_order_from_file(self, file_path: Path) -> Order:
        return self.impl.get_order_from_file(file_path)
    
    def remove_file(self, file_path: Path) -> None:
        self.impl.remove_file(file_path)
    
    def move_file(self, src: Path, dest: Path, overwrite: bool=False) -> None:
        self.impl.move_file(src, dest, overwrite)
    
    def generate_vendor_upload_file(self, order: Order, context: dict | None=None) -> Path:
        return self.impl.generate_vendor_upload_file(order, context=context)
    
    def combine_orders_by_store(self, vendors: list[str]) -> Path | None:
        return self.impl.combine_orders_by_store(vendors)

class OrderRepositoryAdapter(OrderRepository):

    def __init__(self, impl: OrderDatabaseHandler | None=None) -> None:
        self.impl = impl or OrderDatabaseHandler()

    def save_order(self, order: Order) -> int:
        return self.impl.save_order(order)

