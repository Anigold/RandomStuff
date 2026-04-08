from ..command import Command
import argparse
from tabulate import tabulate

from backend.app.cli.commands.command_result import CommandResult
from backend.domain.models.vendors.vendor import Vendor


class VendorInformation(Command):
    name = "vendor_information"

    def arguments(self):
        parser = argparse.ArgumentParser(
            prog=self.name,
            description="Display the saved information for the specified vendor, if any.",
        )
        parser.add_argument(
            "--vendor",
            required=True,
            help="A single vendor name.",
        )
        return parser

    def autocomplete(self, flag: str, text: str):
        flags = {
            "--vendor": self.context.get_vendors,
        }

        return [
            option
            for option in flags.get(flag, [])()
            if option.startswith(text)
        ]

    def command(self, args):
        try:
            parser = self.arguments()
            parsed_args = parser.parse_args(args)

            vendor_info = self.context.workbot.get_vendor_information(parsed_args.vendor)

            if not vendor_info:
                return CommandResult.error(
                    f"No saved information found for vendor '{parsed_args.vendor}'."
                )

            return CommandResult.text(
                self.format_vendor_information(vendor_info),
                target="side",
                title=f"Vendor: {vendor_info.name or parsed_args.vendor}",
                summary=f"Loaded vendor information for {vendor_info.name or parsed_args.vendor}.",
            )

        except SystemExit:
            return CommandResult.error("Invalid arguments provided.")

    def format_vendor_information(self, data: Vendor) -> str:
        """
        Format the full vendor information into a readable string.
        """
        summary_table = [
            ["Vendor Name", data.name or ""],
            ["Order Format", data.order_format or ""],
            ["Special Notes", data.special_notes or "None"],
            ["Minimum Order Value", f"${data.min_order_value:,.2f}" if data.min_order_value is not None else "$0.00"],
            ["Minimum Order Cases", data.min_order_cases if data.min_order_cases is not None else 0],
        ]
        summary_output = tabulate(summary_table, tablefmt="plain")

        contacts = data.internal_contacts or []
        if contacts:
            contact_table = [
                [
                    c.name or "",
                    c.title or "",
                    c.email or "",
                    self._format_phone_number(c.phone) if c.phone else "",
                ]
                for c in contacts
            ]
            contact_output = tabulate(
                contact_table,
                headers=["Name", "Title", "Email", "Phone"],
                tablefmt="fancy_grid",
            )
        else:
            contact_output = "[No internal contacts listed.]"

        ordering = data.ordering
        if ordering:
            ordering_table = [
                ["Ordering Methods", ", ".join(ordering.method or []) or "None"],
                ["Order Email", ordering.email or ""],
                ["Portal URL", ordering.portal_url or ""],
                ["Ordering Phone", self._format_phone_number(ordering.phone_number) if ordering.phone_number else ""],
            ]
            ordering_output = tabulate(ordering_table, tablefmt="plain")

            schedule = ordering.schedule or []
            if schedule:
                schedule_table = [
                    [
                        entry.order_day or "",
                        ", ".join(entry.delivery_days or []),
                        entry.cutoff_time or "None",
                    ]
                    for entry in schedule
                ]
                schedule_output = tabulate(
                    schedule_table,
                    headers=["Order Day", "Delivery Days", "Cutoff Time"],
                    tablefmt="fancy_grid",
                )
            else:
                schedule_output = "[No ordering schedule listed.]"
        else:
            ordering_output = "[No ordering information listed.]"
            schedule_output = "[No ordering schedule listed.]"

        store_ids = data.store_ids or {}
        if store_ids:
            store_table = [[name, value] for name, value in store_ids.items()]
            store_output = tabulate(
                store_table,
                headers=["Store", "Vendor Store ID"],
                tablefmt="fancy_grid",
            )
        else:
            store_output = "[No store IDs listed.]"

        return f"""
=============================
 V E N D O R   D E T A I L S
=============================

{summary_output}

Internal Contacts:
{contact_output}

Ordering Information:
{ordering_output}

Ordering Schedule:
{schedule_output}

Store IDs:
{store_output}
""".strip()

    def _format_phone_number(self, phone_number: str) -> str:
        if not phone_number:
            return ""

        if not phone_number.isdigit():
            return phone_number

        area_code = phone_number[0:3]
        lead_digits = phone_number[3:6]
        last_four = phone_number[6:]
        return f"({area_code}) {lead_digits}-{last_four}"