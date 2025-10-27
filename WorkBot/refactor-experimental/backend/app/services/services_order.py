from __future__ import annotations
from dataclasses import dataclass

from backend.app.ports import (
    OrderRepository, 
    DownloadPort
)

from backend.app.application.orders import *

@dataclass
class OrderServices:

    repo:      OrderRepository
    downloads: DownloadPort

    def __post_init__(self) -> None:
        
        self.list_orders          = ListOrders(self.repo)
        self.get_orders_by_vendor = GetOrdersByVendor(self.repo)
        self.get_orders_by_store  = GetOrdersByStore(self.repo)
        self.get_order            = GetOrder(self.repo)
        self.get_orders           = GetOrders(self.repo, self.get_order)

        self.save_order     = SaveOrder(self.repo)
        self.remove_order   = RemoveOrder(self.repo)
        self.combine_orders = CombineOrders(self.repo)

        self.generate_vendor_upload  = GenerateVendorUploadFile(self.repo)
        self.generate_vendor_uploads = GenerateVendorUploadFiles(
            self.get_order,
            self.generate_vendor_upload
        )

        self.expect_downloaded_pdf = ExpectDownloadedPdf(self.repo, self.downloads)
        self.check_and_update_order = CheckAndUpdateOrder(self.repo)

        self.generate_store_order_email = GenerateStoreOrderEmail(self.repo)
        self.generate_store_order_emails = GenerateStoreOrderEmails(self.repo, self.generate_store_order_email)
