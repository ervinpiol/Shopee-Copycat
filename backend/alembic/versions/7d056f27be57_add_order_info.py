"""add order info

Revision ID: 7d056f27be57
Revises: 35b58fc88ef0
Create Date: 2025-12-16 11:56:18.835174

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '7d056f27be57'
down_revision: Union[str, None] = '35b58fc88ef0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "orders",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("owner_id", sa.Integer, sa.ForeignKey("user.id"), nullable=False),
        sa.Column("owner_name", sa.String, nullable=False),
        sa.Column("status", sa.String, nullable=False, default="pending"),
        sa.Column("total_price", sa.Float, nullable=False, default=0.0),
        sa.Column("order_date", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "order_item",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("order_id", sa.Integer, sa.ForeignKey("orders.id"), nullable=False),
        sa.Column("product_id", sa.Integer, sa.ForeignKey("product.id"), nullable=False),
        sa.Column("quantity", sa.Integer, nullable=False),
        sa.Column("total_price", sa.Float, nullable=False),
        sa.Column("product_name", sa.String, nullable=False),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("order_item")
    op.drop_table("orders")