from dataclasses import dataclass, asdict
from typing import Dict, Optional

@dataclass
class StoreItemInfo:
    store_name: str
    store_id: str

    par: Optional[float]     = None
    on_hand: Optional[float] = None
    last_counted: str | None = None # Date

    is_active: bool = True

    