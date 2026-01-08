"""add seller status remove is_active

Revision ID: 71672cd00656
Revises: 2af2edeb9123
Create Date: 2026-01-08 11:02:53.910580

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '71672cd00656'
down_revision: Union[str, None] = '2af2edeb9123'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "sellers",
        sa.Column(
            "status",
            sa.String(),
            nullable=False,
            server_default="pending",
        ),
    )
    op.drop_column("sellers", "is_active")


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("sellers", "status")
    op.add_column(
        "sellers",
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=True,
        ),
    )
