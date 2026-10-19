from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.service import Service


def create_service(
    db: Session,
    business_id,
    name: str,
    price: Decimal,
    duration_minutes: int = 30,
    description: str | None = None,
) -> Service:
    service = Service(
        business_id=business_id,
        name=name.strip(),
        description=description,
        price=price,
        duration_minutes=duration_minutes,
    )
    db.add(service)
    db.commit()
    db.refresh(service)
    return service


def list_services(db: Session, business_id, include_inactive: bool = False):
    query = db.query(Service).filter(Service.business_id == business_id)

    if not include_inactive:
        query = query.filter(Service.is_active.is_(True))

    return query.order_by(Service.name.asc()).all()


def get_service(db: Session, business_id, service_id):
    return (
        db.query(Service)
        .filter(
            Service.business_id == business_id,
            Service.id == service_id,
        )
        .first()
    )


def update_service(db: Session, business_id, service_id, **updates):
    service = get_service(db, business_id, service_id)

    if service is None:
        return None

    for field in ("name", "description", "price", "duration_minutes", "is_active"):
        if field in updates and updates[field] is not None:
            value = updates[field]
            if field == "name":
                value = value.strip()
            setattr(service, field, value)

    db.commit()
    db.refresh(service)
    return service


def delete_service(db: Session, business_id, service_id):
    service = get_service(db, business_id, service_id)

    if service is None:
        return False

    db.delete(service)
    db.commit()
    return True