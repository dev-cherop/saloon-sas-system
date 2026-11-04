import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.authorization import require_permission
from app.db import get_db
from app.schemas.payroll import (
    PayrollCreate,
    PayrollRead,
    PayrollStatusUpdate,
    PayrollUpdate,
)
from app.services.payroll import (
    create_payroll,
    list_payroll,
    update_payroll,
    update_payroll_status,
)

router = APIRouter(
    prefix="/api/v1/businesses/{business_id}/payroll",
    tags=["Payroll"],
)


@router.post(
    "",
    response_model=PayrollRead,
    status_code=status.HTTP_201_CREATED,
)
def create_payroll_endpoint(
    business_id: uuid.UUID,
    payload: PayrollCreate,
    db: Session = Depends(get_db),
    _membership=Depends(require_permission("payroll:create")),
):
    return create_payroll(db, business_id, payload)


@router.get("", response_model=list[PayrollRead])
def list_payroll_endpoint(
    business_id: uuid.UUID,
    worker_id: uuid.UUID | None = None,
    payroll_status: str | None = Query(
        default=None,
        pattern="^(draft|approved|paid)$",
    ),
    db: Session = Depends(get_db),
    _membership=Depends(require_permission("payroll:read")),
):
    return list_payroll(
        db,
        business_id,
        worker_id=worker_id,
        payroll_status=payroll_status,
    )


@router.patch("/{payroll_id}", response_model=PayrollRead)
def update_payroll_endpoint(
    business_id: uuid.UUID,
    payroll_id: uuid.UUID,
    payload: PayrollUpdate,
    db: Session = Depends(get_db),
    _membership=Depends(require_permission("payroll:update")),
):
    return update_payroll(
        db,
        business_id,
        payroll_id,
        payload,
    )


@router.patch(
    "/{payroll_id}/status",
    response_model=PayrollRead,
)
def update_payroll_status_endpoint(
    business_id: uuid.UUID,
    payroll_id: uuid.UUID,
    payload: PayrollStatusUpdate,
    db: Session = Depends(get_db),
    _membership=Depends(require_permission("payroll:approve")),
):
    return update_payroll_status(
        db=db,
        business_id=business_id,
        payroll_id=payroll_id,
        new_status=payload.status,
        payment_method=payload.payment_method,
    )