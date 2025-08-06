from config.paths import TRANSFER_FILES_DIR
from backend.storage.file.file_handler import FileHandler
from backend.models.transfer import Transfer
from backend.parsers.transfer_parser import TransferParser
from backend.utils.logger import Logger
from backend.storage.file.helpers.filename_strategies.transfer_filename_strategy import TransferFilenameStrategy
from backend.exporters.excel_exporter import Exporter

from openpyxl import Workbook
from pathlib import Path
from typing import Any
from datetime import datetime
import re

@Logger.attach_logger
class TransferFileHandler(FileHandler):

    TRANSFER_FILES_DIR = Path(TRANSFER_FILES_DIR)

    def __init__(self):
        super().__init__(self.TRANSFER_FILES_DIR)
        self.parser = TransferParser()
        self.filename_strategy = TransferFilenameStrategy()

    def _generate_file_name(self, transfer: Transfer, format: str) -> str:
        ext = self.extension_map.get(format, 'xlsx')
        return self.filename_strategy.format(transfer, extension=ext)

    def save_transfer(self, transfer: Transfer, format: str = 'excel') -> None:
        exporter          = Exporter.get_exporter(Transfer, format)
        file_data_to_save = exporter.export(transfer)
        file_path         = self.TRANSFER_FILES_DIR / self._generate_file_name(transfer, format)
        self._write_data(format, file_data_to_save, file_path)

    def read_transfer_file(self, file_path: Path) -> Transfer:
        return self.parser.parse_excel(file_path)

    def get_transfer_file_path(self, transfer: Transfer, format: str = 'excel') -> Path:
        return self.TRANSFER_FILES_DIR / self._generate_file_name(transfer, format)

    def get_transfer_files(self, stores: list[str], start_date: str = None, end_date: str = None) -> list[Path]:
        """
        Returns all transfer files whose parsed metadata falls within the given store and date range filters.
        """
        start = datetime.strptime(start_date, "%Y-%m-%d") if start_date else None
        end   = datetime.strptime(end_date, "%Y-%m-%d") if end_date else None

        def matches_filters(meta: dict) -> bool:
            if not meta or "date" not in meta:
                return False
            if stores and not (meta.get("store_from") in stores or meta.get("store_to") in stores):
                return False
            try:
                file_date = datetime.strptime(meta["date"], "%Y-%m-%d")
            except ValueError:
                return False
            if start and file_date < start:
                return False
            if end and file_date > end:
                return False
            return True

        matched_files = []

        for file in self.TRANSFER_FILES_DIR.iterdir():
            if not file.is_file() or file.suffix != '.xlsx':
                continue

            meta = self.filename_strategy.parse(file.name)
            if matches_filters(meta):
                matched_files.append(file)

        return matched_files

    def archive_transfer_file(self, transfer: Transfer) -> None:
        """
        Moves all files related to the given transfer into the CompletedTransfers archive folder.
        Matches based on filename prefix (store_from_store_to_date). Overwrites if exists.
        """
        archive_dir = self.TRANSFER_FILES_DIR / "CompletedTransfers"
        archive_dir.mkdir(parents=True, exist_ok=True)

        filename_prefix = self.filename_strategy.prefix(transfer)

        for file in self.TRANSFER_FILES_DIR.iterdir():
            if not file.is_file() or not file.name.startswith(filename_prefix):
                continue

            dest = archive_dir / file.name
            try:
                if dest.exists():
                    dest.unlink()
                file.rename(dest)
                self.logger.info(f"Archived transfer file: {file.name}")
            except Exception as e:
                self.logger.warning(f"Failed to archive {file.name}: {e}")
