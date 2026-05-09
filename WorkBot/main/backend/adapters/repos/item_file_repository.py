from pathlib import Path

from backend.app.ports import ItemRepository
from backend.adapters.files.generic_file_adapter import GenericFileAdapter
from backend.domain.serializer.serializers.item import ItemSerializer
from backend.domain.naming.item_namer import ItemFilenameStrategy
from backend.domain.models import Item
from backend.infra.filesystem.local_blob_store import LocalBlobStore
from backend.infra.logger import Logger

import json
from typing import Callable, Any


@Logger.attach_logger
class ItemFileRepository(ItemRepository):
    """File-backed implementation of ItemRepository using GenericFileAdapter."""

    def __init__(self, base_dir: Path):
        self._engine = GenericFileAdapter[Item](
            store=LocalBlobStore(),
            serializer=ItemSerializer(default_format="json"),
            namer=ItemFilenameStrategy(base=base_dir),
        )

    # ---- Repository API ----

    def get(self, item_id: str) -> Item:
        """
        Primary lookup by stable ID filename.

        Includes a fallback scan for backward compatibility in case older
        files were saved under name-based filenames.
        """
        direct_path = (self._engine.get_directory() / f"{item_id}.json").resolve()

        if self._engine.store.exists(direct_path):
            return self._engine.read_from_path(direct_path)

        # Backward-compatibility fallback:
        # scan existing item files and compare the loaded object's ID
        for path in self._engine.list_files("*.json"):
            try:
                item = self._engine.read_from_path(path)
                if item.id == item_id:
                    return item
            except Exception as e:
                self.logger.info(f"Skipping unreadable item file {path}: {e}")

        raise FileNotFoundError(f"Item not found: {item_id}")
    
    def get_by_name(self, item_name: str) -> Item:
        
        # Look up in the index.
        index_path = (self._engine.get_directory() / 'index.json')
        if not self._engine.store.exists(index_path):
            raise FileNotFoundError(f'Index search file not found.')
        
        
        with open(index_path, 'r') as f:
            item_index = json.load(f)

        if item_name not in item_index:
            raise FileNotFoundError(f'Item not found in index [ignore error type for now]')

        item_file_path = (self._engine.get_directory() / f'{item_index[item_name]}.json').resolve()

        return self._engine.read_from_path(item_file_path)

    def get_item_names(self) -> list[str]:
        
        item_names: list[str] = []

        index_path = (self._engine.get_directory() / 'index.json')
        if not self._engine.store.exists(index_path):
            raise FileNotFoundError(f'Index search file not found.')
        
        
        with open(index_path, 'r') as f:
            item_index = json.load(f)

        return item_index.keys()




    def list_all(self) -> list[Item]:
        
        items: list[Item] = []

        directory = self._engine.get_directory()
        # self.logger.info(f"DEBUG directory={directory!r}")

        direct_paths = self._engine.store.list_paths(directory, "*.json")
        # self.logger.info(f"DEBUG direct_paths={direct_paths!r}")

        engine_paths = self._engine.list_files("*.json")
        # self.logger.info(f"DEBUG engine_paths={engine_paths!r}")

        for path in engine_paths:
            try:
                items.append(self._engine.read_from_path(path))
            except Exception as e:
                self.logger.info(f"Skipping unreadable item file {path}: {e}")

        return items

    def save(self, item: Item, format: str | None = None, context: dict | None = None) -> Path:
        """
        Persist an item using the serializer's preferred format by default.
        """
        return self._engine.save(item, format=format, context=context)

    def save_data(self, data: bytes, path_override: Path, overwrite: bool = True) -> Path:
        """
        Pass-through raw save for import/export workflows when needed.
        """
        return self._engine.save_data(
            data=data,
            path_override=path_override,
            overwrite=overwrite,
        )

    def update(self, 
        item_id: str, 
        updater: Callable[[Item], Item], 
        *args: Any, 
        **kwargs: Any
    ) -> Item:
        
        item = self.get(item_id)

        updated = updater(item, *args, **kwargs)
        item_to_save = updated if updated is not None else item

        if item_to_save.id != item.id:
            raise ValueError(f'Item ID cannot be changed during standard update: {item_id} --/-> {item_to_save.id}')

        self.save(item_to_save)
        return item_to_save
    
    def remove(self, item_id: str) -> None:
        """
        Remove the item file if it exists.
        """
        try:
            item = self.get(item_id)
            fmt = self._engine.preferred_format()
            path = self._engine.get_file_path(item, format=fmt)
            self._engine.remove(path)
        except FileNotFoundError:
            pass

    def find(self, **criteria) -> list[Item]:
        """
        Delegate metadata-based discovery to the generic file adapter.
        """
        return self._engine.find(**criteria)