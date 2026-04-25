from dataclasses import dataclass, asdict
from typing import Dict, Optional

@dataclass
class StoreItemInfo:
    store: str
    par: Optional[float] = None
    on_hand: Optional[float] = None
    