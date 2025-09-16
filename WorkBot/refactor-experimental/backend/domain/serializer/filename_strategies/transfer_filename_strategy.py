import re
from pathlib import Path
from datetime import datetime
from backend.domain.models.transfer import Transfer

class TransferFilenameStrategy:
    '''
    Provides regex-based parsing and formatting of transfer filenames.
    '''

    FILENAME_PATTERN = re.compile(r'^(?P<origin>.+?)_(?P<destination>.+?)_(?P<date>\d{4}-\d{2}-\d{2})$')

    def format(self, transfer: Transfer, extension: str = 'xlsx') -> str:
        try:
            date_obj = datetime.strptime(transfer.transfer_date, '%Y-%m-%d')
        except ValueError:
            try:
                date_obj = datetime.strptime(transfer.transfer_date, '%Y%m%d')
            except ValueError:
                raise ValueError(f'Unrecognized date format: {transfer.transfer_date}')

        formatted_date = date_obj.strftime('%Y-%m-%d')
        return f'{transfer.origin}_{transfer.destination}_{formatted_date}.{extension}'

    def parse(self, filename: str) -> dict:
        stem = Path(filename).stem
        match = self.FILENAME_PATTERN.match(stem)
        if not match:
            raise ValueError(f'Invalid filename format: {filename}')

        origin        = match.group('origin')
        destination   = match.group('destination')
        transfer_date = match.group('date')

        try:
            datetime.strptime(transfer_date, '%Y-%m-%d')
        except ValueError:
            raise ValueError(f'Invalid date in filename: {filename}')

        return {
            'origin': origin,
            'destination': destination,
            'transfer_date': transfer_date
        }

    def prefix(self, transfer: Transfer) -> str:
        try:
            date_obj = datetime.strptime(transfer.transfer_date, '%Y-%m-%d')
        except ValueError:
            try:
                date_obj = datetime.strptime(transfer.transfer_date, '%Y%m%d')
            except ValueError:
                raise ValueError(f'Unrecognized date format: {transfer.transfer_date}')

        formatted_date = date_obj.strftime('%Y-%m-%d')
        return f'{transfer.origin}_{transfer.destination}_{formatted_date}'
