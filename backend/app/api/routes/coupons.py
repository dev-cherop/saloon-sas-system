import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.authorization import require_permission
from app.db import get_db
from app.schemas.coupon import CouponCreate, CouponRead, CouponUpdate
from app.services.coupon import (
    create_coupon,
    delete_coupon,
    get_coupon,
    list_coupons,
    update_coupon,
)

router = APIRouter(
    prefix="/api/v1/businesses/{business_id}/coupons",
    tags=["Coupons"],
)


@router.post("", response_model=CouponRead, status_code=status.HTTP_201_CREATED)
def create_coupon_endpoint(
    business_id: uuid.UUID,
    payload: CouponCreate,
    db: Session = Depends(get_db),
    _membership=Depends(require_permission("coupons:create")),
):
    return create_coupon(db, business_id, **payload.model_dump())


@router.get("", response_model=list[CouponRead])
def list_coupons_endpoint(
    business_id: uuid.UUID,
    include_inactive: bool = Query(default=False),
    db: Session = Depends(get_db),
    _membership=Depends(require_permission("coupons:read")),
):
    return list_coupons(db, business_id, include_inactive=include_inactive)


@router.get("/{coupon_id}", response_model=CouponRead)
def get_coupon_endpoint(
    business_id: uuid.UUID,
    coupon_id: uuid.UUID,
    db: Session = Depends(get_db),
    _membership=Depends(require_permission("coupons:read")),
):
    coupon = get_coupon(db, business_id, coupon_id)
    if coupon is None:
        raise HTTPException(status_code=404, detail="Coupon not found")
    return coupon


@router.patch("/{coupon_id}", response_model=CouponRead)
def update_coupon_endpoint(
    business_id: uuid.UUID,
    coupon_id: uuid.UUID,
    payload: CouponUpdate,
    db: Session = Depends(get_db),
    _membership=Depends(require_permission("coupons:update")),
):
    coupon = update_coupon(
        db,
        business_id,
        coupon_id,
        **payload.model_dump(exclude_unset=True),
    )
    if coupon is None:
        raise HTTPException(status_code=404, detail="Coupon not found")
    return coupon


@router.delete("/{coupon_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_coupon_endpoint(
    business_id: uuid.UUID,
    coupon_id: uuid.UUID,
    db: Session = Depends(get_db),
    _membership=Depends(require_permission("coupons:delete")),
):
    if not delete_coupon(db, business_id, coupon_id):
        raise HTTPException(status_code=404, detail="Coupon not found")
    return None
