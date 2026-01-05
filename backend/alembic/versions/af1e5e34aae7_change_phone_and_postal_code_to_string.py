"""change phone and postal code to string

Revision ID: af1e5e34aae7
Revises: 875f0ec2c531
Create Date: 2026-01-05 11:59:17.505786

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'af1e5e34aae7'
down_revision: Union[str, None] = '875f0ec2c531'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: change phone and postal_code columns to String."""
    with op.batch_alter_table("user_addresses") as batch_op:
        batch_op.alter_column(
            "phone",
            existing_type=sa.Integer(),
            type_=sa.String(),
            existing_nullable=False,
        )
        batch_op.alter_column(
            "postal_code",
            existing_type=sa.Integer(),
            type_=sa.String(),
            existing_nullable=False,
        )

    with op.batch_alter_table("sellers") as batch_op:
        batch_op.alter_column(
            "postal_code",
            existing_type=sa.Integer(),
            type_=sa.String(),
            existing_nullable=False,
        )


def downgrade() -> None:
    """Downgrade schema: revert phone and postal_code columns to Integer."""
    with op.batch_alter_table("user_addresses") as batch_op:
        batch_op.alter_column(
            "phone",
            existing_type=sa.String(),
            type_=sa.Integer(),
            existing_nullable=False,
        )
        batch_op.alter_column(
            "postal_code",
            existing_type=sa.String(),
            type_=sa.Integer(),
            existing_nullable=False,
        )

    with op.batch_alter_table("sellers") as batch_op:
        batch_op.alter_column(
            "postal_code",
            existing_type=sa.String(),
            type_=sa.Integer(),
            existing_nullable=False,
        )
