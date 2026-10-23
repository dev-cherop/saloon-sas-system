import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.authorization import require_permission
from app.db import get_db
from app.schemas.checkout import CheckoutCreate, SaleRead
from app.services.checkout import create_checkout, get_sale

router = APIRouter(
    prefix="/api/v1/businesses/{business_id}/checkout",
    tags=["Checkout"],
)


@router.post("", response_model=SaleRead, status_code=status.HTTP_201_CREATED)
def create_checkout_endpoint(
    business_id: uuid.UUID,
    payload: CheckoutCreate,
    db: Session = Depends(get_db),
    _membership=Depends(require_permission("checkout:create")),
):
    try:
        return create_checkout(db, business_id, payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get("/{sale_id}", response_model=SaleRead)
def get_sale_endpoint(
    business_id: uuid.UUID,
    sale_id: uuid.UUID,
    db: Session = Depends(get_db),
    _membership=Depends(require_permission("checkout:read")),
):
    sale = get_sale(db, business_id, sale_id)

    if sale is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sale not found in this business.",
        )

    return sale