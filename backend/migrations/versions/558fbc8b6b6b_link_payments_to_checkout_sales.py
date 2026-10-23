"""link payments to checkout sales

Revision ID: 558fbc8b6b6b
Revises: d76cde4352e3
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "558fbc8b6b6b"
down_revision: Union[str, Sequence[str], None] = "d76cde4352e3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "payments",
        sa.Column("sale_id", sa.Uuid(), nullable=True),
    )
    op.alter_column(
        "payments",
        "visit_id",
        existing_type=sa.Uuid(),
        nullable=True,
    )
    op.create_index(
        "ix_payments_sale_id",
        "payments",
        ["sale_id"],
        unique=False,
    )
    op.create_foreign_key(
        "fk_payments_sale_id_sales",
        "payments",
        "sales",
        ["sale_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_payments_sale_id_sales",
        "payments",
        type_="foreignkey",
    )
    op.drop_index("ix_payments_sale_id", table_name="payments")
    op.alter_column(
        "payments",
        "visit_id",
        existing_type=sa.Uuid(),
        nullable=False,
    )
    op.drop_column("payments", "sale_id")