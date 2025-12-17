from ..command import Command
import argparse
from tabulate import tabulate
from backend.domain.models.vendors.vendor import Vendor

class VendorInformation(Command):

    name = 'vendor_information'

    def arguments(self):
        parser = argparse.ArgumentParser(prog=self.name, description='Display the saved information for the specified vendor, if any.')
        parser.add_argument('--vendor', required=True, help='A single vendor name.')
        return parser

    def autocomplete(self, flag: str, text: str):
        
        flags = {
            '--vendor': self.context.get_vendors
        }
        
        return [option for option in flags.get(flag, [])() if option.startswith(text)]

    def command(self, args):
        try:
            parser = self.arguments()
            parsed_args = parser.parse_args(args)
            vendor_info = self.context.workbot.get_vendor_information(parsed_args.vendor)
            print(f'{self.format_vendor_information(vendor_info)}\n')
        except SystemExit:
            pass


#     def _format_vendor_info(self, data: dict) -> str:
#         # Prepare the top-level vendor info
#         summary_table = [
#             ['Minimum Order Value', f'${data.min_order_value:,.2f}'],
#             ['Minimum Order Cases', data.min_order_cases],
#             ['Special Notes', data.special_notes or 'None']
#         ]

#         # Prepare internal contacts, if any
#         contacts = data.internal_contacts
#         if contacts:
#             contact_table = [
#                 [c.name, c.title, c.email, self._format_phone_number(c.phone)] for c in contacts
#             ]
#             contact_headers = ['Name', 'Title', 'Email', 'Phone']
#             contact_output = tabulate(contact_table, headers=contact_headers, tablefmt='fancy_grid')
#         else:
#             contact_output = '[No internal contacts listed.]'

#         return f'''
# ===================

# {tabulate(summary_table, tablefmt='plain')}

# Internal Contacts:
# {contact_output}
# '''.strip()
    
    def format_vendor_information(self, data: Vendor) -> str:
        """
        Format the full vendor information dict into a readable string.
        """

        # ------------------------------
        # Summary Section
        # ------------------------------
        summary_table = [
            ['Vendor Name', data.name or ''],
            ['Order Format', data.order_format or ''],
            ['Special Notes', data.special_notes or 'None'],
            ['Minimum Order Value', f"${data.min_order_value:,.2f}"] or '$0.00',
            ['Minimum Order Cases', data.min_order_cases] or 0
        ]
        summary_output = tabulate(summary_table, tablefmt='plain')

        # ------------------------------
        # Internal Contacts
        # ------------------------------
        contacts = data.internal_contacts or []
        if contacts:
            contact_table = [
                [
                    c.name or '',
                    c.title or '',
                    c.email or '',
                    self._format_phone_number(c.phone) or ''
                ]
                for c in contacts
            ]
            contact_output = tabulate(
                contact_table,
                headers=["Name", "Title", "Email", "Phone"],
                tablefmt="fancy_grid"
            )
        else:
            contact_output = "[No internal contacts listed.]"

        # ------------------------------
        # Ordering Information
        # ------------------------------
        ordering = data.ordering or []
        ordering_table = [
            ["Ordering Methods", ", ".join(ordering.method) or "None"],
            ["Order Email", ordering.email or ""],
            ["Portal URL", ordering.portal_url or ""],
            ["Ordering Phone", self._format_phone_number(ordering.phone_number) or ""]
        ]
        ordering_output = tabulate(ordering_table, tablefmt='plain')

        # ------------------------------
        # Ordering Schedule
        # ------------------------------
        schedule = ordering.schedule or []
        if schedule:
            schedule_table = [
                [
                    entry.order_day,
                    ", ".join(entry.delivery_days or []),
                    entry.cutoff_time or 'None'
                ]
                for entry in schedule
            ]
            schedule_output = tabulate(
                schedule_table,
                headers=["Order Day", "Delivery Days", "Cutoff Time"],
                tablefmt="fancy_grid"
            )
        else:
            schedule_output = "[No ordering schedule listed.]"

        # ------------------------------
        # Store IDs
        # ------------------------------
        store_ids = data.store_ids or {}
        store_table = [[name, value] for name, value in store_ids.items()]
        store_output = tabulate(store_table, headers=["Store", "Vendor Store ID"], tablefmt="fancy_grid")

        # ------------------------------
        # Final Output
        # ------------------------------
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

        if not phone_number.isdigit(): 
            return phone_number

        area_code   = phone_number[0:3]
        lead_digits = phone_number[3:6]
        last_four   = phone_number[6:]
        return f'({area_code}) {lead_digits}-{last_four}'