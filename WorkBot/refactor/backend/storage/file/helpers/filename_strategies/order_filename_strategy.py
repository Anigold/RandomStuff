import re
from pathlib import Path
from datetime import datetime
from typing import Optional
from backend.models.order import Order

class OrderFilenameStrategy:
    """
    Provides regex-based parsing and formatting of order filenames.
    """

    FILENAME_PATTERN = re.compile(r"^(?P<vendor>.+?)_(?P<store>.+?)_(?P<date>\d{4}-\d{2}-\d{2})$")
    

    def format(self, order: Order, extension: str = 'xlsx') -> str:
        try:
            date_obj = datetime.strptime(order.date, "%Y-%m-%d")
        except ValueError:
            try:
                date_obj = datetime.strptime(order.date, "%Y%m%d")
            except ValueError:
                raise ValueError(f"Unrecognized date format: {order.date}")

        formatted_date = date_obj.strftime("%Y-%m-%d")
        return f"{order.vendor}_{order.store}_{formatted_date}.{extension}"

    def parse(self, filename: str) -> dict[str: str, str: str, str: str]:
        stem = Path(filename).stem  # removes .xlsx, .csv, etc.
        match = self.FILENAME_PATTERN.match(stem)
        if not match:
            raise ValueError(f"Invalid filename format: {filename}")
        
        vendor   = match.group("vendor")
        store    = match.group("store")
        date_str = match.group("date")

        # Optional: validate date
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            raise ValueError(f"Invalid date in filename: {filename}")
        
        return {'vendor': vendor, 'store': store, 'date': date_str}
    
    def prefix(self, order: Order):
        try:
            date_obj = datetime.strptime(order.date, '%Y-%m-%d')
        except ValueError:
            try:
                date_obj = datetime.strptime(order.date, '%Y%m%d')
            except ValueError:
                raise ValueError(f'Unrecognized date format: {order.date}')

        formatted_date = date_obj.strftime('%Y-%m-%d')
        return f'{order.vendor}_{order.store}_{formatted_date}'