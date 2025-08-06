from backend.utils.logger import Logger
from backend.models.transfer import Transfer
from backend.storage.file.transfer_file_handler import TransferFileHandler
from backend.parsers.transfer_parser import TransferParser
# from backend.database_handlers.transfer_db_handler import TransferDatabaseHandler  # Optional
from backend.storage.file.download_handler import DownloadHandler

@Logger.attach_logger
class TransferCoordinator:
    """
    Handles high-level operations for Transfer domain objects.
    """
    
    def __init__(self, file_handler=None, db_handler=None, parser=None):
        self.file_handler = file_handler or TransferFileHandler()
        # self.db_handler   = db_handler or TransferDatabaseHandler()
        self.parser       = parser or TransferParser()
        self.download_handler = DownloadHandler()

    def save_transfer(self, transfer: Transfer) -> None:
        """
        Saves the transfer to both file and database storage layers.
        """
        # Save to file
        self.file_handler.save_transfer(transfer)

        # Optional: save to database
        # self.db_handler.upsert_transfer(transfer)

    def load_transfer(self, path: str) -> Transfer:
        """
        Load a transfer from a file path.
        """
        raw_data = self.file_handler.read_transfer_file(path)
        return self.parser.parse_transfer(raw_data)

    def get_transfers_from_file(self, stores: list[str], start_date=None, end_date=None) -> list[Transfer]:
        """
        Get a list of Transfer domain objects based on file search criteria.
        """
        transfer_files = self.file_handler.list_transfer_files(stores, start_date, end_date)
        transfers = []

        for path in transfer_files:
            raw_data = self.file_handler.read_transfer_file(path)
            transfer = self.parser.parse_transfer(raw_data)
            transfers.append(transfer)

        return transfers
