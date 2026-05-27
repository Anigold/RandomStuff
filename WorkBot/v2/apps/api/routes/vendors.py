from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from apps.api.dependencies import get_db_session
from workbot_core.infrastructure.database.repositories.vendor_repository import (
    SqlVendorRepository,
)


router = APIRouter(prefix="/vendors", tags=["vendors"])


@router.get("")
def list_vendors(session: Session = Depends(get_db_session)) -> list[dict]:
    vendors = SqlVendorRepository(session).list_all()

    return [
        {
            "id": vendor.id,
            "name": vendor.name,
            "is_active": vendor.is_active,
        }
        for vendor in vendors
    ]