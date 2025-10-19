"""
Tests for backend.app.ports.generic

These tests verify that:
  • Each port (Protocol) defines the expected contract surface.
  • Concrete adapters (like OrderFileRepository, VendorFilenameStrategy)
    conform to those contracts and produce valid outputs.

We don't test real file I/O or serialization logic here — just the structure and compliance.
"""

from backend.app.ports import generic
from backend.adapters.repos.order_file_repository import OrderFileRepository
from backend.adapters.repos.vendor_file_repository import VendorFileRepository
from backend.adapters.repos.store_file_repository import StoreFileRepository
from backend.adapters.files.local_blob_store import LocalBlobStore

from backend.adapters.repos.vendor_file_repository import VendorFileRepository
from backend.adapters.repos.order_file_repository import OrderFileRepository
from backend.adapters.repos.store_file_repository import StoreFileRepository
from backend.domain.models import Order, Vendor, Store
from backend.adapters.repos.vendor_file_repository import VendorFileRepository
from backend.domain.naming.vendor_namer import VendorFilenameStrategy

from pathlib import Path
import inspect
import tempfile
import pytest


# ----------------------------------------------------------------------
# ---- Serializer Protocol ---------------------------------------------
# ----------------------------------------------------------------------
def test_serializer_protocol_has_expected_methods():
    methods = {name for name, _ in inspect.getmembers(generic.Serializer, predicate=inspect.isfunction)}
    expected = {"preferred_format", "dumps", "loads", "load_path", "get_formatter"}
    assert expected.issubset(methods), f"Serializer missing methods: {expected - methods}"


# ----------------------------------------------------------------------
# ---- Namer Protocol ---------------------------------------------------
# ----------------------------------------------------------------------
def test_namer_protocol_defines_core_methods():
    methods = {name for name, _ in inspect.getmembers(generic.Namer, predicate=inspect.isfunction)}
    expected = {"base_dir", "filename", "parse_filename_for_metadata", "path_for", "parse_path_metadata"}
    assert expected.issubset(methods), f"Namer missing: {expected - methods}"


def test_vendor_filename_strategy_conforms_to_namer(tmp_path):
    """Verify VendorFilenameStrategy implements Namer contract."""
    namer = VendorFilenameStrategy(base=tmp_path)
    assert hasattr(namer, "base_dir")
    assert hasattr(namer, "filename")
    assert hasattr(namer, "path_for")
    assert hasattr(namer, "parse_filename_for_metadata")

    vendor = Vendor(name="Sysco")
    path = namer.path_for(vendor, format="json")
    assert isinstance(path, Path)
    assert path.suffix == ".json"
    assert "Sysco" in path.name


# ----------------------------------------------------------------------
# ---- Repository Protocol ----------------------------------------------
# ----------------------------------------------------------------------
def test_repository_protocol_methods_exist():
    methods = {name for name, _ in inspect.getmembers(generic.Repository, predicate=inspect.isfunction)}
    expected = {"get", "list_all", "save", "remove"}
    assert expected.issubset(methods), f"Repository missing: {expected - methods}"


def test_order_file_repository_exposes_repo_contract(tmp_path):
    """Ensure OrderFileRepository provides all expected Repository methods."""
    repo = OrderFileRepository(base_dir=tmp_path, uploads_dir=tmp_path)
    for method in ("get", "list_all", "save", "remove"):
        assert hasattr(repo, method), f"OrderFileRepository missing {method}()"


# ----------------------------------------------------------------------
# ---- BlobStore Protocol -----------------------------------------------
# ----------------------------------------------------------------------
def test_blobstore_protocol_defines_full_surface():
    methods = {name for name, _ in inspect.getmembers(generic.BlobStore, predicate=inspect.isfunction)}
    expected = {
        "write_bytes", "read_bytes", "exists", "remove", "move",
        "list_paths", "iter_files", "ensure_dir"
    }
    assert expected.issubset(methods), f"BlobStore missing: {expected - methods}"


def test_local_blob_store_conforms_to_blobstore(tmp_path):
    """Check LocalBlobStore supports all required BlobStore methods."""
    store = LocalBlobStore(base_dir=tmp_path)

    for name in (
        "write_bytes", "read_bytes", "exists", "remove", "move", "list_paths", "iter_files", "ensure_dir"
    ):
        assert hasattr(store, name), f"LocalBlobStore missing {name}()"

    # simple write/read roundtrip
    path = tmp_path / "hello.txt"
    data = b"hello world"
    store.write_bytes(path, data)
    assert store.exists(path)
    read = store.read_bytes(path)
    assert read == data
    store.remove(path)
    assert not store.exists(path)
