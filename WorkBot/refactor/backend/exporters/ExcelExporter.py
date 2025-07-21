from exporters import Exporter, register_exporter
from models import Order, Item
from openpyxl import Workbook

@register_exporter(Order, "excel")
class ExcelOrderExporter(Exporter):
    def export(self, order: Order) -> Workbook:
        wb = Workbook()
        ws = wb.active

        headers = ["SKU", "Name", "Quantity", "Cost Per", "Total Cost"]
        ws.append(headers)

        for item in order.items:
            ws.append([item.sku, item.name, item.quantity, item.cost_per, item.total_cost])

        return wb

@register_exporter(Item, "excel")
class ExcelItemExporter(Exporter):
    def export(self, item: Item) -> Workbook:
        wb = Workbook()
        ws = wb.active
        ws.append(["Name", "Quantity"])
        ws.append([item.name, item.quantity])
        return wb
