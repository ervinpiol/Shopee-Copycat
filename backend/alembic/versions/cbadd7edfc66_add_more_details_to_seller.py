"""add more details to seller

Revision ID: cbadd7edfc66
Revises: 4a8e64fd7105
Create Date: 2026-01-01 10:41:11.163867

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cbadd7edfc66'
down_revision: Union[str, None] = '4a8e64fd7105'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # 1️⃣ Add columns as nullable
    op.add_column(
        "sellers",
        sa.Column("address_line1", sa.String(), nullable=True),
    )
    op.add_column(
        "sellers",
        sa.Column("address_line2", sa.String(), nullable=True),
    )
    op.add_column(
        "sellers",
        sa.Column("city", sa.String(), nullable=True),
    )
    op.add_column(
        "sellers",
        sa.Column("province", sa.String(), nullable=True),
    )
    op.add_column(
        "sellers",
        sa.Column("postal_code", sa.Integer(), nullable=True),
    )
    op.add_column(
        "sellers",
        sa.Column(
            "country",
            sa.String(),
            nullable=True,
            server_default="PH",
        ),
    )

    # 2️⃣ Backfill existing rows
    op.execute("""
        UPDATE sellers
        SET
            address_line1 = 'N/A',
            city = 'N/A',
            province = 'N/A',
            postal_code = 0,
            country = 'PH'
        WHERE address_line1 IS NULL
    """)

    # 3️⃣ Enforce NOT NULL
    op.alter_column("sellers", "address_line1", nullable=False)
    op.alter_column("sellers", "city", nullable=False)
    op.alter_column("sellers", "province", nullable=False)
    op.alter_column("sellers", "postal_code", nullable=False)
    op.alter_column("sellers", "country", nullable=False)

    

def downgrade():
    op.drop_column("sellers", "address_line1")
    op.drop_column("sellers", "address_line2")
    op.drop_column("sellers", "city")
    op.drop_column("sellers", "province")
    op.drop_column("sellers", "postal_code")
    op.drop_column("sellers", "country")