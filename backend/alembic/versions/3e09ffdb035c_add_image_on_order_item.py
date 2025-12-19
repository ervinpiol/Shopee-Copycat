"""add image on order item

Revision ID: 3e09ffdb035c
Revises: aa58d23e8350
Create Date: 2025-12-19 12:09:15.824096

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3e09ffdb035c'
down_revision: Union[str, None] = 'aa58d23e8350'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("order_item", sa.Column("image", sa.String(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("order_item", "image")
