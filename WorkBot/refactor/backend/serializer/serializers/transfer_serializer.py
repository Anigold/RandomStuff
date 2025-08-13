from backend.models.transfer import Transfer, TransferItem
from backend.serializer.serializers.base_serializer import BaseSerializer
from typing import Any

class TransferSerializer(BaseSerializer):
    DEFAULT_HEADERS = ['SKU', 'Name', 'Quantity', 'From Store', 'To Store']

    def get_headers(self) -> list[str]:
        return self.DEFAULT_HEADERS

    def to_rows(self, transfer: Transfer) -> list[list[Any]]:
        rows = []
        for item in transfer.transfer_items:
            rows.append([
                item.name,
                item.quantity,
                transfer.origin,
                transfer.destination
            ])
        return rows

    def from_rows(self, rows: list[list[Any]], metadata: dict = None) -> Transfer:
        metadata = metadata or {}
        origin = metadata.get('origin')
        destination = metadata.get('destination')
        transfer_date = metadata.get('transfer_date')

        transfer = Transfer(origin=origin, destination=destination, transfer_date=transfer_date, transfer_items=[])
        for row in rows:
            name, quantity, *_ = row
            item = TransferItem(name, quantity)
            transfer.transfer_items.append(item)

        return transfer
