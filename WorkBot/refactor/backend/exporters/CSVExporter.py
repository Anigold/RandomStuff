from backend.exporters.Exporter import Exporter
from backend.models.Order import Order
from backend.models.Item import Item
from openpyxl import Workbook

@Exporter.register_exporter(Order, 'csv')
class CSVOrderExporter(Exporter):

    def export(self) -> None:
        pass