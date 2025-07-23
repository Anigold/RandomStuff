from backend.exporters.adapters.exporter_adapter import ExportAdapter

@ExportAdapter.register("Performance Food")
class PerformanceFoodAdapter(ExportAdapter):
    preferred_format = "csv"
    preferred_delimiter = ","

    def modify_headers(self, headers: list[str]) -> list[str]:
        return []

    def modify_row(self, row: list, item: object = None) -> list:
        return [item.sku, int(item.quantity), "CS"]
