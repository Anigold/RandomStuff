from openpyxl import Workbook
from models.Order import Order

class OrderExporter:

    def export_to_excel(self, order: Order) -> Workbook:
        wb = Workbook()
        ws = wb.active

        headers = ["SKU", "Name", "Quantity", "Cost Per", "Total Cost"]
        ws.append(headers)

        for item in order.items:
            ws.append([item.sku, item.name, item.quantity, item.cost_per, item.total_cost])

        return wb
