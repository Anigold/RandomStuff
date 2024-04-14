from ..vendor_bots.VendorBot import PricingBotMixin
from openpyxl import load_workbook, Workbook
import shutil

class PriceSheetTemplate:
    
    def __init__(self) -> None:
        self.skus = []


class PriceComparator:

    def __init__(self) -> None:
        self.item_skus_file_path = './ItemSkus.xlsx'
    
    # def get_skus_from_template(self, vendor: PricingBotMixin) -> dict:
    #     vendor_name = vendor.name
    #     workbook = load_workbook(self.item_skus_file_path)
    #     sheet = workbook.active

    #     # Find column
    #     top_row = list(sheet.rows)[0]

    #     vendor_column = None
    #     for pos, val in enumerate(top_row):
    #         if val.value == vendor_name:
    #             vendor_column = pos + 1

    #     if not vendor_column: return None

    #     # Find skus
    #     item_info = {}
    #     for pos, row in enumerate(sheet.iter_rows(min_row=2)):
    #         item_name = sheet.cell(row=pos+1, column=1).value
    #         item_sku  = sheet.cell(row=pos+1, column=vendor_column).value
    #         if item_sku and item_name:
    #             if item_name not in item_info:
    #                 item_info[item_name] = item_sku
        
    #     return item_info
    
    def get_all_skus(self) -> dict:

        workbook = load_workbook(self.item_skus_file_path)
        sheet = workbook.active

        sku_info = {}
        vendors  = []
        top_row = list(sheet.rows)[0]
        for pos, val in enumerate(top_row):
            if not val.value: continue
            vendors.append(val.value)
            sku_info[val.value] = {}

        if not sku_info: return None

        
        for item_pos, row in enumerate(sheet.iter_rows(min_row=2)):
            item_name = sheet.cell(row=item_pos+1, column=1).value
         
            for vendor_col, vendor in enumerate(vendors):
                item_sku = sheet.cell(row=item_pos+1, column=vendor_col+2).value
                if item_sku and item_name:
                    if item_name not in sku_info[vendor]:
                        sku_info[vendor][item_name] = item_sku

        return sku_info
 
    
    def generate_pricing_sheet(self, pricing_sheet_template_path: str, vendor_sheets_paths: list[str], output_file_path: str) -> None:

        # Make copy of template
        #shutil.copyfile(pricing_sheet_template_path, output_file_path)

        # Get skus from copy of template
        template_copy_workbook = load_workbook(pricing_sheet_template_path)
        sheet = template_copy_workbook.active

        first_row = list(sheet.rows)[0]
        ignore_list = ['Item', 'Buy From']
        skus = {}
        for column in first_row:
            if column.value not in ignore_list:
                skus[column.value] = []

        offset = 3
        for row in sheet.iter_rows(min_row=3):
            pass
        #template_copy_workbook.save(self.path_to_skus)
        
        # Iterate through vender sheets pulling data for each sku found in copy of template
        #   Add info to the copy of template

        # Save copy of template
        pass

    def compare_prices(self, pricing_sheets_paths: list[str], output_file_path: str) -> None:
        for sheet_path in pricing_sheets_paths:

            pass