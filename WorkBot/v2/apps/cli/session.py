from __future__ import annotations

from dataclasses import dataclass, field

from .cache import CacheManager, SCOPE_CACHE


@dataclass(slots=True)
class CliSession:
    access_token: str | None = None
    active_scope_id: str | None = None

    cache: CacheManager = field(
        default_factory=CacheManager,
        init=False, # Shouldn't be injecting cache configuration; keep it internal mechanism.
        repr=False,
    )

    def __post_init__(self) -> None:
        self.cache.register(SCOPE_CACHE)

    @property
    def is_authenticated(self) -> bool:
        return self.access_token is not None

    def login(self, access_token: str) -> None:
        self.cache.clear_all()

        self.access_token = access_token
        self.active_scope_id = None

    def logout(self) -> None:
        self.access_token = None
        self.active_scope_id = None

        self.cache.clear_all()

    def set_active_scope(self, scope_id: str | None) -> None:
        
        if self.active_scope_id == scope_id:
            return

        self.active_scope_id = scope_id
        self.cache.clear_scope_sensitive()