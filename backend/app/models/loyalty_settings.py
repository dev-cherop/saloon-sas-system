from sqlalchemy import Boolean, Column, ForeignKey, Integer, Numeric
from sqlalchemy.orm import relationship

from app.db import Base


class LoyaltySettings(Base):
    __tablename__ = "loyalty_settings"

    id = Column(Integer, primary_key=True, index=True)

    business_id = Column(
        ForeignKey("businesses.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )

    enabled = Column(Boolean, nullable=False, default=True)

    # Amount of money spent to earn one point.
    spend_per_point = Column(
        Numeric(12, 2),
        nullable=False,
        default=1000,
    )

    # Monetary value of one redeemed point.
    redemption_value = Column(
        Numeric(12, 2),
        nullable=False,
        default=1,
    )

    minimum_redemption_points = Column(
        Integer,
        nullable=False,
        default=10,
    )

    business = relationship("Business")