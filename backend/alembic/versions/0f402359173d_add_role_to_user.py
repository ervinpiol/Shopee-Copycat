"""add role to user

Revision ID: 0f402359173d
Revises: 7d056f27be57
Create Date: 2025-12-18 09:48:09.040734

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0f402359173d'
down_revision: Union[str, None] = '7d056f27be57'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


user_role_enum = sa.Enum(
    "customer",
    "seller",
    "admin",
    name="userrole"
)


def upgrade() -> None:
    # Create enum type
    user_role_enum.create(op.get_bind(), checkfirst=True)

    # Add role column
    op.add_column(
        "user",
        sa.Column(
            "role",
            user_role_enum,
            nullable=False,
            server_default="customer",
        ),
    )

    # Backfill from old data (SAFE EVEN IF UNUSED)
    op.execute(
        """
        UPDATE "user"
        SET role = CASE
            WHEN is_seller = true THEN 'seller'::userrole
            ELSE 'customer'::userrole
        END
        """
    )

    # Drop is_seller permanently
    op.drop_column("user", "is_seller")


def downgrade() -> None:
    # Best-effort downgrade (optional)
    op.add_column(
        "user",
        sa.Column(
            "is_seller",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )

    op.execute(
        """
        UPDATE "user"
        SET is_seller = CASE
            WHEN role = 'seller' THEN true
            ELSE false
        END
        """
    )

    op.drop_column("user", "role")
    user_role_enum.drop(op.get_bind(), checkfirst=True)