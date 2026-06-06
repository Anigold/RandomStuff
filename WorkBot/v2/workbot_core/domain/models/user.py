from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class UserRole(StrEnum):
    SUPERVISOR = "supervisor"
    MANAGER    = "manager"
    VIEWER     = "viewer"


@dataclass(frozen=True, slots=True)
class User:
    id: str
    username: str
    password_hash: str
    role: UserRole

    is_active: bool = True

    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass(frozen=True, slots=True)
class UserStoreAccess:
    id: str
    user_id: str
    store_id: str

    created_at: datetime | None = None
    updated_at: datetime | None = None