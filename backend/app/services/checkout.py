import uuid
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.business import Branch
from app.models.coupon import Coupon, coupon_services
from app.models.customer import Customer
from app.models.sale import Sale, SaleItem
from app.models.service import Service
from app.schemas.checkout import CheckoutCreate


CENT = Decimal("0.01")


def _money(value: Decimal) -> Decimal:
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


def create_checkout(
    db: Session,
    business_id: uuid.UUID,
    payload: CheckoutCreate,
) -> Sale:
    now = datetime.now(timezone.utc)

    try:
        customer = None
        if payload.customer_id is not None:
            customer = db.scalar(
                select(Customer).where(
                    Customer.id == payload.customer_id,
                    Customer.business_id == business_id,
                )
            )
            if customer is None:
                raise ValueError("Customer not found in this business.")

        branch = None
        if payload.branch_id is not None:
            branch = db.scalar(
                select(Branch).where(
                    Branch.id == payload.branch_id,
                    Branch.business_id == business_id,
                    Branch.is_active.is_(True),
                )
            )
            if branch is None:
                raise ValueError("Active branch not found in this business.")

        items = []
        subtotal = Decimal("0.00")

        for requested_item in payload.items:
            service = db.scalar(
                select(Service).where(
                    Service.id == requested_item.service_id,
                    Service.business_id == business_id,
                    Service.is_active.is_(True),
                )
            )
            if service is None:
                raise ValueError(
                    "One or more services are inactive or not in this business."
                )

            unit_price = _money(Decimal(str(service.price)))
            line_total = _money(unit_price * requested_item.quantity)
            subtotal += line_total

            items.append(
                {
                    "service_id": service.id,
                    "service_name": service.name,
                    "quantity": requested_item.quantity,
                    "unit_price": unit_price,
                    "line_total": line_total,
                }
            )

        subtotal = _money(subtotal)
        discount = Decimal("0.00")
        coupon = None

        if payload.coupon_code:
            coupon = db.scalar(
                select(Coupon)
                .where(
                    Coupon.business_id == business_id,
                    Coupon.code == payload.coupon_code,
                )
                .with_for_update()
            )

            if coupon is None or not coupon.is_active:
                raise ValueError("Coupon is invalid or inactive.")

            if coupon.starts_at is not None:
                starts_at = coupon.starts_at
                if starts_at.tzinfo is None:
                    starts_at = starts_at.replace(tzinfo=timezone.utc)
                if now < starts_at:
                    raise ValueError("Coupon is not yet valid.")

            if coupon.expires_at is not None:
                expires_at = coupon.expires_at
                if expires_at.tzinfo is None:
                    expires_at = expires_at.replace(tzinfo=timezone.utc)
                if now > expires_at:
                    raise ValueError("Coupon has expired.")

            if (
                coupon.usage_limit is not None
                and coupon.usage_count >= coupon.usage_limit
            ):
                raise ValueError("Coupon usage limit has been reached.")

            if subtotal < Decimal(str(coupon.minimum_spend)):
                raise ValueError("Sale does not meet the coupon minimum spend.")

            eligible_service_ids = set(
                db.scalars(
                    select(coupon_services.c.service_id).where(
                        coupon_services.c.coupon_id == coupon.id
                    )
                ).all()
            )

            if eligible_service_ids:
                eligible_subtotal = sum(
                    (
                        item["line_total"]
                        for item in items
                        if item["service_id"] in eligible_service_ids
                    ),
                    Decimal("0.00"),
                )
                if eligible_subtotal <= 0:
                    raise ValueError(
                        "Coupon does not apply to the selected services."
                    )
            else:
                eligible_subtotal = subtotal

            if coupon.discount_type == "percentage":
                discount = _money(
                    eligible_subtotal
                    * Decimal(str(coupon.discount_value))
                    / Decimal("100")
                )
            elif coupon.discount_type == "fixed":
                discount = min(
                    _money(Decimal(str(coupon.discount_value))),
                    eligible_subtotal,
                )
            else:
                raise ValueError("Unsupported coupon discount type.")

            discount = min(discount, subtotal)

        total = _money(max(Decimal("0.00"), subtotal - discount))

        sale = Sale(
            business_id=business_id,
            customer_id=customer.id if customer else None,
            branch_id=branch.id if branch else None,
            coupon_id=coupon.id if coupon else None,
            coupon_code=coupon.code if coupon else None,
            subtotal=subtotal,
            discount_amount=discount,
            total_amount=total,
            status="paid" if total == Decimal("0.00") else "pending",
            notes=payload.notes,
        )

        db.add(sale)
        db.flush()

        for item_data in items:
            db.add(SaleItem(sale_id=sale.id, **item_data))

        if coupon is not None:
            coupon.usage_count += 1

        db.commit()
        db.refresh(sale)
        return sale

    except Exception:
        db.rollback()
        raise


def get_sale(
    db: Session,
    business_id: uuid.UUID,
    sale_id: uuid.UUID,
) -> Sale | None:
    return db.scalar(
        select(Sale).where(
            Sale.id == sale_id,
            Sale.business_id == business_id,
        )
    )
