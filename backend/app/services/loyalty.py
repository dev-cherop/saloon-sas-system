
from decimal import Decimal, InvalidOperation
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.models.loyalty_settings import LoyaltySettings
from app.models.loyalty_transaction import LoyaltyTransaction
from app.models.customer_visit import CustomerVisit

def _get_customer(
    db: Session,
    business_id: UUID,
    customer_id: UUID,
) -> Customer:
    customer = (
        db.query(Customer)
        .filter(
            Customer.id == customer_id,
            Customer.business_id == business_id,
        )
        .with_for_update()
        .first()
    )

    if customer is None:
        raise ValueError("Customer not found in this business.")

    return customer


def _get_settings(
    db: Session,
    business_id: UUID,
) -> LoyaltySettings:
    settings = (
        db.query(LoyaltySettings)
        .filter(LoyaltySettings.business_id == business_id)
        .first()
    )

    if settings is None:
        settings = LoyaltySettings(business_id=business_id)
        db.add(settings)
        db.flush()

    if not settings.enabled:
        raise ValueError("Loyalty is disabled for this business.")

    return settings


def get_loyalty_balance(
    db: Session,
    business_id: UUID,
    customer_id: UUID,
) -> int:
    _get_customer(db, business_id, customer_id)

    balance = (
        db.query(
            func.coalesce(
                func.sum(LoyaltyTransaction.points_change),
                0,
            )
        )
        .filter(
            LoyaltyTransaction.business_id == business_id,
            LoyaltyTransaction.customer_id == customer_id,
        )
        .scalar()
    )

    return int(balance or 0)


def get_loyalty_history(
    db: Session,
    business_id: UUID,
    customer_id: UUID,
) -> list[LoyaltyTransaction]:
    _get_customer(db, business_id, customer_id)

    return (
        db.query(LoyaltyTransaction)
        .filter(
            LoyaltyTransaction.business_id == business_id,
            LoyaltyTransaction.customer_id == customer_id,
        )
        .order_by(LoyaltyTransaction.created_at.desc())
        .all()
    )


def award_loyalty_points(
    db: Session,
    business_id: UUID,
    customer_id: UUID,
    amount_spent: Decimal,
    description: str | None = None,
) -> LoyaltyTransaction | None:
    customer = _get_customer(db, business_id, customer_id)
    settings = _get_settings(db, business_id)

    try:
        amount = Decimal(str(amount_spent))
    except (InvalidOperation, ValueError):
        raise ValueError("Invalid spending amount.")

    if not amount.is_finite() or amount <= 0:
        raise ValueError("Spending amount must be positive.")

    spend_per_point = Decimal(str(settings.spend_per_point))

    if spend_per_point <= 0:
        raise ValueError("Spend per point must be greater than zero.")

    points = int(amount // spend_per_point)

    if points == 0:
        return None

    transaction = LoyaltyTransaction(
        business_id=business_id,
        customer_id=customer.id,
        points_change=points,
        transaction_type="earned",
        monetary_value=Decimal("0.00"),
        description=description or "Points earned from spending",
    )

    db.add(transaction)
    db.flush()

    return transaction


def redeem_loyalty_points(
    db: Session,
    business_id: UUID,
    customer_id: UUID,
    points: int,
    description: str | None = None,
) -> LoyaltyTransaction:
    customer = _get_customer(db, business_id, customer_id)
    settings = _get_settings(db, business_id)

    if isinstance(points, bool) or not isinstance(points, int) or points <= 0:
        raise ValueError("Points to redeem must be a positive integer.")

    if points < settings.minimum_redemption_points:
        raise ValueError(
            f"At least {settings.minimum_redemption_points} "
            "points are required for redemption."
        )

    balance = get_loyalty_balance(
        db,
        business_id,
        customer.id,
    )

    if points > balance:
        raise ValueError("Insufficient loyalty points.")

    redemption_value = Decimal(str(settings.redemption_value))

    if redemption_value <= 0:
        raise ValueError("Redemption value must be greater than zero.")

    discount = Decimal(points) * redemption_value

    transaction = LoyaltyTransaction(
        business_id=business_id,
        customer_id=customer.id,
        points_change=-points,
        transaction_type="redeemed",
        monetary_value=discount,
        description=description or "Loyalty points redeemed",
    )

    db.add(transaction)
    db.flush()

    return transaction


def award_points_for_visit(
    db: Session,
    business_id: UUID,
    visit_id: UUID,
) -> LoyaltyTransaction:
    visit = (
        db.query(CustomerVisit)
        .filter(
            CustomerVisit.id == visit_id,
            CustomerVisit.business_id == business_id,
        )
        .with_for_update()
        .first()
    )

    if visit is None:
        raise ValueError("Visit not found in this business.")

    existing = (
        db.query(LoyaltyTransaction)
        .filter(LoyaltyTransaction.visit_id == visit_id)
        .first()
    )

    if existing is not None:
        raise ValueError("Loyalty points already awarded for this visit.")

    settings = _get_settings(db, business_id)

    amount = Decimal(str(visit.amount))
    spend_per_point = Decimal(str(settings.spend_per_point))

    if spend_per_point <= 0:
        raise ValueError("Spend per point must be greater than zero.")

    points = int(amount // spend_per_point)

    if points <= 0:
        raise ValueError(
            "This visit does not qualify for any loyalty points."
        )

    transaction = LoyaltyTransaction(
        business_id=business_id,
        customer_id=visit.customer_id,
        visit_id=visit.id,
        points_change=points,
        transaction_type="earned",
        monetary_value=Decimal("0.00"),
        description=f"Points earned from {visit.service_name}",
    )

    db.add(transaction)
    db.flush()

    return transaction
