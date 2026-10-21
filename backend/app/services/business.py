
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.business import Branch, Business
from app.schemas.business import BusinessCreate, BranchCreate, BranchUpdate


def create_business(
    db: Session,
    data: BusinessCreate,
) -> Business:
    business = Business(
        name=data.name,
        email=data.email,
        phone=data.phone,
    )
    db.add(business)
    db.commit()
    db.refresh(business)
    return business


def get_business(
    db: Session,
    business_id: uuid.UUID,
) -> Business | None:
    return db.get(Business, business_id)


def list_businesses(db: Session) -> list[Business]:
    statement = select(Business).order_by(Business.name)
    return list(db.scalars(statement).all())


def create_branch(
    db: Session,
    business_id: uuid.UUID,
    data: BranchCreate,
) -> Branch | None:
    business = db.get(Business, business_id)

    if business is None or not business.is_active:
        return None

    branch = Branch(
        business_id=business.id,
        name=data.name,
        address=data.address,
    )
    db.add(branch)
    db.commit()
    db.refresh(branch)
    return branch


def list_branches(
    db: Session,
    business_id: uuid.UUID,
) -> list[Branch] | None:
    business = db.get(Business, business_id)

    if business is None:
        return None

    statement = (
        select(Branch)
        .where(Branch.business_id == business_id)
        .order_by(Branch.name)
    )
    return list(db.scalars(statement).all())

def update_branch(
    db: Session,
    business_id: uuid.UUID,
    branch_id: uuid.UUID,
    data: BranchUpdate,
) -> Branch | None:
    statement = select(Branch).where(
        Branch.id == branch_id,
        Branch.business_id == business_id,
    )
    branch = db.scalars(statement).first()

    if branch is None:
        return None

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(branch, field, value)

    db.commit()
    db.refresh(branch)
    return branch
