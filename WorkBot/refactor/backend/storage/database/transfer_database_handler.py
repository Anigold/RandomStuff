from .database_handler import DatabaseHandler

class TransferStorage(DatabaseHandler):
    
    def get_transfers_for_store(self, store_id: int):
        return self.fetch_all('SELECT * FROM Transfers WHERE store_id = ?', (store_id,))
