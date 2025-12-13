"""add is_seller to user

Revision ID: 35b58fc88ef0
Revises: f8915d778922
Create Date: 2025-12-12 16:39:39.495376

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '35b58fc88ef0'
down_revision: Union[str, None] = 'f8915d778922'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'user',
        sa.Column("is_seller", sa.Boolean(), server_default="false")
    )


def downgrade() -> None:
    op.drop_column("user", "is_seller")
