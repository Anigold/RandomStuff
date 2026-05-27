from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from apps.api.dependencies import get_db_session
from workbot_core.infrastructure.database.repositories.store_repository import (
    SqlStoreRepository,
)


router = APIRouter(prefix="/stores", tags=["stores"])


@router.get("")
def list_stores(session: Session = Depends(get_db_session)) -> list[dict]:
    stores = SqlStoreRepository(session).list_all()

    return [
        {
            "id": store.id,
            "name": store.name,
            "is_active": store.is_active,
        }
        for store in stores
    ]