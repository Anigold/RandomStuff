from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from apps.api.dependencies import get_db_session
from apps.api.schemas.vendor_schema import (
    ContactInfoSchema,
    CreateVendorRequest,
    OrderingInfoSchema,
    ScheduleEntrySchema,
    UpdateVendorRequest,
    VendorResponse,
    VendorStoreReferenceSchema,
)
from workbot_core.application.dto.vendor_commands import (
    CreateVendorCommand,
    UpdateVendorCommand,
)
from workbot_core.application.use_cases.vendors.manage_vendors import ManageVendors
from workbot_core.domain.models.vendor import (
    ContactInfo,
    OrderingInfo,
    ScheduleEntry,
    Vendor,
    VendorStoreReference,
)
from workbot_core.infrastructure.database.repositories.vendor_repository import (
    SqlVendorRepository,
)
from workbot_core.domain.models.user import User
from apps.api.auth.dependencies import require_supervisor, get_current_user

router = APIRouter(
    prefix="/vendors",
    tags=["vendors"],
    # dependencies=[Depends(require_supervisor)]
)


@router.get("", response_model=list[VendorResponse])
def list_vendors(
    search: str | None = None,
    include_inactive: bool = True,
    session: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> list[VendorResponse]:
    vendors = ManageVendors(
        vendors=SqlVendorRepository(session),
    ).list_vendors(
        search=search,
        include_inactive=include_inactive,
    )

    return [_vendor_response(vendor) for vendor in vendors]


@router.get("/{vendor_id}", response_model=VendorResponse)
def get_vendor(
    vendor_id: str,
    session: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> VendorResponse:
    try:
        vendor = ManageVendors(
            vendors=SqlVendorRepository(session),
        ).get_vendor(vendor_id)

        return _vendor_response(vendor)

    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("", response_model=VendorResponse, status_code=201)
def create_vendor(
    request: CreateVendorRequest,
    session: Session = Depends(get_db_session),
    current_user: User = Depends(require_supervisor),
) -> VendorResponse:
    try:
        vendor = ManageVendors(
            vendors=SqlVendorRepository(session),
        ).create_vendor(
            CreateVendorCommand(
                name=request.name,
                is_active=request.is_active,
                order_format=request.order_format,
                special_notes=request.special_notes,
                min_order_value=request.min_order_value,
                min_order_cases=request.min_order_cases,
                internal_contacts=_contact_info_commands(request.internal_contacts),
                ordering=_ordering_info_command(request.ordering),
                store_references=_store_reference_commands(
                    request.store_references
                ),
            )
        )

        session.commit()

        return _vendor_response(vendor)

    except ValueError as exc:
        session.rollback()
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.put("/{vendor_id}", response_model=VendorResponse)
def update_vendor(
    vendor_id: str,
    request: UpdateVendorRequest,
    session: Session = Depends(get_db_session),
    current_user: User = Depends(require_supervisor),
) -> VendorResponse:
    try:
        vendor = ManageVendors(
            vendors=SqlVendorRepository(session),
        ).update_vendor(
            UpdateVendorCommand(
                vendor_id=vendor_id,
                name=request.name,
                is_active=request.is_active,
                order_format=request.order_format,
                special_notes=request.special_notes,
                min_order_value=request.min_order_value,
                min_order_cases=request.min_order_cases,
                internal_contacts=_contact_info_commands(request.internal_contacts),
                ordering=_ordering_info_command(request.ordering),
                store_references=_store_reference_commands(
                    request.store_references
                ),
            )
        )

        session.commit()

        return _vendor_response(vendor)

    except ValueError as exc:
        session.rollback()
        raise _http_error_from_value_error(exc) from exc


@router.delete("/{vendor_id}", response_model=VendorResponse)
def delete_vendor(
    vendor_id: str,
    session: Session = Depends(get_db_session),
    current_user: User = Depends(require_supervisor),
) -> VendorResponse:
    try:
        vendor = ManageVendors(
            vendors=SqlVendorRepository(session),
        ).deactivate_vendor(vendor_id)

        session.commit()

        return _vendor_response(vendor)

    except ValueError as exc:
        session.rollback()
        raise HTTPException(status_code=404, detail=str(exc)) from exc


def _http_error_from_value_error(exc: ValueError) -> HTTPException:
    message = str(exc)

    if "not found" in message.casefold():
        return HTTPException(status_code=404, detail=message)

    return HTTPException(status_code=400, detail=message)


def _contact_info_commands(
    contacts: list[ContactInfoSchema],
) -> tuple[ContactInfo, ...]:
    return tuple(
        ContactInfo(
            name=contact.name,
            title=contact.title,
            email=contact.email,
            phone=contact.phone,
        )
        for contact in contacts
    )


def _ordering_info_command(ordering: OrderingInfoSchema) -> OrderingInfo:
    return OrderingInfo(
        method=tuple(ordering.method),
        email=ordering.email,
        portal_url=ordering.portal_url,
        phone_number=ordering.phone_number,
        schedule=tuple(
            ScheduleEntry(
                order_day=entry.order_day,
                delivery_days=tuple(entry.delivery_days),
                cutoff_time=entry.cutoff_time,
            )
            for entry in ordering.schedule
        ),
    )


def _store_reference_commands(
    store_references: list[VendorStoreReferenceSchema],
) -> tuple[VendorStoreReference, ...]:
    return tuple(
        VendorStoreReference(
            store_id=reference.store_id,
            vendor_store_reference=reference.vendor_store_reference,
        )
        for reference in store_references
    )


def _vendor_response(vendor: Vendor) -> VendorResponse:
    return VendorResponse(
        id=vendor.id,
        name=vendor.name,
        is_active=vendor.is_active,
        order_format=vendor.order_format,
        special_notes=vendor.special_notes,
        min_order_value=vendor.min_order_value,
        min_order_cases=vendor.min_order_cases,
        internal_contacts=[
            ContactInfoSchema(
                name=contact.name,
                title=contact.title,
                email=contact.email,
                phone=contact.phone,
            )
            for contact in vendor.internal_contacts
        ],
        ordering=OrderingInfoSchema(
            method=list(vendor.ordering.method),
            email=vendor.ordering.email,
            portal_url=vendor.ordering.portal_url,
            phone_number=vendor.ordering.phone_number,
            schedule=[
                ScheduleEntrySchema(
                    order_day=entry.order_day,
                    delivery_days=list(entry.delivery_days),
                    cutoff_time=entry.cutoff_time,
                )
                for entry in vendor.ordering.schedule
            ],
        ),
        store_references=[
            VendorStoreReferenceSchema(
                store_id=reference.store_id,
                vendor_store_reference=reference.vendor_store_reference,
            )
            for reference in vendor.store_references
        ],
        created_at=vendor.created_at,
        updated_at=vendor.updated_at,
    )