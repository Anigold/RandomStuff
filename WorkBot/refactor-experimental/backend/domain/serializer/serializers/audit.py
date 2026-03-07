from pathlib import Path
from typing import Any, Dict, Optional
from backend.domain.models import Audit, AuditItem
from backend.core.interfaces.serializer import Serializer
from ..formats import get_formatter 
from backend.infra.logger import Logger
from backend.core.interfaces.formatter import BaseFormatter

@Logger.attach_logger
class AuditSerializer(Serializer[Audit]):

    def __init__(self, default_format: str = 'xlsx'):
        self.default_format = default_format

    def preferred_format(self) -> str:
        return self.default_format

    # ----------------- Dumps -----------------
    def dumps(self, obj: Audit, format: Optional[str] = None, context: dict | None = None) -> bytes:
        
        fmt = format or self.preferred_format()
        formatter = self.get_formatter(fmt)

        order_dict = self.to_dict(obj)
        order_tablular = self._to_table(order_dict)
        
        return formatter.dumps(order_tablular, context=context)

    # ----------------- Loads -----------------
    def loads(self, data: bytes, format: Optional[str] = None) -> Audit:
        fmt = format or self.preferred_format()
        formatter = self.get_formatter(fmt)
        payload = formatter.loads(data)

        if fmt in ("xlsx", "csv"):
            return self.from_table(payload) 
        else:
            return self.from_dict(payload)

    def load_path(self, path: Path, context: dict | None = None) -> Audit:
        
        fmt = path.suffix.lstrip(".").lower()
   
        formatter = self.get_formatter(fmt)

        payload = formatter.load_path(path, context=context)
    
        return self.from_table(payload)



    def get_formatter(self, fmt: str) -> BaseFormatter:
        return get_formatter(fmt)


        # -------- Domain <-> dict --------
    def to_dict(self, audit: Audit) -> Dict[str, Any]:
        return {
            "store": audit.store,
            "date": audit.date,
            "audit_type": audit.audit_type,
            "auditor": audit.auditor,
            "items": [self._audit_item_to_dict(i) for i in audit.items],
        }
    
    def from_dict(self, data: Dict[str, Any]) -> Audit:
        return Audit(
            store=data["store"],
            date=data["date"],
            audit_type=data["audit_type"],
            auditor=data["auditor"],
            items=[self._audit_item_from_dict(i) for i in data.get("items", [])],
        )
    
    def _audit_item_to_dict(self, item: "AuditItem") -> Dict[str, Any]:
        return {
            "item_name":   item.item_name,
            "count_unit":  item.count_unit,
            "on_hand":     item.on_hand,
            "category":    item.category,
            "subcategory": item.subcategory,
            "unit_price":  item.unit_price,
            "total_price": item.total_price,
        }

    def _audit_item_from_dict(self, data: Dict[str, Any]) -> "AuditItem":
        return AuditItem(
            item_name=str(data.get("item_name", "")).strip(),
            count_unit=str(data.get("count_unit", "")).strip(),
            on_hand=self._coerce_float(data.get("on_hand")),
            category=str(data.get("category", "")).strip(),
            subcategory=str(data.get("subcategory", "")).strip(),
            unit_price=self._coerce_float(data.get("unit_price")),
            total_price=self._coerce_float(data.get("total_price")),
        )
    
    @staticmethod
    def _coerce_float(value: Any) -> Optional[float]:
        """
        Accepts numbers or strings like '12', '12.5', '$12.50', ' 1,234.56 '.
        Returns None for blanks/unparseable values.
        """
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return float(value)

        s = str(value).strip()
        if s == "":
            return None

        # common cleanup for spreadsheets
        s = s.replace("$", "").replace(",", "")
        try:
            return float(s)
        except ValueError:
            return None
        

    def from_dict(self, data: Dict[str, Any]) -> "Audit":
        return Audit(
            store=data["store"],
            date=data["date"],
            audit_type=data["audit_type"],
            auditor=data["auditor"],
            items=[self._audit_item_from_dict(i) for i in data.get("items", [])],
        )

    # -------- Domain <-> tabular --------
    def _to_table(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'headers': ['Name', 'Total Quantity'],
            'rows': [[i['name'], i['quantity']] for i in data['items']],
            'metadata': {
                'store': data['store'],
                'date': data['date'],
                'audit_type': data['audit_type'],
                'auditor': data['auditor']
            }
        }

def from_table(self, table: dict) -> Audit:
    metadata = table.get("metadata") or {}
    headers = table.get("headers") or []
    rows = table.get("rows") or []

    # Build a case-insensitive header -> index lookup
    idx = {str(h).strip().lower(): i for i, h in enumerate(headers)}

    # Expect these exact header names from _to_table()
    name_i = idx.get("name")
    qty_i = idx.get("total quantity")

    if name_i is None or qty_i is None:
        raise ValueError(
            f"Invalid table headers. Expected at least 'Name' and 'Total Quantity'. Got: {headers}"
        )

    items: list[AuditItem] = []
    for r in rows:
        # Defensive: allow shorter rows
        name = r[name_i] if name_i < len(r) else ""
        qty = r[qty_i] if qty_i < len(r) else None

        items.append(
            AuditItem(
                item_name=str(name).strip(),
                on_hand=self._coerce_float(qty),
            )
        )

    return Audit(
        store=str(metadata.get("store", "")).strip(),
        date=str(metadata.get("date", "")).strip(),
        audit_type=str(metadata.get("audit_type", "")).strip(),
        auditor=str(metadata.get("auditor", "")).strip(),
        items=items,
    )