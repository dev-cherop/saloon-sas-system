import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Table,
    Text,
    UniqueConstraint,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


coupon_services = Table(
    "coupon_services",
    Base.metadata,
    Column("coupon_id", Uuid(as_uuid=True),
           ForeignKey("coupons.id", ondelete="CASCADE"), primary_key=True),
    Column("service_id", Uuid(as_uuid=True),
           ForeignKey("services.id", ondelete="CASCADE"), primary_key=True),
)


class Coupon(Base):
    __tablename__ = "coupons"
    __table_args__ = (
        UniqueConstraint("business_id", "code", name="uq_coupon_business_code"),
        CheckConstraint(
            "discount_type IN ('percentage', 'fixed')",
            name="ck_coupon_discount_type",
        ),
        CheckConstraint("discount_value > 0", name="ck_coupon_discount_positive"),
        CheckConstraint("minimum_spend >= 0", name="ck_coupon_minimum_spend"),
        CheckConstraint("usage_count >= 0", name="ck_coupon_usage_count"),
        CheckConstraint(
            "usage_limit IS NULL OR usage_limit > 0",
            name="ck_coupon_usage_limit",
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
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    discount_type: Mapped[str] = mapped_column(String(20), nullable=False)
    discount_value: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    minimum_spend: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, default=0
    )
    starts_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    usage_limit: Mapped[int | None] = mapped_column(Integer, nullable=True)
    usage_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
