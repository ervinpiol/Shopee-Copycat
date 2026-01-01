"""add phone to sellers

Revision ID: 4a8e64fd7105
Revises: d40a3278fa3d
Create Date: 2026-01-01 10:34:09.616138

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4a8e64fd7105'
down_revision: Union[str, None] = 'd40a3278fa3d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # 1️⃣ Add column as nullable
    op.add_column(
        "sellers",
        sa.Column("phone", sa.String(), nullable=True),
    )

    # 2️⃣ Backfill existing rows (temporary value)
    op.execute(
        "UPDATE sellers SET phone = '0000000000' WHERE phone IS NULL"
    )

    # 3️⃣ Enforce NOT NULL
    op.alter_column(
        "sellers",
        "phone",
        nullable=False,
    )
    

def downgrade():
    op.drop_column("sellers", "phone")