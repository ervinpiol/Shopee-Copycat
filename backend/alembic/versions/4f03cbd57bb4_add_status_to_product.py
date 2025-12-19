"""add status to product

Revision ID: 4f03cbd57bb4
Revises: c8ca64e4af0c
Create Date: 2025-12-19 10:19:38.176046

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4f03cbd57bb4'
down_revision: Union[str, None] = 'c8ca64e4af0c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Create enum type if it doesn't exist
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'status_enum') THEN
                CREATE TYPE status_enum AS ENUM ('in_stock', 'low_stock', 'out_of_stock');
            END IF;
        END$$;
    """)

    # Add column
    op.add_column(
        "product",
        sa.Column(
            "status",
            sa.Enum(
                "in_stock",
                "low_stock",
                "out_of_stock",
                name="status_enum",
            ),
            nullable=True,
        ),
    )


def downgrade():
    op.drop_column("product", "status")
    op.execute("DROP TYPE IF EXISTS status_enum")