from fastapi import HTTPException, status

from apps.api.auth.dependencies import StoreScope


def require_supervisor_scope(scope: StoreScope) -> None:
    if not scope.is_supervisor_scope:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Supervisor scope required.",
        )


def require_store_in_scope(
    *,
    store_id: str,
    scope: StoreScope,
) -> None:
    if store_id not in scope.real_store_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Selected scope cannot access this store.",
        )


def require_single_store_scope(scope: StoreScope) -> str:
    if scope.is_supervisor_scope:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A single store scope is required for this operation.",
        )

    if len(scope.real_store_ids) != 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A single store scope is required for this operation.",
        )

    return scope.real_store_ids[0]