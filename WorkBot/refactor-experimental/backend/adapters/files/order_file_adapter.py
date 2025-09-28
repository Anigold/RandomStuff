from __future__ import annotations
from pathlib import Path
from typing import List, Optional

from backend.domain.models import Order
from backend.app.ports import OrderFilePort
from backend.adapters.files.generic_file_adapter import GenericFileAdapter
from backend.adapters.files.local_blob_store import LocalBlobStore
from backend.domain.serializer.serializers.order import OrderSerializer
from backend.domain.naming.order_namer import OrderFilenameStrategy

class OrderFileAdapter(OrderFilePort):
    """Implements OrderFilePort via the generic file engine."""

    def __init__(self, base_dir: Path):

        self._engine = GenericFileAdapter[Order](
            store=LocalBlobStore(),
            serializer= OrderSerializer(),
            namer=OrderFilenameStrategy(base=base_dir),
        )

    # Order-specific discovery
    def list_orders(self) -> List[Order]:
        return [self._engine.read(p) for p in self._engine.list_paths()]
    

    def get_order(self, store: str, vendor: str,) -> Order:

        path = self._engine.path_for(Order(store, vendor, None))
        """
        Discover saved order files, filtered by store, vendor, and format.

        Uses the Namer's base directory (vendor subdirs) and recurses
        into them when searching. Filters are applied via filename metadata.
        """
        
        # results: list[Path] = []

        # base_dir = self.get_directory().resolve()

        # for f in fmts:
        #     ext = "xlsx" if f in ("excel", "xlsx") else f
        #     # Search recursively in vendor subdirectories
        #     for p in base_dir.rglob(f"*.{ext}"):
        #         if not p.is_file():
        #             continue

        #         meta = self.parse_metadata(p.name)
                
        #         if (not stores or meta.get("store") in stores) and \
        #         (not vendors or meta.get("vendor") in vendors):
        #             results.append(p)
    
        # return sorted(results)

    # helper used by ExpectDownloadedPdf use-case if you need it elsewhere
    def target_pdf_path_for(self, order: Order) -> Path:
        return self.get_file_path(order, format="pdf")

    def generate_vendor_upload_file(self, order: Order, context: dict = None) -> None:
        return self._engine.serializer.dumps(order, format=order.vendor, context=context)


      

        adapter    = BaseAdapter.get_adapter(order.vendor)
        fmt        = BaseFormat.get_format(order.vendor)
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
