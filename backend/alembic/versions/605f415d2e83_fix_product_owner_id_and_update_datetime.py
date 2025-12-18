"""fix product owner id and update datetime

Revision ID: 605f415d2e83
Revises: d5f1dc4c57c0
Create Date: 2025-12-18 15:26:43.871478

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '605f415d2e83'
down_revision: Union[str, None] = 'd5f1dc4c57c0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add timestamps
    op.add_column(
        "sellers",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    op.add_column(
        "sellers",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    # Auto-update updated_at
    op.execute("""
    CREATE OR REPLACE FUNCTION update_updated_at_column()
    RETURNS TRIGGER AS $$
    BEGIN
        NEW.updated_at = NOW();
        RETURN NEW;
    END;
    $$ language 'plpgsql';
    """)

    op.execute("""
    CREATE TRIGGER set_sellers_updated_at
    BEFORE UPDATE ON sellers
    FOR EACH ROW
    EXECUTE PROCEDURE update_updated_at_column();
    """)

    # Fix FK
    op.drop_constraint("sellers_owner_id_fkey", "sellers", type_="foreignkey")

    op.create_foreign_key(
        "sellers_owner_id_fkey",
        "sellers",
        "user",
        ["owner_id"],
        ["id"],
        ondelete="CASCADE",
    )



def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS set_sellers_updated_at ON sellers;")
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column;")

    op.drop_column("sellers", "updated_at")
    op.drop_column("sellers", "created_at")

    op.drop_constraint("sellers_owner_id_fkey", "sellers", type_="foreignkey")

    op.create_foreign_key(
        "sellers_owner_id_fkey",
        "sellers",
        "users",
        ["owner_id"],
        ["id"],
    )
