from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.coupon import Coupon


def create_coupon(db: Session, business_id, **data):
    data["code"] = data["code"].strip().upper()

    coupon = Coupon(business_id=business_id, **data)
    db.add(coupon)
    db.commit()
    db.refresh(coupon)
    return coupon


def list_coupons(db: Session, business_id, include_inactive: bool = False):
    query = db.query(Coupon).filter(Coupon.business_id == business_id)

    if not include_inactive:
        query = query.filter(Coupon.is_active.is_(True))

    return query.order_by(Coupon.created_at.desc()).all()


def get_coupon(db: Session, business_id, coupon_id):
    return (
        db.query(Coupon)
        .filter(
            Coupon.business_id == business_id,
            Coupon.id == coupon_id,
        )
        .first()
    )


def update_coupon(db: Session, business_id, coupon_id, **updates):
    from sqlalchemy import select

    from app.models.coupon import coupon_services
    from app.models.service import Service

    coupon = get_coupon(db, business_id, coupon_id)

    if coupon is None:
        return None

    service_ids = updates.pop("service_ids", None)

    discount_type = updates.get("discount_type", coupon.discount_type)
    discount_value = updates.get("discount_value", coupon.discount_value)
    starts_at = updates.get("starts_at", coupon.starts_at)
    expires_at = updates.get("expires_at", coupon.expires_at)

    if discount_type == "percentage" and discount_value > 100:
        raise HTTPException(
            status_code=422,
            detail="Percentage discount cannot exceed 100",
        )

    if starts_at and expires_at and expires_at <= starts_at:
        raise HTTPException(
            status_code=422,
            detail="Expiry must be later than the start date",
        )

    if service_ids is not None:
        service_ids = set(service_ids)

        if service_ids:
            valid_service_ids = set(
                db.scalars(
                    select(Service.id).where(
                        Service.business_id == business_id,
                        Service.id.in_(service_ids),
                    )
                ).all()
            )

            if valid_service_ids != service_ids:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "One or more services were not found "
                        "in this business."
                    ),
                )

    try:
        for field, value in updates.items():
            if field == "code" and value is not None:
                value = value.strip().upper()
            setattr(coupon, field, value)

        if service_ids is not None:
            db.execute(
                coupon_services.delete().where(
                    coupon_services.c.coupon_id == coupon.id
                )
            )

            for service_id in service_ids:
                db.execute(
                    coupon_services.insert().values(
                        coupon_id=coupon.id,
                        service_id=service_id,
                    )
                )

        db.commit()
        db.refresh(coupon)
        return coupon
    except Exception:
        db.rollback()
        raise


def delete_coupon(db: Session, business_id, coupon_id):
    coupon = get_coupon(db, business_id, coupon_id)

    if coupon is None:
        return False

    db.delete(coupon)
    db.commit()
    return True


def create_coupon(db: Session, business_id, **data):
    from sqlalchemy import select

    from app.models.coupon import coupon_services
    from app.models.service import Service

    data["code"] = data["code"].strip().upper()
    service_ids = set(data.pop("service_ids", []))

    if service_ids:
        valid_service_ids = set(
            db.scalars(
                select(Service.id).where(
                    Service.business_id == business_id,
                    Service.id.in_(service_ids),
                )
            ).all()
        )

        if valid_service_ids != service_ids:
            raise HTTPException(
                status_code=400,
                detail="One or more services were not found in this business.",
            )

    coupon = Coupon(business_id=business_id, **data)
    db.add(coupon)

    try:
        db.flush()

        for service_id in service_ids:
            db.execute(
                coupon_services.insert().values(
                    coupon_id=coupon.id,
                    service_id=service_id,
                )
            )

        db.commit()
        db.refresh(coupon)
        return coupon
    except Exception:
        db.rollback()
        raise