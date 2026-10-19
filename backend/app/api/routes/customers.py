import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.authorization import require_permission
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
    delete_customer,
)

from app.schemas.customer_visit import (
    CustomerVisitCreate,
    CustomerVisitRead,
)

from app.schemas.customer_summary import CustomerSpendingSummary


from app.services.customer_visit import (
    create_customer_visit,
    get_customer_visits,
)

from app.services.customer_summary import (
    get_customer_spending_summary,
)



router = APIRouter(
    prefix="/api/v1/businesses/{business_id}/customers",
    tags=["Customers"],
)


# --------------------------------------------------
# Create customer
# --------------------------------------------------

@router.post(
    "",
    response_model=CustomerRead,
    status_code=status.HTTP_201_CREATED,
)
def create_customer_endpoint(
    business_id: uuid.UUID,
    payload: CustomerCreate,
    db: Session = Depends(get_db),
    _membership=Depends(
        require_permission("customers:create")
    ),
):
    customer = create_customer(
        db,
        business_id,
        payload,
    )

    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found or inactive",
        )

    return customer


# --------------------------------------------------
# List and search customers
# --------------------------------------------------

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
    _membership=Depends(
        require_permission("customers:read")
    ),
):
    return list_customers(
        db,
        business_id,
        search,
    )


# --------------------------------------------------
# Get one customer
# --------------------------------------------------

@router.get(
    "/{customer_id}",
    response_model=CustomerRead,
)
def get_customer_endpoint(
    business_id: uuid.UUID,
    customer_id: uuid.UUID,
    db: Session = Depends(get_db),
    _membership=Depends(
        require_permission("customers:read")
    ),
):
    customer = get_customer(
        db,
        business_id,
        customer_id,
    )

    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found",
        )

    return customer


# --------------------------------------------------
# Update customer
# --------------------------------------------------

@router.patch(
    "/{customer_id}",
    response_model=CustomerRead,
)
def update_customer_endpoint(
    business_id: uuid.UUID,
    customer_id: uuid.UUID,
    payload: CustomerUpdate,
    db: Session = Depends(get_db),
    _membership=Depends(
        require_permission("customers:update")
    ),
):
    customer = update_customer(
        db,
        business_id,
        customer_id,
        payload,
    )

    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found",
        )

    return customer


# --------------------------------------------------
# Delete customer
# --------------------------------------------------

@router.delete(
    "/{customer_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_customer_endpoint(
    business_id: uuid.UUID,
    customer_id: uuid.UUID,
    db: Session = Depends(get_db),
    _membership=Depends(
        require_permission("customers:delete")
    ),
):
    deleted = delete_customer(
        db,
        business_id,
        customer_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found",
        )


# --------------------------------------------------
# Create customer visit / service record
# --------------------------------------------------

@router.post(
    "/{customer_id}/visits",
    response_model=CustomerVisitRead,
    status_code=status.HTTP_201_CREATED,
)
def create_customer_visit_endpoint(
    business_id: uuid.UUID,
    customer_id: uuid.UUID,
    payload: CustomerVisitCreate,
    db: Session = Depends(get_db),
    _membership=Depends(
        require_permission("customers:create")
    ),
):
    return create_customer_visit(
        db,
        business_id,
        customer_id,
        payload,
    )


# --------------------------------------------------
# Get customer visit / service history
# --------------------------------------------------

@router.get(
    "/{customer_id}/visits",
    response_model=list[CustomerVisitRead],
)
def get_customer_visits_endpoint(
    business_id: uuid.UUID,
    customer_id: uuid.UUID,
    db: Session = Depends(get_db),
    _membership=Depends(
        require_permission("customers:read")
    ),
):
    return get_customer_visits(
        db,
        business_id,
        customer_id,
    )



@router.get(
    "/{customer_id}/spending-summary",
    response_model=CustomerSpendingSummary,
)
def customer_spending_summary_endpoint(
    business_id: uuid.UUID,
    customer_id: uuid.UUID,
    db: Session = Depends(get_db),
    _membership=Depends(
        require_permission("customers:read")
    ),
):
    return get_customer_spending_summary(
        db,
        business_id,
        customer_id,
    )
