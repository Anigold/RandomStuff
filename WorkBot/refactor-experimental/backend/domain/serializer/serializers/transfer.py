from pathlib import Path
from typing import Any, Dict, Optional
from backend.domain.models import Transfer, TransferItem
from backend.core.interfaces.serializer import Serializer
from ..formats import get_formatter 
from backend.infra.logger import Logger
from backend.core.interfaces.formatter import BaseFormatter

@Logger.attach_logger
class TransferSerializer(Serializer[Transfer]):

    def __init__(self, default_format: str = 'xlsx'):
        self.default_format = default_format

    def preferred_format(self) -> str:
        return self.default_format

    # ----------------- Dumps -----------------
    def dumps(self, obj: Transfer, format: Optional[str] = None, context: dict | None = None) -> bytes:
        
        fmt = format or self.preferred_format()
        formatter = self.get_formatter(fmt)

        order_dict = self.to_dict(obj)
        order_tablular = self._to_table(order_dict)
        
        return formatter.dumps(order_tablular, context=context)

    # ----------------- Loads -----------------
    def loads(self, data: bytes, format: Optional[str] = None) -> Transfer:
        fmt = format or self.preferred_format()
        formatter = self.get_formatter(fmt)
        payload = formatter.loads(data)

        if fmt in ("xlsx", "csv"):
            return self.from_table(payload) 
        else:
            return self.from_dict(payload)

    def load_path(self, path: Path, context: dict | None = None) -> Transfer:
        
        fmt = path.suffix.lstrip(".").lower()
   
        formatter = self.get_formatter(fmt)

        payload = formatter.load_path(path, context=context)
    
        return self.from_table(payload)



    def get_formatter(self, fmt: str) -> BaseFormatter:
        return get_formatter(fmt)


        # -------- Domain <-> dict --------
    def to_dict(self, transfer: Transfer) -> Dict[str, Any]:
        return {
            "origin": transfer.origin,
            'destination': transfer.destination,
            'transfer_date': transfer.transfer_date,
            'transfer_items': [
                {
                    "name": i.name,
                    "quantity": i.quantity,
                }
                for i in transfer.transfer_items
            ]
        }

    def from_dict(self, data: Dict[str, Any]) -> Transfer:
        return Transfer(
            origin=data['origin'],
            destination=data['destination'],
            transfer_date=data['transfer_date'],
            transfer_items=[
                TransferItem(
                    name=i['name'],
                    quantity=i['quantity']
                )
                for i in data['transfer_items']
            ]
        )

    # -------- Domain <-> tabular --------
    def _to_table(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'headers': ['Name', 'Quantity'],
            'rows': [[i['name'], i['quantity']] for i in data['transfer_items']],
            'metadata': {
                'origin': data['origin'],
                'destination': data['destination'],
                'transfer_date': data['transfer_date']
            }
        }

    def from_table(self, table: Dict[str, Any]) -> Transfer:
        return Transfer(
            origin=table['metadata']['origin'],
            destination=table['metadata']['destination'],
            transfer_date=table['metadata']['transfer_date'],
            transfer_items=[
                TransferItem(
                    name=i[0],
                    quantity=i[1]
                )
                for i in table['rows']
            ]
        )
