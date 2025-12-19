"""add created and updated at to product

Revision ID: aa58d23e8350
Revises: 4f03cbd57bb4
Create Date: 2025-12-19 10:24:29.354908

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'aa58d23e8350'
down_revision: Union[str, None] = '4f03cbd57bb4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column(
        "product",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    op.add_column(
        "product",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )


def downgrade():
    op.drop_column("product", "updated_at")
    op.drop_column("product", "created_at")