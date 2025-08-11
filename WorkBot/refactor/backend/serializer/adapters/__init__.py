from typing import Optional, Any

from .hill_n_markes_adapter import HillNMarkesAdapter
from .performance_food_adapter import PerformanceFoodAdapter
from .sysco_adapter import SyscoAdapter
from .unfi_adapter import UNFIAdapter
from .us_foods_adapter import USFoodsAdapter

_ADAPTERS = {
  'unfi': UNFIAdapter,
  'sysco': SyscoAdapter,
  'us foods': USFoodsAdapter,
  'performance food': PerformanceFoodAdapter,
  'hill & markes': HillNMarkesAdapter
}

_ALIASES = {
  'unfi llc': 'unfi',
  'usfoods': 'us foods',
  'sysco, inc.': 'sysco',
}

def _norm(s: str) -> str:
    return ' '.join(s.split()).strip().lower()

def get_adapter(vendor_name: str):
    key = _norm(vendor_name)
    key = _ALIASES.get(key, key)
    cls = _ADAPTERS.get(key)
    return cls() if cls else None

def get_vendor_context(vendor_name: str, **overrides: Any) -> Optional[dict]:
    '''
    Returns a context dict like:
      {'adapter': <BaseAdapter>, 'preferred_format': 'excel', ...overrides}
    or None if vendor unknown.
    '''
    adapter = get_adapter(vendor_name)
    return adapter.to_context(**overrides) if adapter else None
