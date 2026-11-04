import uuid
from datetime import datetime, timezone
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.payroll import Payroll
from app.models.worker import Worker
from app.schemas.payroll import PayrollCreate, PayrollUpdate


ZERO = Decimal("0.00")


def calculate_net_pay(
    base_pay: Decimal,
    commission: Decimal,
    bonus: Decimal,
    deductions: Decimal,
) -> Decimal:
    return base_pay + commission + bonus - deductions


def get_worker(
    db: Session,
    business_id: uuid.UUID,
    worker_id: uuid.UUID,
) -> Worker:
    worker = db.scalar(
        select(Worker).where(
            Worker.id == worker_id,
            Worker.business_id == business_id,
        )
    )

    if worker is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Worker not found in this business",
        )

    return worker


def get_payroll(
    db: Session,
    business_id: uuid.UUID,
    payroll_id: uuid.UUID,
) -> Payroll:
    payroll = db.scalar(
        select(Payroll)
        .options(joinedload(Payroll.worker))
        .where(
            Payroll.id == payroll_id,
            Payroll.business_id == business_id,
        )
    )

    if payroll is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payroll record not found",
        )

    return payroll


def list_payroll(
    db: Session,
    business_id: uuid.UUID,
    worker_id: uuid.UUID | None = None,
    payroll_status: str | None = None,
) -> list[Payroll]:
    query = (
        select(Payroll)
        .options(joinedload(Payroll.worker))
        .where(Payroll.business_id == business_id)
        .order_by(Payroll.period_start.desc(), Payroll.created_at.desc())
    )

    if worker_id is not None:
        query = query.where(Payroll.worker_id == worker_id)

    if payroll_status is not None:
        query = query.where(Payroll.status == payroll_status)

    return list(db.scalars(query).unique().all())


def create_payroll(
    db: Session,
    business_id: uuid.UUID,
    data: PayrollCreate,
) -> Payroll:
    get_worker(db, business_id, data.worker_id)

    existing = db.scalar(
        select(Payroll.id).where(
            Payroll.business_id == business_id,
            Payroll.worker_id == data.worker_id,
            Payroll.period_start == data.period_start,
            Payroll.period_end == data.period_end,
        )
    )

    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Payroll already exists for this worker and pay period",
        )

    base_pay = data.base_pay
    commission = data.commission
    bonus = data.bonus
    deductions = data.deductions

    payroll = Payroll(
        business_id=business_id,
        worker_id=data.worker_id,
        period_start=data.period_start,
        period_end=data.period_end,
        base_pay=base_pay,
        commission=commission,
        bonus=bonus,
        deductions=deductions,
        net_pay=calculate_net_pay(
            base_pay, commission, bonus, deductions
        ),
        status="draft",
        notes=data.notes,
    )

    db.add(payroll)
    db.commit()
    db.refresh(payroll)

    return get_payroll(db, business_id, payroll.id)


def update_payroll(
    db: Session,
    business_id: uuid.UUID,
    payroll_id: uuid.UUID,
    data: PayrollUpdate,
) -> Payroll:
    payroll = get_payroll(db, business_id, payroll_id)

    if payroll.status != "draft":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only draft payroll records can be edited",
        )

    changes = data.model_dump(exclude_unset=True)

    for field, value in changes.items():
        setattr(payroll, field, value)

    period_start = payroll.period_start
    period_end = payroll.period_end

    if period_end < period_start:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Pay period end cannot precede its start",
        )

    duplicate = db.scalar(
        select(Payroll.id).where(
            Payroll.business_id == business_id,
            Payroll.worker_id == payroll.worker_id,
            Payroll.period_start == period_start,
            Payroll.period_end == period_end,
            Payroll.id != payroll.id,
        )
    )

    if duplicate is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Payroll already exists for this worker and pay period",
        )

    payroll.net_pay = calculate_net_pay(
        payroll.base_pay,
        payroll.commission,
        payroll.bonus,
        payroll.deductions,
    )

    db.commit()
    db.refresh(payroll)

    return get_payroll(db, business_id, payroll.id)


def update_payroll_status(
    db: Session,
    business_id: uuid.UUID,
    payroll_id: uuid.UUID,
    new_status: str,
    payment_method: str | None = None,
) -> Payroll:
    payroll = get_payroll(db, business_id, payroll_id)

    if new_status == "approved":
        if payroll.status != "draft":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Only draft payroll records can be approved",
            )

    elif new_status == "paid":
        if payroll.status != "approved":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Only approved payroll records can be paid",
            )

        if not payment_method:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Payment method is required when marking payroll as paid",
            )

        payroll.payment_method = payment_method
        payroll.paid_at = datetime.now(timezone.utc)

    else:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid payroll status transition",
        )

    payroll.status = new_status
    db.commit()
    db.refresh(payroll)

    return get_payroll(db, business_id, payroll.id)