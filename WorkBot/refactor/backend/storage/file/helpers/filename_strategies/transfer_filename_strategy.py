import re
from pathlib import Path
from datetime import datetime
from backend.models.transfer import Transfer

class TransferFilenameStrategy:
    """
    Provides regex-based parsing and formatting of transfer filenames.
    """

    FILENAME_PATTERN = re.compile(r"^(?P<store_from>.+?)_(?P<store_to>.+?)_(?P<date>\d{4}-\d{2}-\d{2})$")

    def format(self, transfer: Transfer, extension: str = 'xlsx') -> str:
        try:
            date_obj = datetime.strptime(transfer.date, "%Y-%m-%d")
        except ValueError:
            try:
                date_obj = datetime.strptime(transfer.date, "%Y%m%d")
            except ValueError:
                raise ValueError(f"Unrecognized date format: {transfer.date}")

        formatted_date = date_obj.strftime("%Y-%m-%d")
        return f"{transfer.store_from}_{transfer.store_to}_{formatted_date}.{extension}"

    def parse(self, filename: str) -> dict:
        stem = Path(filename).stem
        match = self.FILENAME_PATTERN.match(stem)
        if not match:
            raise ValueError(f"Invalid filename format: {filename}")

        store_from = match.group("store_from")
        store_to   = match.group("store_to")
        date_str   = match.group("date")

        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            raise ValueError(f"Invalid date in filename: {filename}")

        return {
            'store_from': store_from,
            'store_to': store_to,
            'date': date_str
        }

    def prefix(self, transfer: Transfer) -> str:
        try:
            date_obj = datetime.strptime(transfer.date, '%Y-%m-%d')
        except ValueError:
            try:
                date_obj = datetime.strptime(transfer.date, '%Y%m%d')
            except ValueError:
                raise ValueError(f'Unrecognized date format: {transfer.date}')

        formatted_date = date_obj.strftime('%Y-%m-%d')
        return f'{transfer.store_from}_{transfer.store_to}_{formatted_date}'
