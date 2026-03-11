from backend.domain.models import Vendor
from typing import Dict, List
from functools import lru_cache
from backend.domain.serializer.serializers.vendor import VendorSerializer
from backend.infra.paths import VENDOR_FILES_DIR

_VENDORS: Dict[str, Vendor] = {}
serializer = VendorSerializer(default_format='json')

@lru_cache(maxsize=10)
def _load_all() -> None:
    for path in VENDOR_FILES_DIR.glob(serializer.preferred_format()):
        fmt = path.suffix.lstrip('.').lower()
        with path.open('rb') as f:
            vendor = serializer.loads(f.read(), format=fmt)
        _register_vendor(vendor) # Don't include inside the "with" indent to ensure file closure.

def _register_vendor(vendor: Vendor) -> None:
    '''Register a vendor by its name.'''
    _VENDORS[vendor.name] = vendor

def get_vendor(name: str) -> Vendor:
    '''Retrieve a vendor by name.'''
    for vendor_name, vendor in _load_all().items(): # Automatically checks the cache before calling the full _load_all
        if vendor_name.lower() == name.lower():
            return vendor
    return None

def list_vendors() -> List[Vendor]:
    return [vendor for vendor in _load_all.values()]

def reload_registry() -> None:
    _load_all.cache_clear()