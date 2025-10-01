from __future__ import annotations
from dataclasses import dataclass

from backend.app.ports import (
    OrderRepository, 
    DownloadPort
)

from backend.app.application.orders import *

@dataclass
class OrderServices:
    """
    Stable surface for CLI / API / schedulers.
    Wires ports into small, testable use-cases and exposes them as attributes.
    """
    repo:      OrderRepository
    downloads: DownloadPort

    def __post_init__(self) -> None:
        
        self.list_orders          = ListOrders(self.repo)
        self.get_orders_by_vendor = GetOrdersByVendor(self.repo)
        self.get_orders_by_store  = GetOrdersByStore(self.repo)
        self.get_order            = GetOrder(self.repo)

        self.save_order   = SaveOrder(self.repo)
        self.remove_order = RemoveOrder(self.repo)

        self.generate_vendor_upload  = GenerateVendorUploadFile(self.repo)
        self.generate_vendor_uploads = GenerateVendorUploadFiles(
            self.get_orders_by_vendor,
            self.generate_vendor_upload
        )

        self.expect_downloaded_pdf = ExpectDownloadedPdf(
            self.repo,
            self.downloads
        )

        self.check_and_update_order = CheckAndUpdateOrder(self.repo)

        # # Queries
        # self.get_order_files       = GetOrderFiles(self.repo)
        # self.read_order_from_file  = ReadOrderFromFile(self.repo)
        # self.read_orders_from_file = ReadOrdersFromFile(
        #     self.repo,
        #     self.read_order_from_file
        # )

        # # Commands
        # self.generate_vendor_upload  = GenerateVendorUploadFile(self.repo)
        # self.generate_vendor_uploads = GenerateVendorUploadFiles(
        #     get_paths=self.get_order_files,
        #     read_order=self.read_order_from_file,
        #     gen_upload=self.generate_vendor_upload,
        # )
        # self.save_order_to_file          = SaveOrderToFile(self.repo)
        # self.save_order_to_db            = SaveOrderToDB(self.repo)
        # self.archive_order_file          = ArchiveOrderFile(self.repo)
        # self.combine_orders              = CombineOrders(self.repo)
        # self.parse_filename_for_metadata = ParseFilenameForMetadata(self.repo)

        # # Download watcher (domain-specific wrapper over generic download plumbing)
        # self.expect_downloaded_pdf = ExpectDownloadedPdf(self.repo, self.downloads)

        # # Diff/validation
        # self.check_and_update_order = CheckAndUpdateOrder(self.repo)
