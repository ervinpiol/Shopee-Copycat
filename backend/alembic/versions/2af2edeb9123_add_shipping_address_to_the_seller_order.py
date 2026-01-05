"""add shipping address to the seller order

Revision ID: 2af2edeb9123
Revises: af1e5e34aae7
Create Date: 2026-01-05 12:19:46.831745

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2af2edeb9123'
down_revision: Union[str, None] = 'af1e5e34aae7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: link seller_orders to order_addresses."""
    with op.batch_alter_table("order_addresses") as batch_op:
        batch_op.add_column(
            sa.Column(
                "seller_order_id",
                sa.Integer(),
                sa.ForeignKey("seller_orders.id", ondelete="CASCADE"),
                nullable=True,
            )
        )
        batch_op.create_unique_constraint(
            "uq_order_addresses_seller_order_id",
            ["seller_order_id"],
        )


def downgrade() -> None:
    """Downgrade schema: unlink seller_orders from order_addresses."""
    with op.batch_alter_table("order_addresses") as batch_op:
        batch_op.drop_constraint(
            "uq_order_addresses_seller_order_id",
            type_="unique",
        )
        batch_op.drop_column("seller_order_id")
