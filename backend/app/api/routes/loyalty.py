
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from sqlalchemy.exc import IntegrityError
from app.services.loyalty import award_points_for_visit

from app.core.authorization import require_permission
from app.db import get_db
from app.schemas.loyalty import (
    LoyaltyBalanceRead,
    LoyaltyRedeem,
    LoyaltyTransactionRead,
)

from app.models.loyalty_settings import LoyaltySettings
from app.schemas.loyalty import (
    LoyaltySettingsRead,
    LoyaltySettingsUpdate,
)

from app.services.loyalty import (
    get_loyalty_balance,
    get_loyalty_history,
    redeem_loyalty_points,
)

router = APIRouter(
    prefix="/api/v1/businesses/{business_id}/loyalty",
    tags=["Loyalty"],
)


@router.get(
    "/customers/{customer_id}",
    response_model=LoyaltyBalanceRead,
)
def get_customer_loyalty(
    business_id: uuid.UUID,
    customer_id: uuid.UUID,
    db: Session = Depends(get_db),
    _membership=Depends(require_permission("loyalty:read")),
):
    try:
        balance = get_loyalty_balance(
            db, business_id, customer_id
        )
        history = get_loyalty_history(
            db, business_id, customer_id
        )

        return {
            "customer_id": customer_id,
            "balance": balance,
            "history": history,
        }
    except ValueError as exc:
        raise HTTPException(
            status_code=404, detail=str(exc)
        ) from exc


@router.post(
    "/customers/{customer_id}/redeem",
    response_model=LoyaltyTransactionRead,
)
def redeem_customer_loyalty(
    business_id: uuid.UUID,
    customer_id: uuid.UUID,
    payload: LoyaltyRedeem,
    db: Session = Depends(get_db),
    _membership=Depends(require_permission("loyalty:redeem")),
):
    try:
        transaction = redeem_loyalty_points(
            db=db,
            business_id=business_id,
            customer_id=customer_id,
            points=payload.points,
            description=payload.description,
        )
        db.commit()
        db.refresh(transaction)
        return transaction

    except ValueError as exc:
        db.rollback()

        message = str(exc)
        status_code = (
            404 if "Customer not found" in message else 400
        )

        raise HTTPException(
            status_code=status_code,
            detail=message,
        ) from exc

    except Exception:
        db.rollback()
        raise


@router.post(
    "/visits/{visit_id}/earn",
    response_model=LoyaltyTransactionRead,
)
def earn_points_for_visit_endpoint(
    business_id: uuid.UUID,
    visit_id: uuid.UUID,
    db: Session = Depends(get_db),
    _membership=Depends(require_permission("loyalty:earn")),
):
    try:
        transaction = award_points_for_visit(
            db=db,
            business_id=business_id,
            visit_id=visit_id,
        )
        db.commit()
        db.refresh(transaction)
        return transaction

    except ValueError as exc:
        db.rollback()
        message = str(exc)
        status_code = (
            404 if "not found" in message.lower() else 400
        )
        raise HTTPException(
            status_code=status_code,
            detail=message,
        ) from exc

    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Points have already been awarded for this visit.",
        ) from exc

    except Exception:
        db.rollback()
        raise


@router.get(
    "/settings",
    response_model=LoyaltySettingsRead,
)
def get_loyalty_settings(
    business_id: uuid.UUID,
    db: Session = Depends(get_db),
    _membership=Depends(require_permission("loyalty:read")),
):
    settings = (
        db.query(LoyaltySettings)
        .filter(LoyaltySettings.business_id == business_id)
        .first()
    )

    if settings is None:
        settings = LoyaltySettings(business_id=business_id)
        db.add(settings)
        db.commit()
        db.refresh(settings)

    return settings


@router.put(
    "/settings",
    response_model=LoyaltySettingsRead,
)
def update_loyalty_settings(
    business_id: uuid.UUID,
    payload: LoyaltySettingsUpdate,
    db: Session = Depends(get_db),
    _membership=Depends(require_permission("loyalty:manage")),
):
    settings = (
        db.query(LoyaltySettings)
        .filter(LoyaltySettings.business_id == business_id)
        .first()
    )

    if settings is None:
        settings = LoyaltySettings(business_id=business_id)
        db.add(settings)

    settings.enabled = payload.enabled
    settings.spend_per_point = payload.spend_per_point
    settings.redemption_value = payload.redemption_value
    settings.minimum_redemption_points = (
        payload.minimum_redemption_points
    )

    db.commit()
    db.refresh(settings)
    return settings
