from __future__ import annotations
from dataclasses import dataclass
from typing import List
from datetime import datetime
from collections import defaultdict
from backend.domain.models import Order, Vendor
from backend.adapters.emailer.emailer import Emailer, Email
from backend.infra.logger import Logger
from .services_order import OrderServices
from .services_vendor import VendorServices


@Logger.attach_logger
@dataclass
class EmailServices:
    """
    Application-level service for all email-related use cases.
    Keeps email logic separate from domain logic.
    """

    emailer: Emailer
    orders:  OrderServices
    vendors: VendorServices

    # -------------------------------------------------------------------------
    # VENDOR-FACING EMAILS
    # -------------------------------------------------------------------------
    def send_vendor_order_emails(
        self, stores: List[str], vendors: List[str]
    ) -> List[Email]:
        """
        Generate and display emails to vendors with attached order files.
        """
        orders = self.orders.get_orders(vendors, stores)
        if not orders:
            self.logger.info("No orders found for vendor email dispatch.")
            return []

        grouped_orders = self._group_orders_by_vendor(orders)
        emails: list[Email] = []

        for vendor_name, vendor_orders in grouped_orders.items():
            try:
                vendor_info = self.vendors.get_vendor(vendor_name)
            except Exception as e:
                self.logger.warning(f"Could not fetch vendor info for {vendor_name}: {e}")
                continue

            to_addrs = [vendor_info.ordering.email] if vendor_info.ordering.email else []
            if not to_addrs:
                self.logger.warning(f"No ordering email for vendor {vendor_name}, skipping.")
                continue

            subject     = self._build_vendor_subject(vendor_name)
            body        = self._build_vendor_body(vendor_name, vendor_orders)
            attachments = self._get_vendor_attachments(vendor_orders)

            email = Email(
                to=tuple(to_addrs),
                subject=subject,
                body=body,
                attachments=tuple(attachments),
            )

            self.emailer.create_email(email)
            self.emailer.display_email(email)
            emails.append(email)

        self.logger.info(f"Prepared {len(emails)} vendor email(s).")
        return emails

    # -------------------------------------------------------------------------
    # STORE-FACING EMAILS
    # -------------------------------------------------------------------------
    def send_store_order_emails(self, stores: List[str]) -> List[Email]:
        """
        Generate and display emails to stores with their weekly order summaries.
        """
        orders = []
        for store in stores:
            orders += self.orders.get_orders_by_store(store=store)

        grouped_orders = self._group_orders_by_store(orders)
        emails: list[Email] = []
  
        for store_name, store_orders in grouped_orders.items():
            subject = f"Orders for the Week: {store_name}"
            body = self._build_store_body(store_name, store_orders)
            attachments = self._get_store_attachments(store_orders)

            email = Email(
                to=("store@example.com",),  # TODO: retrieve from StoreRepository
                subject=subject,
                body=body,
                attachments=tuple(attachments),
            )
           
            self.emailer.create_email(email)
            self.emailer.display_email(email)
            emails.append(email)
        
        self.logger.info(f"Prepared {len(emails)} store email(s).")
        return emails

    # -------------------------------------------------------------------------
    # INTERNAL HELPERS
    # -------------------------------------------------------------------------
    def _group_orders_by_vendor(self, orders: List[Order]) -> dict[str, list[Order]]:
        grouped = defaultdict(list)
        for order in orders:
            grouped[order.vendor].append(order)
        return grouped

    def _group_orders_by_store(self, orders: List[Order]) -> dict[str, list[Order]]:
        grouped = defaultdict(list)
        for order in orders:
            grouped[order.store].append(order)
        return grouped

    def _build_vendor_subject(self, vendor_name: str) -> str:
        today = datetime.now().strftime("%B %d, %Y")
        return f"Orders for {vendor_name} ({today})"

    def _build_vendor_body(self, vendor_name: str, orders: List[Order]) -> str:
        today = datetime.now().strftime("%B %d, %Y")
        lines = [f"Hello {vendor_name},", "", f"Please find below our orders for {today}:"]
        for order in orders:
            lines.append(f"\nStore: {order.store}")
            for item in order.items:
                lines.append(f"  - {item.quantity} × {item.name}")
        lines += ["", "Thank you!", "Purchasing Department"]
        return "\n".join(lines)

    def _build_store_body(self, store_name: str, orders: List[Order]) -> str:
        today = datetime.now().strftime("%B %d, %Y")
        lines = [f"Hi {store_name},", "", f"Here are your orders for the week of {today}:"]
        for order in orders:
            lines.append(f"\nVendor: {order.vendor}")
            for item in order.items:
                lines.append(f"  - {item.quantity} × {item.name}")
        return "\n".join(lines)

    def _get_vendor_attachments(self, orders: List[Order]) -> List[str]:
        attachments: list[str] = []
        for order in orders:
            try:
                path = self.orders.repo.get_file_path(order, format="pdf")
                if path.exists():
                    attachments.append(str(path))
            except Exception as e:
                self.logger.warning(f"Attachment lookup failed for {order.vendor}/{order.store}: {e}")
        return attachments

    def _get_store_attachments(self, orders: List[Order]) -> List[str]:
        attachments: list[str] = []
        for order in orders:
            try:
                path = self.orders.repo.get_file_path(order, format="pdf")
                if path.exists():
                    attachments.append(str(path))
            except Exception as e:
                self.logger.warning(f"Attachment lookup failed for store {order.store}: {e}")
        return attachments
