import re
from pathlib import Path
from .Order import Order

SOURCE_PATH         = Path(__file__).parent.parent
ORDERS_DIRECTORY    = SOURCE_PATH / 'orders' / 'OrderFiles'
DOWNLOADS_DIRECTORY = SOURCE_PATH / 'downloads'

class OrderManager:

    file_pattern = re.compile(r"^(?P<vendor>.+?) _ (?P<store>.+?) (?P<date>\d{8})$")

    def get_order_files_directory(self) -> Path:
        return ORDERS_DIRECTORY
    
    def get_downloads_directory(self) -> Path:
        return DOWNLOADS_DIRECTORY
    
    def get_vendor_orders_directory(self, vendor: str) -> Path:
        print('Checking for vendor order directory...', flush=True)
        vendor_orders_directory = self.get_order_files_directory() / vendor
        if vendor_orders_directory.exists() and vendor_orders_directory.is_dir():
            print(f'...order directory found for {vendor}.')
            return vendor_orders_directory
        print(f'...no order directory found for {vendor}.')
        return None

    def generate_filename(self, order: Order = None, store: str = None, vendor: str = None, date: str = None, file_extension: str = '.xlsx') -> str:
        return f'{order.vendor} _ {order.store} {order.date}{file_extension}' if order else f'{vendor} _ {store} {date}{file_extension}'

    def get_file_path(self, order: Order, file_extension: str = '.xlsx') -> Path:
        return self.orders_directory / self.generate_filename(order, file_extension)

    def save_order(self, order: Order, file_extension: str = '.xlsx') -> None:

        extensions = {
            '.xlsx': self._save_as_excel
        }

        if file_extension in extensions: extensions[file_extension]()

        else: return None

    def _save_as_excel(self, order: Order) -> None:
        
        workbook = order.to_excel_workbook()
        workbook.save(self.get_file_path(order, '.xlsx'))

        return 
    
    def sort_orders(self) -> None:
        """Sorts order files into vendor-specific subdirectories within the orders directory."""
        orders_dir = self.get_order_files_directory()
        
        for file in orders_dir.iterdir():
            
            if file.is_file() and OrderManager.is_valid_filename(file):
                
                order_info = self.parse_file_name(file)
                vendor_name = order_info.get('vendor')
                
                if not vendor_name:
                    raise ValueError(f'Filename "{file.stem}" does not contain a valid vendor name.')

                vendor_dir = orders_dir / vendor_name  # Target directory for vendor
                vendor_dir.mkdir(exist_ok=True)  # Create vendor directory if it doesn't exist
                
                new_path = vendor_dir / file.name
                file.rename(new_path)  # Move file into the vendor directory
                # print(f'Moved: {file.name} → {new_path}')  # Debug output
     
    @classmethod
    def is_valid_filename(cls, filename: Path) -> bool:
        return cls.file_pattern.match(filename.stem)
    
    @classmethod
    def parse_file_name(cls, filename: Path) -> dict:
        if cls.is_valid_filename(filename): 
            return cls.file_pattern.match(filename.stem).groupdict()
        raise ValueError(f'Filename "{filename}" does not match expected pattern.')
        