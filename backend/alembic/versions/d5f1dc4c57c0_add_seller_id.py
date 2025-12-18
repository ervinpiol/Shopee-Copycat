"""add seller id

Revision ID: d5f1dc4c57c0
Revises: 1c5fccef4111
Create Date: 2025-12-18 14:48:11.802210

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd5f1dc4c57c0'
down_revision: Union[str, None] = '1c5fccef4111'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ---- product ----
    op.add_column(
        "product",
        sa.Column("seller_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "product_seller_id_fkey",
        "product",
        "sellers",
        ["seller_id"],
        ["id"],
        ondelete="CASCADE",
    )

    # ---- order_item ----
    op.add_column(
        "order_item",
        sa.Column("seller_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "order_item_seller_id_fkey",
        "order_item",
        "sellers",
        ["seller_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    # ---- order_item ----
    op.drop_constraint(
        "order_item_seller_id_fkey",
        "order_item",
        type_="foreignkey",
    )
    op.drop_column("order_item", "seller_id")

    # ---- product ----
    op.drop_constraint(
        "product_seller_id_fkey",
        "product",
        type_="foreignkey",
    )
    op.drop_column("product", "seller_id")