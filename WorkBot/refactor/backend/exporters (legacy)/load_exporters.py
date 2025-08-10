import importlib
import pkgutil
import sys
from pathlib import Path

def load_exporters():
    """
    Dynamically imports all modules in the exporters package to ensure decorators run.
    """
    package = "backend.exporters"
    package_path = Path(__file__).parent

    for (_, name, is_pkg) in pkgutil.iter_modules([str(package_path)]):
        if not is_pkg:
            importlib.import_module(f"{package}.{name}")