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
    coupon = get_coupon(db, business_id, coupon_id)

    if coupon is None:
        return None

    for field, value in updates.items():
        if field == "code" and value is not None:
            value = value.strip().upper()
        setattr(coupon, field, value)

    db.commit()
    db.refresh(coupon)
    return coupon


def delete_coupon(db: Session, business_id, coupon_id):
    coupon = get_coupon(db, business_id, coupon_id)

    if coupon is None:
        return False

    db.delete(coupon)
    db.commit()
    return True
