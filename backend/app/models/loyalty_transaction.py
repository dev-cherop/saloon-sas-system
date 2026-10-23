import uuid

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db import Base


class LoyaltyTransaction(Base):
    __tablename__ = "loyalty_transactions"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    business_id = Column(
        UUID(as_uuid=True),
        ForeignKey("businesses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    customer_id = Column(
        UUID(as_uuid=True),
        ForeignKey("customers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    visit_id = Column(
        UUID(as_uuid=True),
        ForeignKey("customer_visits.id", ondelete="SET NULL"),
        nullable=True,
        unique=True,
        index=True,
    )

    sale_id = Column(
        UUID(as_uuid=True),
        ForeignKey("sales.id", ondelete="SET NULL"),
        nullable=True,
        unique=True,
        index=True,
    )

    # Positive points are earned; negative points are redeemed.
    points_change = Column(Integer, nullable=False)

    transaction_type = Column(String(20), nullable=False)

    # Monetary discount value, when applicable.
    monetary_value = Column(
        Numeric(12, 2),
        nullable=False,
        default=0,
    )

    description = Column(Text, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    customer = relationship("Customer")