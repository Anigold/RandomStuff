from backend.exporters.exporter import Exporter
from backend.models.order import Order
from backend.models.item import Item
from openpyxl import Workbook
from .adapters import ExportAdapter

@Exporter.register_exporter(Order, "excel")
class ExcelOrderExporter(Exporter):
    def export(self, order: Order, adapter: ExportAdapter = None) -> Workbook:
        wb = Workbook()
        ws = wb.active

        # Default headers and row logic
        default_headers = ["SKU", "Name", "Quantity", "Cost Per", "Total Cost"]
        default_row_fn = lambda item: [item.sku, item.name, item.quantity, item.cost_per, item.total_cost]

        # Use adapter if available
        headers = adapter.modify_headers(default_headers) if adapter else default_headers
        ws.append(headers)

        for item in order.items:
            row = adapter.modify_row(default_row_fn(item), item) if adapter else default_row_fn(item)
            ws.append(row)

        return wb

@Exporter.register_exporter(Item, "excel")
class ExcelItemExporter(Exporter):
    def export(self, item: Item) -> Workbook:
        wb = Workbook()
        ws = wb.active
        ws.append(["Name", "Quantity"])
        ws.append([item.name, item.quantity])
        return wb
