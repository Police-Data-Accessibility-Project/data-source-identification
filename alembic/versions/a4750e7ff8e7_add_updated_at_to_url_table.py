"""Add updated_at to URL table

Revision ID: a4750e7ff8e7
Revises: d11f07224d1f
Create Date: 2025-01-08 10:25:04.031123

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'a4750e7ff8e7'
down_revision: Union[str, None] = 'd11f07224d1f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add `updated_at` column to the `URL` table
    op.add_column(
        table_name='urls',
        column=sa.Column(
            'updated_at',
            sa.DateTime(),
            server_default=sa.text('CURRENT_TIMESTAMP'),
            nullable=True
        )
    )


    # Create a function and trigger to update the `updated_at` column
    op.execute("""
    CREATE OR REPLACE FUNCTION update_updated_at_column()
    RETURNS TRIGGER AS $$
    BEGIN
        NEW.updated_at = CURRENT_TIMESTAMP;
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """)

    op.execute("""
    CREATE TRIGGER set_updated_at
    BEFORE UPDATE ON urls
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
    """)


def downgrade() -> None:
    # Remove `updated_at` column from the `URL` table
    op.drop_column('urls', 'updated_at')

    # Drop the trigger and function
    op.execute("DROP TRIGGER IF EXISTS set_updated_at ON urls;")
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column;")
