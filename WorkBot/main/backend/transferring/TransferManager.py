from .Transfer import Transfer
from pathlib import Path
from datetime import datetime
import re

from backend.helpers.DatetimeFormattingHelper import string_to_datetime

SOURCE_PATH              = Path(__file__).parent.parent
TRANSFER_FILES_DIRECTORY = SOURCE_PATH / 'transferring' / 'TransferFiles'

class TransferManager:

    file_pattern = re.compile(r"^(?P<store_from>.+?) to (?P<store_to>.+?) (?P<date>\d{8})$")

    def __init__(self, transfers: list[Transfer] = None) -> None:
        self.transfers = transfers

    def load_transfer_from_file(self, path: Path) -> Transfer:
        
        if not (path.exists() and path.is_file() and path.suffix in ['.xlsx', '.xls']):
            return None
        
        transfer_metadata = self.parse_filename(path)
        datetime = string_to_datetime(transfer_metadata['date'])

        return Transfer.from_excel_workbook(path, transfer_metadata['store_from'], transfer_metadata['store_to'], datetime)

    def generate_file_name(self, transfer: Transfer = None, store_to: str = None, store_from: str = None, date: datetime = None, file_extension='.xlsx') -> str:
        return f'{transfer.store_from} to {transfer.store_to} {transfer.date}{file_extension}' if transfer else f'{store_from} to {store_to} {date}{file_extension}'

    def get_file_path(self, transfer: Transfer, file_extension: str = '.xlsx') -> Path:
        return self.__class__.get_transfer_files_directory() / self.generate_filename(transfer, file_extension)

    def save_transfer(self, transfer: Transfer, file_extension: str = '.xlsx') -> None:

        extensions = {
            '.xlsx': self._save_as_excel
        }

        return extensions[file_extension](transfer) if file_extension in extensions else None
    
    def _save_as_excel(self, transfer: Transfer) -> None:
        
        workbook = self._to_excel(transfer)
        workbook.save(self.get_file_path(transfer, '.xlsx'))

        return 
    
    @staticmethod
    def format_date_string(date_string: str) -> str:
        return TransferManager._format_datetime_to_string(string_to_datetime(date_string))

    @staticmethod
    def get_transfer_files_directory() -> Path:
        return TRANSFER_FILES_DIRECTORY
    
    @staticmethod
    def _format_datetime_to_string(datetime_obj: datetime) -> str:
        return datetime_obj.strftime('%Y%m%d')
    
    @classmethod
    def parse_filename(cls, filename: Path) -> dict:
        if cls.is_valid_filename(filename): 
            return cls.file_pattern.match(filename.stem).groupdict()
        raise ValueError(f'Filename "{filename}" does not match expected pattern.')
    
    @classmethod
    def is_valid_filename(cls, filename: Path) -> bool:
        return bool(cls.file_pattern.match(filename.stem))
    