from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.models.customer_visit import CustomerVisit
from app.schemas.customer_visit import CustomerVisitCreate


def create_customer_visit(
    db: Session,
    business_id: UUID,
    customer_id: UUID,
    visit_data: CustomerVisitCreate,
) -> CustomerVisit:
    from decimal import Decimal

    from app.models.loyalty_settings import LoyaltySettings
    from app.services.loyalty import award_points_for_visit

    customer = db.scalar(
        select(Customer).where(
            Customer.id == customer_id,
            Customer.business_id == business_id,
        )
    )

    if customer is None:
        raise HTTPException(
            status_code=404,
            detail="Customer not found",
        )

    data = visit_data.model_dump(exclude_unset=True)

    visit = CustomerVisit(
        business_id=business_id,
        customer_id=customer_id,
        **data,
    )

    try:
        db.add(visit)
        db.flush()

        settings = db.scalar(
            select(LoyaltySettings).where(
                LoyaltySettings.business_id == business_id,
            )
        )

        if settings is not None and settings.enabled:
            amount = Decimal(str(visit.amount))
            spend_per_point = Decimal(str(settings.spend_per_point))

            if spend_per_point > 0 and amount >= spend_per_point:
                award_points_for_visit(
                    db,
                    business_id,
                    visit.id,
                )

        db.commit()
        db.refresh(visit)
        return visit

    except Exception:
        db.rollback()
        raise



def get_customer_visits(
    db: Session,
    business_id: UUID,
    customer_id: UUID,
) -> list[CustomerVisit]:
    customer = db.scalar(
        select(Customer).where(
            Customer.id == customer_id,
            Customer.business_id == business_id,
        )
    )

    if customer is None:
        raise HTTPException(
            status_code=404,
            detail="Customer not found",
        )

    statement = (
        select(CustomerVisit)
        .where(
            CustomerVisit.business_id == business_id,
            CustomerVisit.customer_id == customer_id,
        )
        .order_by(CustomerVisit.visited_at.desc())
    )

    return list(db.scalars(statement).all())
