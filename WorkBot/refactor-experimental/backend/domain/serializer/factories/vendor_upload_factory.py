from backend.domain.models.order import Order
from backend.domain.serializer.filename_strategies.order_filename_strategy import OrderFilenameStrategy
from backend.domain.serializer.adapters.base_adapter import BaseAdapter
from backend.domain.serializer.formats.base_format import BaseFormat
from backend.domain.serializer.serializers.order_serializer import OrderSerializer
from backend.app.ports import OrderFilePort
from backend.adapters.files.order_file_adapter import OrderFileAdapter
from pathlib import Path

class VendorUploadFileFactory:
    def __init__(self, file_handler: OrderFilePort, output_dir: Path):
        self.file_handler      = file_handler or OrderFileHandler()

    def generate_upload_file(self, file_path: Path) -> Path:
        order = self.file_handler.get_order_from_file(file_path)

        adapter = BaseAdapter.get_adapter(order.vendor)
        fmt = BaseFormat.get_format(order.vendor)
        serializer = OrderSerializer(adapter=adapter)

        headers = serializer.get_headers()
        rows = serializer.to_rows(order)
        file_data = fmt.write(headers, rows)

        # override default suffix for special cases like Performance Food
        extension = 'txt' if order.vendor == 'Performance Food' else fmt.default_suffix.strip('.')
        filename = self.filename_strategy.format(order, extension=extension)
        output_path = self.output_dir / order.vendor / filename

        output_path.parent.mkdir(parents=True, exist_ok=True)
        self.file_handler._write_data(fmt.name, file_data, output_path)
        return output_path
