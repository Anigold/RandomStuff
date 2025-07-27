from csv import writer
from io import StringIO
from backend.exporters.exporter import Exporter
from backend.models.order import Order
from backend.models.item import Item
from backend.exporters.adapters.exporter_adapter import ExportAdapter

@Exporter.register_exporter(Order, "csv")
class CSVOrderExporter(Exporter):

    preferred_delimiter: str = ','

    def export(self, order: Order, adapter: ExportAdapter = None, context: dict = None) -> str:
        buffer = StringIO()
        csv_writer = writer(buffer)

        # Adapter can override the exporter's default delimiter
        delimiter = getattr(adapter, "preferred_delimiter", self.preferred_delimiter)
        csv_writer = writer(buffer, delimiter=delimiter, lineterminator='\n')

        # Default header and row structure
        default_headers = ["SKU", "Name", "Quantity", "Cost Per", "Total Cost"]
        default_row_fn = lambda item: [item.sku, item.name, item.quantity, item.cost_per, item.total_cost]

        # Determine headers and rows
        headers = adapter.modify_headers(default_headers, context=context) if adapter else default_headers
        if headers:
            csv_writer.writerow(headers)

        for item in order.items:
            row = adapter.modify_row(default_row_fn(item), item, context=context) if adapter else default_row_fn(item)
            csv_writer.writerow(row)

        return buffer.getvalue()
