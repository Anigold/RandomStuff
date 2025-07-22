import re
from pathlib import Path
from datetime import datetime
from typing import Optional
from backend.models.Order import Order

class OrderFilenameStrategy:
    """
    Provides regex-based parsing and formatting of order filenames.
    """

    FILENAME_PATTERN = re.compile(r"^(?P<vendor>.+?)_(?P<store>.+?)_(?P<date>\d{8})")

    def format(self, order: Order, extension: str = 'xlsx') -> str:
        return f'{order.vendor}_{order.store}_{order.date}.{extension}'

    def parse(self, filename: str) -> tuple[str, str, str]:
        stem = Path(filename).stem  # removes .xlsx, .csv, etc.
        match = self.FILENAME_REGEX.match(stem)
        if not match:
            raise ValueError(f"Invalid filename format: {filename}")
        
        vendor = match.group("vendor")
        store = match.group("store")
        date_str = match.group("date")

        # Optional: validate date
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            raise ValueError(f"Invalid date in filename: {filename}")
        
        return vendor, store, date_str
