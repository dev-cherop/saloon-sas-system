import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.customer import (
    CustomerCreate,
    CustomerRead,
    CustomerUpdate,
)
from app.services.customer import (
    create_customer,
    get_customer,
    list_customers,
    update_customer,
)


router = APIRouter(
    prefix="/api/v1/businesses/{business_id}/customers",
    tags=["Customers"],
)


@router.post(
    "",
    response_model=CustomerRead,
    status_code=status.HTTP_201_CREATED,
)
def create_customer_endpoint(
    business_id: uuid.UUID,
    payload: CustomerCreate,
    db: Session = Depends(get_db),
):
    customer = create_customer(
        db,
        business_id,
        payload,
    )

    if customer is None:
        raise HTTPException(
            status_code=404,
            detail="Business not found or inactive",
        )

    return customer


@router.get(
    "",
    response_model=list[CustomerRead],
)
def list_customers_endpoint(
    business_id: uuid.UUID,
    search: str | None = Query(
        default=None,
        max_length=100,
    ),
    db: Session = Depends(get_db),
):
    return list_customers(
        db,
        business_id,
        search,
    )


@router.get(
    "/{customer_id}",
    response_model=CustomerRead,
)
def get_customer_endpoint(
    business_id: uuid.UUID,
    customer_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    customer = get_customer(
        db,
        business_id,
        customer_id,
    )

    if customer is None:
        raise HTTPException(
            status_code=404,
            detail="Customer not found",
        )

    return customer


@router.patch(
    "/{customer_id}",
    response_model=CustomerRead,
)
def update_customer_endpoint(
    business_id: uuid.UUID,
    customer_id: uuid.UUID,
    payload: CustomerUpdate,
    db: Session = Depends(get_db),
):
    customer = update_customer(
        db,
        business_id,
        customer_id,
        payload,
    )

    if customer is None:
        raise HTTPException(
            status_code=404,
            detail="Customer not found",
        )

    return customer