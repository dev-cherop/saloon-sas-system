import uuid
from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.customer_visit import CustomerVisit
from app.models.payment import Payment
from app.schemas.payment import PaymentCreate
from app.models.customer_visit import CustomerVisit
from app.models.sale import Sale
from app.services.loyalty import award_points_for_sale

def create_payment(
    db: Session,
    business_id: uuid.UUID,
    payload: PaymentCreate,
) -> Payment | None:
    if payload.visit_id is not None:
        visit = db.scalar(
            select(CustomerVisit).where(
                CustomerVisit.id == payload.visit_id,
                CustomerVisit.business_id == business_id,
            )
        )

        if visit is None:
            return None

        payment = Payment(
            business_id=business_id,
            visit_id=visit.id,
            sale_id=None,
            amount=payload.amount,
            payment_method=payload.payment_method,
            reference=payload.reference,
            notes=payload.notes,
        )

    else:
        sale = db.scalar(
    select(Sale)
    .where(
        Sale.id == payload.sale_id,
        Sale.business_id == business_id,
    )
    .with_for_update()
)

        if sale is None:
            return None

        if sale.status in ("cancelled", "paid"):
            raise ValueError("Cannot accept payment for this sale")

        already_paid = db.scalar(
            select(func.coalesce(func.sum(Payment.amount), 0)).where(
                Payment.business_id == business_id,
                Payment.sale_id == sale.id,
            )
        )
        already_paid = Decimal(str(already_paid or 0))
        outstanding = sale.total_amount - already_paid

        if payload.amount > outstanding:
            raise ValueError(
                f"Payment exceeds the outstanding balance of {outstanding}"
            )

        payment = Payment(
            business_id=business_id,
            visit_id=None,
            sale_id=sale.id,
            amount=payload.amount,
            payment_method=payload.payment_method,
            reference=payload.reference,
            notes=payload.notes,
        )

        sale.status = (
            "paid"
            if already_paid + payload.amount >= sale.total_amount
            else "partially_paid"
        )

        if sale.status == "paid":
            award_points_for_sale(
                db,
                business_id=business_id,
                sale_id=sale.id,
            )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    return payment

def list_payments(
    db: Session,
    business_id: uuid.UUID,
    visit_id: uuid.UUID | None = None,
    sale_id: uuid.UUID | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
) -> list[Payment]:
    query = select(Payment).where(Payment.business_id == business_id)

    if visit_id is not None:
        query = query.where(Payment.visit_id == visit_id)

    if sale_id is not None:
        query = query.where(Payment.sale_id == sale_id)
    if start_date is not None:
        start = datetime.combine(start_date, time.min, tzinfo=timezone.utc)
        query = query.where(Payment.paid_at >= start)

    if end_date is not None:
        end = datetime.combine(
            end_date + timedelta(days=1),
            time.min,
            tzinfo=timezone.utc,
        )
        query = query.where(Payment.paid_at < end)

    return list(
        db.scalars(query.order_by(Payment.paid_at.desc())).all()
    )


def summarize_payments(
    db: Session,
    business_id: uuid.UUID,
    start_date: date | None = None,
    end_date: date | None = None,
) -> dict:
    query = select(
        Payment.payment_method,
        func.sum(Payment.amount).label("total"),
        func.count(Payment.id).label("count"),
    ).where(Payment.business_id == business_id)

    if start_date is not None:
        start = datetime.combine(start_date, time.min, tzinfo=timezone.utc)
        query = query.where(Payment.paid_at >= start)

    if end_date is not None:
        end = datetime.combine(
            end_date + timedelta(days=1),
            time.min,
            tzinfo=timezone.utc,
        )
        query = query.where(Payment.paid_at < end)

    rows = db.execute(
        query.group_by(Payment.payment_method)
    ).all()

    return {
        "total_amount": sum(
            (row.total or Decimal("0.00") for row in rows),
            Decimal("0.00"),
        ),
        "total_count": sum(row.count for row in rows),
        "by_method": [
            {
                "payment_method": row.payment_method,
                "total_amount": row.total or Decimal("0.00"),
                "count": row.count,
            }
            for row in rows
        ],
    }