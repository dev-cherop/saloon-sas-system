from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.models.customer_visit import CustomerVisit


def get_customer_spending_summary(
    db: Session,
    business_id: UUID,
    customer_id: UUID,
):
    customer = (
        db.query(Customer)
        .filter(
            Customer.id == customer_id,
            Customer.business_id == business_id,
        )
        .first()
    )

    if customer is None:
        raise HTTPException(
            status_code=404,
            detail="Customer not found",
        )

    visits = db.query(CustomerVisit).filter(
        CustomerVisit.business_id == business_id,
        CustomerVisit.customer_id == customer_id,
    )

    totals = visits.with_entities(
        func.count(CustomerVisit.id).label("total_visits"),
        func.coalesce(
            func.sum(CustomerVisit.amount), 0
        ).label("total_spent"),
        func.coalesce(
            func.avg(CustomerVisit.amount), 0
        ).label("average_spend"),
        func.max(
            CustomerVisit.visited_at
        ).label("last_visit"),
    ).one()

    frequent_services = (
        visits.with_entities(
            CustomerVisit.service_name.label("service_name"),
            func.count(CustomerVisit.id).label("visit_count"),
            func.sum(CustomerVisit.amount).label("total_spent"),
        )
        .group_by(CustomerVisit.service_name)
        .order_by(
            func.count(CustomerVisit.id).desc(),
            func.sum(CustomerVisit.amount).desc(),
        )
        .limit(5)
        .all()
    )

    return {
        "customer_id": customer_id,
        "total_visits": totals.total_visits,
        "total_spent": totals.total_spent,
        "average_spend": totals.average_spend,
        "last_visit": totals.last_visit,
        "most_frequent_services": [
            {
                "service_name": service.service_name,
                "visit_count": service.visit_count,
                "total_spent": service.total_spent,
            }
            for service in frequent_services
        ],
    }
