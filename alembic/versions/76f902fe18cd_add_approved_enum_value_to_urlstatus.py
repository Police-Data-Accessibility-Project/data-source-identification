"""Add approved enum value to URLStatus

Revision ID: 76f902fe18cd
Revises: d7eb670edaf0
Create Date: 2025-02-21 13:46:00.621485

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '76f902fe18cd'
down_revision: Union[str, None] = 'd7eb670edaf0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

old_enum_values = ('pending', 'submitted', 'human_labeling', 'rejected', 'duplicate', 'error')
new_enum_values = old_enum_values + ('approved',)

old_outcome_enum = postgresql.ENUM(
    *old_enum_values,
    name='url_status'
)

tmp_new_outcome_enum = postgresql.ENUM(
    *new_enum_values,
    name='tmp_url_status'
)
new_outcome_enum = postgresql.ENUM(
    *new_enum_values,
    name='url_status'
)

common_args = {
    "table_name": "urls",
    "column_name": "outcome",
}

def upgrade() -> None:
    tmp_new_outcome_enum.create(op.get_bind(), checkfirst=True)
    op.alter_column(
        **common_args,
        existing_type=old_outcome_enum,
        type_=tmp_new_outcome_enum,
        postgresql_using='outcome::text::tmp_url_status'
    )
    old_outcome_enum.drop(op.get_bind(), checkfirst=True)
    new_outcome_enum.create(op.get_bind(), checkfirst=True)

    op.alter_column(
        **common_args,
        existing_type=tmp_new_outcome_enum,
        type_=new_outcome_enum,
        postgresql_using='outcome::text::url_status'
    )
    tmp_new_outcome_enum.drop(op.get_bind(), checkfirst=True)

def downgrade() -> None:
    tmp_new_outcome_enum.create(op.get_bind())
    op.alter_column(
        **common_args,
        existing_type=new_outcome_enum,
        type_=tmp_new_outcome_enum,
        postgresql_using='outcome::text::tmp_url_status'
    )

    new_outcome_enum.drop(op.get_bind(), checkfirst=True)
    old_outcome_enum.create(op.get_bind(), checkfirst=True)

    op.alter_column(
        **common_args,
        existing_type=tmp_new_outcome_enum,
        type_=old_outcome_enum,
        postgresql_using='outcome::text::url_status'
    )

    tmp_new_outcome_enum.drop(op.get_bind(), checkfirst=True)