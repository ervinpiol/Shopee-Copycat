"""add first_name and last_name to user

Revision ID: f8915d778922
Revises: 8e59735baab8
Create Date: 2025-12-09 11:16:46.812336

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f8915d778922'
down_revision: Union[str, None] = '8e59735baab8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # 1. Add columns as nullable first
    op.add_column('user', sa.Column('first_name', sa.String(), nullable=True))
    op.add_column('user', sa.Column('last_name', sa.String(), nullable=True))

    # 2. Populate first_name and last_name from existing 'name' column
    #    This splits 'name' by the first space. If no space, last_name will be empty
    op.execute(
        """
        UPDATE "user"
        SET first_name = split_part(name, ' ', 1),
            last_name = CASE WHEN name LIKE '% %' THEN split_part(name, ' ', 2) ELSE '' END
        """
    )

    # 3. Alter columns to NOT NULL now that existing rows are populated
    op.alter_column('user', 'first_name', nullable=False)
    op.alter_column('user', 'last_name', nullable=False)

    # 4. Drop the old 'name' column
    op.drop_column('user', 'name')


def downgrade():
    # 1. Recreate 'name' column as nullable
    op.add_column('user', sa.Column('name', sa.String(), nullable=True))

    # 2. Populate 'name' from first_name and last_name
    op.execute(
        """
        UPDATE "user"
        SET name = first_name || ' ' || last_name
        """
    )

    # 3. Drop first_name and last_name columns
    op.drop_column('user', 'first_name')
    op.drop_column('user', 'last_name')

    # 4. Optionally make 'name' NOT NULL if needed
    op.alter_column('user', 'name', nullable=False)
    