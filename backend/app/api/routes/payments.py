import uuid
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.core.authorization import require_permission
from app.db import get_db
from app.schemas.payment import PaymentCreate, PaymentRead
from app.services.payment import (
    create_payment,
    list_payments,
    summarize_payments,
)

router = APIRouter(
    prefix="/api/v1/businesses/{business_id}/payments",
    tags=["Payments"],
)


@router.post("", response_model=PaymentRead, status_code=status.HTTP_201_CREATED)
def create_payment_endpoint(
    business_id: uuid.UUID,
    payload: PaymentCreate,
    db: Session = Depends(get_db),
    _membership=Depends(require_permission("payments:create")),
):
    try:
        payment = create_payment(db, business_id, payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    if payment is None:
        raise HTTPException(
            status_code=404,
            detail="Customer visit or sale not found in this business",
        )

    return payment


@router.get("", response_model=list[PaymentRead])
def list_payments_endpoint(
    business_id: uuid.UUID,
    visit_id: uuid.UUID | None = None,
    sale_id: uuid.UUID | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    db: Session = Depends(get_db),
    _membership=Depends(require_permission("payments:read")),
):
    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=422,
            detail="start_date must be on or before end_date",
        )

    return list_payments(
        db,
        business_id,
        visit_id=visit_id,
        sale_id=sale_id,
        start_date=start_date,
        end_date=end_date,
    )


@router.get("/summary")
def payment_summary_endpoint(
    business_id: uuid.UUID,
    start_date: date | None = None,
    end_date: date | None = None,
    db: Session = Depends(get_db),
    _membership=Depends(require_permission("payments:read")),
):
    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=422,
            detail="start_date must be on or before end_date",
        )

    return summarize_payments(
        db,
        business_id,
        start_date=start_date,
        end_date=end_date,
    )