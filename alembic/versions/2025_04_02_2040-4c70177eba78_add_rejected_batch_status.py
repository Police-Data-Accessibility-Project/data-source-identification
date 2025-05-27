"""Add rejected batch status

Revision ID: 4c70177eba78
Revises: 5ea47dacd0ef
Create Date: 2025-04-02 20:40:54.982954

"""
from typing import Sequence, Union


from src.util.alembic_helpers import switch_enum_type

# revision identifiers, used by Alembic.
revision: str = '4c70177eba78'
down_revision: Union[str, None] = '5ea47dacd0ef'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    switch_enum_type(
        table_name='urls',
        column_name='outcome',
        enum_name='url_status',
        new_enum_values=[
            'pending',
            'submitted',
            'validated',
            'duplicate',
            'rejected',
            'error'
        ]
    )

def downgrade() -> None:
    switch_enum_type(
        table_name='urls',
        column_name='outcome',
        enum_name='url_status',
        new_enum_values=[
            'pending',
            'submitted',
            'validated',
            'duplicate',
            'error',
        ]
    )
