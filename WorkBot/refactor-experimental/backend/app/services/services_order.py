from __future__ import annotations
from dataclasses import dataclass

from backend.app.ports import (
    OrderFilePort, 
    OrderRepository, 
    DownloadPort
)

from backend.app.application.orders import (
    GetOrderFiles,
    ReadOrderFromFile,
    GenerateVendorUploadFile,
    GenerateVendorUploadFiles,
    SaveOrderToFile,
    SaveOrderToDB,
    ArchiveOrderFile,
    ExpectDownloadedPdf,
    CheckAndUpdateOrder,
    CombineOrders,
    ParseFilenameForMetadata,
    ReadOrdersFromFile,
)

@dataclass
class OrderServices:
    """
    Stable surface for CLI / API / schedulers.
    Wires ports into small, testable use-cases and exposes them as attributes.
    """
    files:     OrderFilePort
    repo:      OrderRepository
    downloads: DownloadPort

    def __post_init__(self) -> None:
        
        # Queries
        self.get_order_files       = GetOrderFiles(self.files)
        self.read_order_from_file  = ReadOrderFromFile(self.files)
        self.read_orders_from_file = ReadOrdersFromFile(
            self.files,
            self.read_order_from_file
        )

        # Commands
        self.generate_vendor_upload  = GenerateVendorUploadFile(self.files)
        self.generate_vendor_uploads = GenerateVendorUploadFiles(
            get_paths=self.get_order_files,
            read_order=self.read_order_from_file,
            gen_upload=self.generate_vendor_upload,
        )
        self.save_order_to_file          = SaveOrderToFile(self.files)
        self.save_order_to_db            = SaveOrderToDB(self.repo)
        self.archive_order_file          = ArchiveOrderFile(self.files)
        self.combine_orders              = CombineOrders(self.files)
        self.parse_filename_for_metadata = ParseFilenameForMetadata(self.files)

        # Download watcher (domain-specific wrapper over generic download plumbing)
        self.expect_downloaded_pdf = ExpectDownloadedPdf(self.files, self.downloads)

        # Diff/validation
        self.check_and_update_order = CheckAndUpdateOrder(self.files)
