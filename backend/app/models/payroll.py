import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Payroll(Base):
    __tablename__ = "payroll_records"

    __table_args__ = (
       UniqueConstraint(
            "business_id",
            "worker_id",
            "period_start",
            "period_end",
            name="uq_payroll_worker_period",
        ),
        CheckConstraint(
            "period_end >= period_start",
            name="ck_payroll_valid_period",
        ),
        CheckConstraint(
            "base_pay >= 0 AND commission >= 0 AND bonus >= 0 "
            "AND deductions >= 0",
            name="ck_payroll_nonnegative_amounts",
        ),
        CheckConstraint(
            "status IN ('draft', 'approved', 'paid')",
            name="ck_payroll_status",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    business_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("businesses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    worker_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("workers.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    period_start: Mapped[date] = mapped_column(Date, nullable=False)
    period_end: Mapped[date] = mapped_column(Date, nullable=False)

    base_pay: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, default=0
    )
    commission: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, default=0
    )
    bonus: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, default=0
    )
    deductions: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, default=0
    )
    net_pay: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="draft", index=True
    )
    payment_method: Mapped[str | None] = mapped_column(
        String(30), nullable=True
    )
    paid_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    business = relationship("Business")
    worker = relationship("Worker")