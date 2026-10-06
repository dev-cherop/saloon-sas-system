
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.business import (
    BusinessCreate,
    BusinessRead,
    BranchCreate,
    BranchRead,
)
from app.services.business import (
    create_business,
    get_business,
    list_businesses,
    create_branch,
    list_branches,
)

router = APIRouter(
    prefix="/api/v1/businesses",
    tags=["Businesses"],
)


@router.post(
    "",
    response_model=BusinessRead,
    status_code=status.HTTP_201_CREATED,
)
def create_business_endpoint(
    payload: BusinessCreate,
    db: Session = Depends(get_db),
):
    return create_business(db, payload)


@router.get("", response_model=list[BusinessRead])
def list_businesses_endpoint(
    db: Session = Depends(get_db),
):
    return list_businesses(db)


@router.get("/{business_id}", response_model=BusinessRead)
def get_business_endpoint(
    business_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    business = get_business(db, business_id)

    if business is None:
        raise HTTPException(status_code=404, detail="Business not found")

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
):
    branch = create_branch(db, business_id, payload)

    if branch is None:
        raise HTTPException(
            status_code=404,
            detail="Business not found or inactive",
        )

    return branch


@router.get(
    "/{business_id}/branches",
    response_model=list[BranchRead],
)
def list_branches_endpoint(
    business_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    branches = list_branches(db, business_id)

    if branches is None:
        raise HTTPException(status_code=404, detail="Business not found")

    return branches