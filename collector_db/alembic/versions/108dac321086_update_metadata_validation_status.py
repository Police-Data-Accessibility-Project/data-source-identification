"""Update Metadata Validation Status

Revision ID: 108dac321086
Revises: 5a5ca06f36fa
Create Date: 2025-01-15 17:03:10.539891

"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '108dac321086'
down_revision: Union[str, None] = '5a5ca06f36fa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

validation_status = postgresql.ENUM(
    'Pending Label Studio',
    'Validated',
    name='validation_status'
)

metadata_validation_status = postgresql.ENUM(
    'Pending Validation',
    'Validated',
    name='metadata_validation_status'
)

def upgrade() -> None:
    metadata_validation_status.create(op.get_bind())

    op.alter_column(
        table_name="url_metadata",
        column_name="validation_status",
        existing_type=validation_status,
        type_=metadata_validation_status,
        postgresql_using="validation_status::text::metadata_validation_status"
    )

    validation_status.drop(op.get_bind(), checkfirst=True)

def downgrade() -> None:
    validation_status.create(op.get_bind())

    op.alter_column(
        table_name="url_metadata",
        column_name="validation_status",
        existing_type=metadata_validation_status,
        type_=validation_status,
        postgresql_using="validation_status::text::validation_status"
    )

    metadata_validation_status.drop(op.get_bind(), checkfirst=True)
