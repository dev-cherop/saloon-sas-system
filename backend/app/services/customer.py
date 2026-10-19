import uuid

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.models.business import Business
from app.schemas.customer import CustomerCreate, CustomerUpdate


def create_customer(
    db: Session,
    business_id: uuid.UUID,
    data: CustomerCreate,
) -> Customer | None:

    business = db.get(Business, business_id)

    if business is None or not business.is_active:
        return None

    customer = Customer(
        business_id=business_id,
        first_name=data.first_name,
        last_name=data.last_name,
        phone=data.phone,
        email=data.email,
        preferences=data.preferences,
    )

    db.add(customer)
    db.commit()
    db.refresh(customer)

    return customer


def get_customer(
    db: Session,
    business_id: uuid.UUID,
    customer_id: uuid.UUID,
) -> Customer | None:

    statement = (
        select(Customer)
        .where(
            Customer.id == customer_id,
            Customer.business_id == business_id,
        )
    )

    return db.scalar(statement)


def list_customers(
    db: Session,
    business_id: uuid.UUID,
    search: str | None = None,
) -> list[Customer]:

    statement = (
        select(Customer)
        .where(Customer.business_id == business_id)
        .order_by(Customer.first_name, Customer.last_name)
    )

    if search:
        search_pattern = f"%{search}%"

        statement = statement.where(
            or_(
                Customer.first_name.ilike(search_pattern),
                Customer.last_name.ilike(search_pattern),
                Customer.phone.ilike(search_pattern),
                Customer.email.ilike(search_pattern),
            )
        )

    return list(db.scalars(statement).all())


def update_customer(
    db: Session,
    business_id: uuid.UUID,
    customer_id: uuid.UUID,
    data: CustomerUpdate,
) -> Customer | None:

    customer = get_customer(
        db,
        business_id,
        customer_id,
    )

    if customer is None:
        return None

    update_data = data.model_dump(
        exclude_unset=True,
    )

    for field, value in update_data.items():
        setattr(customer, field, value)

    db.commit()
    db.refresh(customer)

    return customer



def delete_customer(
    db: Session,
    business_id: uuid.UUID,
    customer_id: uuid.UUID,
) -> bool:
    customer = get_customer(db, business_id, customer_id)

    if customer is None:
        return False

    db.delete(customer)
    db.commit()
    return True