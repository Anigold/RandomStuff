from config.paths import TRANSFER_FILES_DIR
from backend.storage.file.file_handler import FileHandler
from backend.models.transfer import Transfer
from backend.serializer.serializers.transfer_serializer import TransferSerializer
from backend.serializer.formats.excel_format import ExcelFormat
from backend.serializer.filename_strategies.transfer_filename_strategy import TransferFilenameStrategy
from backend.utils.logger import Logger
from pathlib import Path
from datetime import datetime

@Logger.attach_logger
class TransferFileHandler(FileHandler):

    TRANSFER_FILES_DIR = Path(TRANSFER_FILES_DIR)

    def __init__(self):
        super().__init__(self.TRANSFER_FILES_DIR)
        self.serializer = TransferSerializer()
        self.format = ExcelFormat()
        self.filename_strategy = TransferFilenameStrategy()

    def save_transfer(self, transfer: Transfer, format: str = 'excel') -> Path:
        headers = self.serializer.get_headers()
        rows = self.serializer.to_rows(transfer)
        data = self.format.write(headers, rows)

        file_path = self.get_transfer_file_path(transfer, format)
        self._write_data(format, data, file_path)
        return file_path

    def read_transfer_file(self, file_path: Path) -> Transfer:
        rows = self.format.read(file_path)
        meta = self.filename_strategy.parse(file_path.name)
        return self.serializer.from_rows(rows, metadata=meta)

    def get_transfer_file_path(self, transfer: Transfer, format: str = 'excel') -> Path:
        suffix = f'{self.extension_map.get(format, 'xlsx')}'
        return self.TRANSFER_FILES_DIR / self.filename_strategy.format(transfer, suffix)

    def get_transfer_files(self, stores: list[str], start_date: str = None, end_date: str = None) -> list[Path]:
        start = datetime.strptime(start_date, '%Y-%m-%d') if start_date else None
        end   = datetime.strptime(end_date, '%Y-%m-%d') if end_date else None

        def matches_filters(meta: dict) -> bool:
            if not meta or 'transfer_date' not in meta:
                return False
            if stores and not (meta.get('origin') in stores or meta.get('destination') in stores):
                return False
            try:
                file_date = datetime.strptime(meta['transfer_date'], '%Y-%m-%d')
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
        archive_dir = self.TRANSFER_FILES_DIR / 'CompletedTransfers'
        archive_dir.mkdir(parents=True, exist_ok=True)

        filename_prefix = self.filename_strategy.prefix(transfer)

        for file in self.TRANSFER_FILES_DIR.iterdir():
            if not file.is_file() or not file.name.startswith(filename_prefix):
                continue

            dest = archive_dir / file.name
            try:
                self.move_file(file, dest, overwrite=True)
                self.logger.info(f'Archived transfer file: {file.name}')
            except Exception as e:
                self.logger.warning(f'Failed to archive {file.name}: {e}')
