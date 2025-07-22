from backend.models.Order import Order
from backend.models.OrderItem import OrderItem
from pathlib import Path

class ExcelOrderParser:

    def extract_metadata_from_filename(file_name: str):
        return 
    def parse(self, sheet_data: list[list], path: Path) -> Order:
        # Use file path or sheet header to extract vendor/store/date
        store, vendor, date = extract_metadata_from_filename(path.name)
        items = [
            OrderItem(sku=row[0], name=row[1], quantity=row[2], cost_per=row[3], total_cost=row[4])
            for row in sheet_data
        ]
        return Order(store=store, vendor=vendor, date=date, items=items)
