import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.authorization import require_permission
from app.db import get_db

from sqlalchemy import select

from app.core.auth import get_current_user
from app.models.users import User
from app.db import get_db
from app.models.business import Business
from app.models.membership import BusinessMembership

   
from app.schemas.business import (
    BusinessRead,
    BranchCreate,
    BranchRead,
    BranchUpdate,
)
from app.services.business import (
    get_business,
    create_branch,
    list_branches,
    update_branch,
)

router = APIRouter(
    prefix="/api/v1/businesses",
    tags=["Businesses"],
)


@router.get(
    "",
    response_model=list[BusinessRead],
)
def list_businesses_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    statement = (
        select(Business)
        .join(
            BusinessMembership,
            BusinessMembership.business_id == Business.id,
        )
        .where(
            BusinessMembership.user_id == current_user.id,
            Business.is_active.is_(True),
        )
        .order_by(Business.name)
    )

    return list(db.scalars(statement).all())

@router.get(
    "/{business_id}",
    response_model=BusinessRead,
)
def get_business_endpoint(
    business_id: uuid.UUID,
    db: Session = Depends(get_db),
    _membership=Depends(
        require_permission("settings:manage")
    ),
):
    business = get_business(db, business_id)

    if business is None:
        raise HTTPException(
            status_code=404,
            detail="Business not found",
        )

    return business


@router.post(
    "/{business_id}/branches",
    response_model=BranchRead,
    status_code=status.HTTP_201_CREATED,
)
def create_branch_endpoint(
    business_id: uuid.UUID,
    payload: BranchCreate,
    db: Session = Depends(get_db),
    _membership=Depends(
        require_permission("settings:manage")
    ),
):
    branch = create_branch(
        db,
        business_id,
        payload,
    )

    if branch is None:
        raise HTTPException(
            status_code=404,
            detail="Business not found or inactive",
        )

    return branch


@router.patch(
    "/{business_id}/branches/{branch_id}",
    response_model=BranchRead,
)
def update_branch_endpoint(
    business_id: uuid.UUID,
    branch_id: uuid.UUID,
    payload: BranchUpdate,
    db: Session = Depends(get_db),
    _membership=Depends(require_permission("settings:manage")),
):
    branch = update_branch(db, business_id, branch_id, payload)

    if branch is None:
        raise HTTPException(
            status_code=404,
            detail="Branch not found",
        )

    return branch


@router.get(
    "/{business_id}/branches",
    response_model=list[BranchRead],
)
def list_branches_endpoint(
    business_id: uuid.UUID,
    db: Session = Depends(get_db),
    _membership=Depends(
        require_permission("settings:manage")
    ),
):
    branches = list_branches(
        db,
        business_id,
    )

    if branches is None:
        raise HTTPException(
            status_code=404,
            detail="Business not found",
        )

    return branches