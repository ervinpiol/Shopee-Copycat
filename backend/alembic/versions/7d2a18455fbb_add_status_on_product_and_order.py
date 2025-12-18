"""add status on product and order

Revision ID: 7d2a18455fbb
Revises: 5486042b4b30
Create Date: 2025-12-18 18:19:24.304046

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '7d2a18455fbb'
down_revision: Union[str, None] = '5486042b4b30'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade() -> None:
    # 1. Handle Order changes
    op.alter_column('orders', 'order_date', new_column_name='created_at')
    op.add_column('orders', sa.Column(
        'updated_at', sa.DateTime(timezone=True), 
        server_default=sa.func.now(), nullable=False
    ))

    # 2. Create enum types
    order_status_enum = postgresql.ENUM(
        'pending', 'processing', 'shipped', 'delivered', 'cancelled',
        name='order_status_enum'
    )
    product_status_enum = postgresql.ENUM(
        'in_stock', 'low_stock', 'out_of_stock',
        name='product_status_enum'
    )
    order_item_status_enum = postgresql.ENUM(
        'pending', 'processing', 'shipped', 'cancelled',
        name='order_item_status_enum'
    )

    # Create enum types in DB if not exist
    order_status_enum.create(op.get_bind(), checkfirst=True)
    product_status_enum.create(op.get_bind(), checkfirst=True)
    order_item_status_enum.create(op.get_bind(), checkfirst=True)

    # 3. Convert existing 'orders.status' from string to enum
    op.alter_column(
        'orders',
        'status',
        type_=order_status_enum,
        postgresql_using="status::order_status_enum",
        existing_type=sa.String(),
        nullable=False,
        server_default='pending'
    )

    # 4. Add new columns to 'products' only if table exists
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if 'products' in inspector.get_table_names():
        op.add_column('products', sa.Column('status', product_status_enum, nullable=True))
        op.add_column('products', sa.Column(
            'created_at', sa.DateTime(timezone=True),
            server_default=sa.func.now(), nullable=False
        ))
        op.add_column('products', sa.Column(
            'updated_at', sa.DateTime(timezone=True),
            server_default=sa.func.now(), nullable=False
        ))

    # 5. Add status column to order_items if table exists
    if 'order_items' in inspector.get_table_names():
        op.add_column('order_items', sa.Column(
            'status', order_item_status_enum, nullable=False, server_default='pending'
        ))


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    # Drop status column from order_items if table exists
    if 'order_items' in inspector.get_table_names():
        op.drop_column('order_items', 'status')

    # Drop columns from 'products' if table exists
    if 'products' in inspector.get_table_names():
        op.drop_column('products', 'updated_at')
        op.drop_column('products', 'created_at')
        op.drop_column('products', 'status')
    
    # Convert 'orders.status' back to string
    op.alter_column(
        'orders',
        'status',
        type_=sa.String(),
        postgresql_using="status::text",
        existing_type=postgresql.ENUM(
            'pending', 'processing', 'shipped', 'delivered', 'cancelled',
            name='order_status_enum'
        ),
        nullable=False
    )

    # Drop 'orders' columns and rename
    op.drop_column('orders', 'updated_at')
    op.alter_column('orders', 'created_at', new_column_name='order_date')

    # Drop enum types
    postgresql.ENUM(name='order_item_status_enum').drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name='product_status_enum').drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name='order_status_enum').drop(op.get_bind(), checkfirst=True)