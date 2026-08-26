from ..command import Command
import argparse
from pathlib import Path

from .new_testing import update_items_from_purchase_log

from backend.domain.models.items.vendor_item_info import VendorItemInfo
from backend.domain.models.items.item import Item

class Testing(Command):

    name = 'testing'

    def arguments(self):
        parser = argparse.ArgumentParser(prog=self.name, description="Testing the ArchiveTransfers")

        parser.add_argument(
            "--item",
            required=True,
            help="The vendor to which the order belongs.",
        )
        
        return parser

    def autocomplete(self, flag: str, text: str):
        
        flags = {
            '--item': self.context.get_items
        }
        
        return [option for option in flags.get(flag, [])() if option.startswith(text)]

    def command(self, args):
        '''Handles downloading orders.'''
        # parser = self.arguments()
        # parsed_args = parser.parse_args(args)
        try:
           self.context.workbot.logger.info('here')
           update_items_from_purchase_log(
               workbot=self.context.workbot,
               purchase_log_path=Path('C:/Users/andrew/Desktop/Andrew/Projects/IthacaBakery/RandomStuff/WorkBot/main/data/downloads/Director - Foodager - Purchase Log 2024-01-01 2026-04-28.xlsx')
           )
           self.context.workbot.logger.info('then here')
        except SystemExit:
            pass  # Prevent argparse from exiting CLI loop

        print('\nTesting complete.\n') # You nasty little side effect you...



    # def update_vendor_item_info(self, item: Item, vendor_item_info: VendorItemInfo) -> Item:
    #     item.vendor_info[vendor_item_info.vendor_id] = vendor_item_info
    #     return item





    # def main_command(self):

    #     purchase_log = None

    #     for row in purchase_log:

    #         item_name = ' '.join(row[3].split(' ')[:-1])
    #         item_obj = self.context.workbot.get_item_by_name(item_name)
    #         if not item_obj: continue

    #         vendor_name = row[7]

    #         current_vendor_info = item_obj.vendor_info
            
    #         '''
    #         Cases:
            
    #         The current vendor is not found in the VendorItemInfo -> Add everything
    #         The current vendor is found in the VendorItemInfo
    #             The current SKU is not in the VendorItemInfo -> Add new VendorItemInfo
    #             The current SKU is in the VendorItemInfo
    #                 The current date is newer than the last_ordered date -> Update last_price and last_ordered
    #                 The current date is older than the last_ordered date -> Ignore
    #                 The current date matches the last_ordered date -> Ignore
                
            
            
    #         '''
    #         if not (vendor_name in current_vendor_info):
                
            
    #             vendor_id = self.context.workbot.get_vendor_by_name(vendor_name)

    #             item_id = item_obj.id

    #             item_sku = row[2]
    #             order_unit = row[3].split(' ')[-1]
    #             unit_size = row[4]

    #             price = row[13]
    #             date = row[9]


    #             vendor_info = VendorItemInfo(
    #                 vendor_id=vendor_id,
    #                 sku=item_sku,
    #                 order_unit=order_unit,
    #                 vendor_name=vendor_name,
    #                 unit_size=unit_size,
    #                 last_price=price,
    #                 last_ordered=date
    #             )

    #             self.context.workbot.items.update(item_id, self.update_vendor_item_info, vendor_item_info=vendor_info)
            
    #             continue

    #         saved_vendor_info = current_vendor_info[vendor_name]


