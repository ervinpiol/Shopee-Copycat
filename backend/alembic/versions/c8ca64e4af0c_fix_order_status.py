"""fix order status

Revision ID: c8ca64e4af0c
Revises: 7d2a18455fbb
Create Date: 2025-12-18 18:46:29.732620

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from app.models.order import OrderStatus


# revision identifiers, used by Alembic.
revision: str = 'c8ca64e4af0c'
down_revision: Union[str, None] = '7d2a18455fbb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade():
    # 1. Create new lowercase enum type
    op.execute(
        "CREATE TYPE order_status_enum_new AS ENUM ('pending','processing','shipped','delivered','cancelled')"
    )

    # 2. Drop defaults first (if column exists)
    op.execute("ALTER TABLE orders ALTER COLUMN status DROP DEFAULT")

    # 3. Alter orders.status type to new enum
    op.execute(
        """
        ALTER TABLE orders
        ALTER COLUMN status
        TYPE order_status_enum_new
        USING status::text::order_status_enum_new
        """
    )

    # 4. Add status column to order_item if it does not exist
    #    (use server_default 'pending' so existing rows get a default value)
    with op.batch_alter_table("order_item") as batch_op:
        batch_op.add_column(
            sa.Column(
                "status",
                sa.Enum(
                    OrderStatus,
                    name="order_status_enum_new",
                    values_callable=lambda x: [e.value for e in x],
                ),
                nullable=False,
                server_default="pending",
            )
        )

    # 5. Set new default for orders.status
    op.execute("ALTER TABLE orders ALTER COLUMN status SET DEFAULT 'pending'")

    # 6. Drop old enum and rename new enum
    op.execute("DROP TYPE order_status_enum")
    op.execute("ALTER TYPE order_status_enum_new RENAME TO order_status_enum")


def downgrade():
    # Recreate old enum (uppercase)
    op.execute(
        "CREATE TYPE order_status_enum_old AS ENUM ('PENDING','PROCESSING','SHIPPED','DELIVERED','CANCELLED')"
    )

    # Drop defaults first
    op.execute("ALTER TABLE orders ALTER COLUMN status DROP DEFAULT")

    # Revert orders.status type
    op.execute(
        """
        ALTER TABLE orders
        ALTER COLUMN status
        TYPE order_status_enum_old
        USING UPPER(status)::order_status_enum_old
        """
    )

    # Drop status column in order_item
    with op.batch_alter_table("order_item") as batch_op:
        batch_op.drop_column("status")

    # Reset default for orders.status
    op.execute("ALTER TABLE orders ALTER COLUMN status SET DEFAULT 'PENDING'")

    # Drop lowercase enum and rename old enum
    op.execute("DROP TYPE order_status_enum")
    op.execute("ALTER TYPE order_status_enum_old RENAME TO order_status_enum")