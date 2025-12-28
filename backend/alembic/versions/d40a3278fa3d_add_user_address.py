"""add user address

Revision ID: d40a3278fa3d
Revises: 8b63e09ce553
Create Date: 2025-12-22 13:03:15.524812

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd40a3278fa3d'
down_revision: Union[str, None] = '8b63e09ce553'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "user_addresses",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('user.id'), nullable=False),
        sa.Column('label', sa.String(), nullable=True),
        sa.Column('recipient_name', sa.String(), nullable=False),
        sa.Column('phone', sa.Integer(), nullable=False),
        sa.Column('address_line1', sa.String(), nullable=False),
        sa.Column('address_line2', sa.String(), nullable=True),
        sa.Column('city', sa.String(), nullable=False),
        sa.Column('province', sa.String(), nullable=False),
        sa.Column('postal_code', sa.Integer(), nullable=False),
        sa.Column('country', sa.String(), server_default="PH"),
        sa.Column('is_default', sa.Boolean(), server_default=sa.false(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("user_addresses")
