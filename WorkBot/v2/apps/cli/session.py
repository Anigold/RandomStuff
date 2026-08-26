from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class CliSession:
    access_token: str | None = None
    active_scope_id: str | None = None

    @property
    def is_authenticated(self) -> bool:
        return self.access_token is not None

    def login(
        self,
        access_token: str,
    ) -> None:
        self.access_token = access_token

    def logout(self) -> None:
        self.access_token = None
        self.active_scope_id = None

    def set_active_scope(
        self,
        scope_id: str | None,
    ) -> None:
        self.active_scope_id = scope_id