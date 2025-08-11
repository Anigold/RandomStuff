from backend.utils.logger import Logger
from backend.models.transfer import Transfer
from backend.storage.file.transfer_file_handler import TransferFileHandler
# from backend.parsers.transfer_parser import TransferParser
# from backend.database_handlers.transfer_db_handler import TransferDatabaseHandler  # Optional
from backend.storage.file.download_handler import DownloadHandler

@Logger.attach_logger
class TransferCoordinator:
    '''
    Handles high-level operations for Transfer domain objects.
    '''
    
    def __init__(self, file_handler=None, db_handler=None, parser=None):
        self.file_handler = file_handler or TransferFileHandler()
        # self.db_handler   = db_handler or TransferDatabaseHandler()
        # self.parser       = parser or TransferParser()
        self.download_handler = DownloadHandler()

    def save_transfer(self, transfer: Transfer) -> None:
        '''
        Saves the transfer to both file and database storage layers.
        '''
        # Save to file
        self.file_handler.save_transfer(transfer)

        # Optional: save to database
        # self.db_handler.upsert_transfer(transfer)

    def load_transfer(self, path: str) -> Transfer:
        '''
        Load a transfer from a file path.
        '''
        raw_data = self.file_handler.read_transfer_file(path)
        return self.parser.parse_transfer(raw_data)

    def get_transfers_from_file(
        self,
        stores: list[str] = None,
        start_date: str = None,
        end_date: str = None
    ) -> list[Transfer]:
        '''
        Retrieves and parses all saved transfer files matching the given filters.

        Args:
            stores (list[str], optional): List of store names to filter by.
            start_date (str, optional): Filter transfers from this date forward (YYYY-MM-DD).
            end_date (str, optional): Filter transfers up to this date (YYYY-MM-DD).

        Returns:
            list[Transfer]: List of parsed Transfer domain objects.
        '''
        file_paths = self.file_handler.get_transfer_files(
            stores=stores,
            start_date=start_date,
            end_date=end_date
        )
        
        transfers = []
        for path in file_paths:
            try:
                transfer = self.file_handler.read_transfer_file(path)
                transfers.append(transfer)
            except Exception as e:
                self.logger.warning(f'Failed to read transfer from {path.name}: {e}')

        return transfers

