from __future__ import annotations
from dataclasses import dataclass

from backend.app.ports import (
    ItemRepository, 

)


from dataclasses import dataclass
from typing import Optional, Callable, List
from pathlib import Path
from pprint import pprint

from backend.domain.models import Item
from backend.infra.logger import Logger


# ========== QUERIES ==========
@Logger.attach_logger
@dataclass(frozen=True)
class GetItem:

    repo: ItemRepository

    def __call__(self, item_id: str) -> Item:
        return self.repo.get(item_id)


@Logger.attach_logger
@dataclass(frozen=True)
class GetItemByName:

    repo: ItemRepository

    def __call__(self, item_name: str) -> Item:
        return self.repo.get_by_name(item_name)


@Logger.attach_logger
@dataclass(frozen=True)
class GetAllItemNames:

    repo: ItemRepository

    def __call__(self) -> list[str]:
        return self.repo.get_item_names()


@Logger.attach_logger
@dataclass(frozen=True)
class ListItems:

    repo: ItemRepository

    def __call__(self,) -> list[Item]:
        return self.repo.list_all()


@Logger.attach_logger
@dataclass(frozen=True)
class CreateItem:

    repo: ItemRepository
    # factory: ItemFactory

    def __call__(self, *, name: str, **kwargs) -> Item:
        ...

@Logger.attach_logger
@dataclass(frozen=True)
class RemoveItem:

    repo: ItemRepository

    def __call__(self, item_id: str) -> None:
        ...

@Logger.attach_logger
@dataclass(frozen=True)
class UpdateItem:

    repo: ItemRepository

    def __call__(self, item_id: str, updater: Callable) -> None:
        self.repo.update(item_id, updater)


@dataclass
class ItemServices:

    repo:      ItemRepository
    # downloads: DownloadManagerPort

    def __post_init__(self) -> None:
        
        self.get_item = GetItem(self.repo)
        self.get_item_by_name = GetItemByName(self.repo)
        self.list_items = ListItems(self.repo)
        self.get_all_item_names = GetAllItemNames(self.repo)

        self.create_item = CreateItem(self.repo)
        self.remove = RemoveItem(self.repo)
        self.update = UpdateItem(self.repo)
