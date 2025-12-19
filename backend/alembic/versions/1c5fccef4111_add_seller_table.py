"""add seller table

Revision ID: 1c5fccef4111
Revises: 0f402359173d
Create Date: 2025-12-18 14:44:04.310406

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1c5fccef4111'
down_revision: Union[str, None] = '0f402359173d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create sellers
    op.create_table(
        'sellers',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('owner_id', sa.Integer(), sa.ForeignKey('user.id'), nullable=False),
        sa.Column('store_name', sa.String(), nullable=False, unique=True),
        sa.Column('store_description', sa.String(), nullable=True),
        sa.Column('store_category', sa.String(), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('false'))
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("sellers")
