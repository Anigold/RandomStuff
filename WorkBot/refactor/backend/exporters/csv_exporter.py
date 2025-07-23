from backend.exporters.exporter import Exporter
from backend.models.order import Order
from backend.models.item import Item
from openpyxl import Workbook

@Exporter.register_exporter(Order, 'csv')
class CSVOrderExporter(Exporter):

    def export(self) -> None:
        pass