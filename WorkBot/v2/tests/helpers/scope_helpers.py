from __future__ import annotations

from apps.api.auth.scopes import SUPERVISOR_SCOPE_ID


SUPERVISOR_SCOPE_PARAMS = {
    "scope_id": SUPERVISOR_SCOPE_ID,
}


def store_scope_params(store_id: str) -> dict[str, str]:
    return {
        "scope_id": store_id,
    }