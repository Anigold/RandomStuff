from __future__ import annotations
from dataclasses import dataclass
from typing import List
from datetime import datetime
from collections import defaultdict
from backend.domain.models import Order, Vendor
from backend.adapters.emailer.emailer import Emailer, Email
from backend.infra.logger import Logger
from backend.app.services.file_locator import FileLocator
from backend.app.services import OrderServices, VendorServices


@Logger.attach_logger
@dataclass
class EmailServices:
    """
    Application-level service for generating and sending emails related to Orders and Vendors.

    Responsibilities:
      - Compose vendor-facing and store-facing emails.
      - Retrieve order and vendor data from domain services.
      - Resolve attachment paths via FileLocator.
      - Delegate actual sending/displaying to the Emailer adapter.

    Dependencies:
      - emailer:  Emailer (Gmail/Outlook/etc.)
      - orders:   OrderServices
      - vendors:  VendorServices
      - locator:  FileLocator (for resolving file paths)
    """

    emailer: Emailer
    orders: OrderServices
    vendors: VendorServices
    locator: FileLocator

    # ---------------------------------------------------------------------
    # --- Vendor-Facing Emails -------------------------------------------
    # ---------------------------------------------------------------------
    def send_vendor_order_emails(
        self, stores: List[str], vendors: List[str]
    ) -> List[Email]:
        """
        Build and display emails to vendors containing store orders and attached order PDFs.

        Args:
            stores:  List of store names whose orders are included.
            vendors: List of vendor names to email.

        Returns:
            A list of Email objects created (for logging/testing).
        """
        self.logger.info("Preparing vendor order emails...")

        orders = self.orders.get_orders(stores, vendors)
        if not orders:
            self.logger.info("No orders found for vendor email dispatch.")
            return []

        grouped = self._group_by_vendor(orders)
        emails: list[Email] = []

        for vendor_name, vendor_orders in grouped.items():
            try:
                vendor_info = self.vendors.get_vendor(vendor_name)
            except Exception as e:
                self.logger.warning(f"Could not fetch vendor info for {vendor_name}: {e}")
                continue

            recipients = [vendor_info.ordering.email] if vendor_info.ordering.email else []
            if not recipients:
                self.logger.info(f"No ordering email found for vendor {vendor_name}, using default.")
                recipients = ['default@somewhere.com']

            subject     = self._build_vendor_subject(vendor_name)
            body        = self._build_vendor_body(vendor_name, vendor_orders)
            attachments = self._get_order_attachments(vendor_orders)

            email = Email(
                to=tuple(recipients),
                subject=subject,
                body=body,
                attachments=tuple(attachments),
            )

            self.emailer.create_email(email)
            self.emailer.display_email(email)
            emails.append(email)

        self.logger.info(f"Prepared {len(emails)} vendor email(s).")
        return emails

    # ---------------------------------------------------------------------
    # --- Store-Facing Emails --------------------------------------------
    # ---------------------------------------------------------------------
    def send_store_order_emails(self, stores: List[str]) -> List[Email]:
        """
        Build and display summary emails for stores containing their order PDFs.
        """
        self.logger.info("Preparing store order emails...")

        all_orders: list[Order] = []
        for store in stores:
            try:
                all_orders.extend(self.orders.get_orders_by_store(store=store))
            except Exception as e:
                self.logger.warning(f"Could not retrieve orders for {store}: {e}")

        if not all_orders:
            self.logger.info("No store orders found to email.")
            return []
  
        grouped = self._group_by_store(all_orders)
        emails: list[Email] = []

        for store_name, store_orders in grouped.items():
            subject     = f"Orders for the Week: {store_name}"
            body        = self._build_store_body(store_name, store_orders)
            attachments = self._get_order_attachments(store_orders)

            email = Email(
                to=("store@example.com",),  # TODO: Pull from store info
                subject=subject,
                body=body,
                attachments=tuple(attachments),
            )

            self.emailer.create_email(email)
            self.emailer.display_email(email)
            emails.append(email)

        self.logger.info(f"Prepared {len(emails)} store email(s).")
        return emails

    # ---------------------------------------------------------------------
    # --- Helper Methods --------------------------------------------------
    # ---------------------------------------------------------------------
    def _get_order_attachments(self, orders: List[Order]) -> List[str]:
        """
        Return file paths to attach for a given list of orders.
        """
        attachments: list[str] = []
        for order in orders:
            try:
                path = self.locator.order_path(order, format="pdf")
                if path.exists():
                    attachments.append(str(path))
            except Exception as e:
                self.logger.warning(f"Attachment resolution failed for {order.vendor}/{order.store}: {e}")
        return attachments

    def _group_by_vendor(self, orders: List[Order]) -> dict[str, list[Order]]:
        grouped = defaultdict(list)
        for o in orders:
            grouped[o.vendor].append(o)
        return grouped

    def _group_by_store(self, orders: List[Order]) -> dict[str, list[Order]]:
        grouped = defaultdict(list)
        for o in orders:
            grouped[o.store].append(o)
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
            lines.append(f"\n{order.vendor}")
            for item in order.items:
                lines.append(f"  - {item.quantity} × {item.name}")
        lines += ["", "Thank you!", "Purchasing Department"]
        return "\n".join(lines)
