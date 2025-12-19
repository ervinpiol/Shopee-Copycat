"""populate seller_id for existing orders

Revision ID: 5486042b4b30
Revises: de9874d1c795
Create Date: 2025-12-18 18:03:22.016323

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5486042b4b30'
down_revision: Union[str, None] = 'de9874d1c795'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- Create default seller if it doesn't exist ---
    op.execute("""
    INSERT INTO sellers (id, owner_id, store_name, store_category, is_active, created_at, updated_at)
    SELECT 1, 1, 'Default Store', 'General', TRUE, NOW(), NOW()
    WHERE NOT EXISTS (SELECT 1 FROM sellers WHERE id = 1);
    """)

    # --- Update existing order items ---
    op.execute("UPDATE order_item SET seller_id = 1 WHERE seller_id IS NULL;")


def downgrade() -> None:
    # Optionally revert seller_id back to NULL
    op.execute("UPDATE order_item SET seller_id = NULL WHERE seller_id = 1;")

    # Optionally delete default seller
    op.execute("DELETE FROM sellers WHERE id = 1;")
