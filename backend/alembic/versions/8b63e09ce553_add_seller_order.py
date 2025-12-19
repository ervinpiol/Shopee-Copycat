"""add seller order

Revision ID: 8b63e09ce553
Revises: 3e09ffdb035c
Create Date: 2025-12-19 14:00:47.296588

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8b63e09ce553'
down_revision: Union[str, None] = '3e09ffdb035c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "seller_orders",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("owner_id", sa.Integer, sa.ForeignKey("user.id"), nullable=False),
        sa.Column("owner_name", sa.String, nullable=False),
        sa.Column("total_price", sa.Float, nullable=False, server_default=sa.text("0.0")),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum(
                "pending",
                "processing",
                "shipped",
                "delivered",
                "cancelled",
                name="seller_order_status_enum",
            ),
            nullable=False,
            server_default="pending",
        ),
    )


def downgrade() -> None:
    op.drop_table("seller_orders")