from backend.exporters.adapters.exporter_adapter import ExportAdapter

@ExportAdapter.register("Sysco")
class SyscoAdapter(ExportAdapter):

    preferred_format = "csv"

    def modify_headers(self, headers: list[str]) -> list[str]:
        # Sysco expects no header row
        return []

    def modify_row(self, row: list, item: object = None) -> list:
        return ["P", item.sku, int(item.quantity), 0]
