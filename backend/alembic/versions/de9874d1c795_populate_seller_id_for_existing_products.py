"""populate seller_id for existing products

Revision ID: de9874d1c795
Revises: 605f415d2e83
Create Date: 2025-12-18 16:04:26.166567

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'de9874d1c795'
down_revision: Union[str, None] = '605f415d2e83'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- Create default seller ---
    op.execute("""
    INSERT INTO sellers (id, owner_id, store_name, store_category, is_active, created_at, updated_at)
    VALUES (1, 1, 'Default Store', 'General', TRUE, NOW(), NOW());
    """)

    # --- Update existing products ---
    op.execute("UPDATE product SET seller_id = 1")

def downgrade() -> None:
    # Optionally revert if needed
    op.execute("UPDATE product SET seller_id = NULL")