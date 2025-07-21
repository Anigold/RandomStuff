from exporters import Exporter, register_exporter
from models import Order, Item
from openpyxl import Workbook

@register_exporter(Order, 'csv')
class CSVOrderExporter(Exporter):

    pass