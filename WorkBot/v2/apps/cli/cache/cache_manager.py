from __future__ import annotations

from typing import Any

from .cache import Cache


class CacheManager:
    def __init__(self) -> None:
        self._caches: dict[str, Cache[Any, Any]] = {}
        self._scope_sensitive: set[str] = set()

    def register(
        self,
        name: str,
        *,
        scope_sensitive: bool = False,
    ) -> Cache[Any, Any]:
        if name in self._caches:
            raise ValueError(
                f"Cache already registered: {name}"
            )

        cache: Cache[Any, Any] = Cache()

        self._caches[name] = cache

        if scope_sensitive:
            self._scope_sensitive.add(name)

        return cache

    def get(
        self,
        name: str,
    ) -> Cache[Any, Any]:
        try:
            return self._caches[name]

        except KeyError as exc:
            raise KeyError(
                f"Cache not registered: {name}"
            ) from exc

    def clear(
        self,
        name: str,
    ) -> None:
        self.get(name).clear()

    def invalidate(
        self,
        name: str,
    ) -> None:
        self.get(name).invalidate()

    def clear_all(self) -> None:
        for cache in self._caches.values():
            cache.clear()

    def invalidate_all(self) -> None:
        for cache in self._caches.values():
            cache.invalidate()

    def clear_scope_sensitive(self) -> None:
        for name in self._scope_sensitive:
            self._caches[name].clear()

    def __contains__(self, name: str) -> bool:
        return name in self._caches

    def __getitem__(
        self,
        name: str,
    ) -> Cache[Any, Any]:
        return self.get(name)