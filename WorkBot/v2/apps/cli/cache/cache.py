from __future__ import annotations

from collections.abc import Hashable, Iterable
from typing import Generic, TypeVar


K = TypeVar("K", bound=Hashable)
T = TypeVar("T")


class Cache(Generic[K, T]):
    def __init__(self) -> None:
        self._items: dict[K, T] = {}
        self._loaded = False

    @property
    def loaded(self) -> bool:
        """
        True when the cache is known to contain a complete snapshot.
        """
        return self._loaded

    def get(self, key: K) -> T | None:
        return self._items.get(key)

    def all(self) -> list[T]:
        return list(self._items.values())

    def keys(self) -> list[K]:
        return list(self._items.keys())

    def replace(self, items: Iterable[tuple[K, T]]) -> None:
        """
        Replace the cache with a complete snapshot.

        Calling replace() marks the cache as loaded.
        """
        self._items = dict(items)
        self._loaded = True

    def upsert(self, key: K, item: T) -> None:
        """
        Insert or replace a single cached item.

        This intentionally does NOT mark an unloaded cache as loaded,
        because the cache may still contain only a partial dataset.
        """
        self._items[key] = item

    def remove(self, key: K) -> None:
        self._items.pop(key, None)

    def invalidate(self) -> None:
        """
        Mark the cache as stale without discarding its contents.
        """
        self._loaded = False

    def clear(self) -> None:
        self._items.clear()
        self._loaded = False

    def __contains__(self, key: K) -> bool:
        return key in self._items

    def __len__(self) -> int:
        return len(self._items)