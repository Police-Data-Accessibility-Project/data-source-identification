"""Add Submit URL Task Type Enum

Revision ID: b363794fa4e9
Revises: 33a546c93441
Create Date: 2025-04-15 13:38:58.293627

"""
from typing import Sequence, Union


from src.util.alembic_helpers import switch_enum_type

# revision identifiers, used by Alembic.
revision: str = 'b363794fa4e9'
down_revision: Union[str, None] = '33a546c93441'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    switch_enum_type(
        table_name='tasks',
        column_name='task_type',
        enum_name='task_type',
        new_enum_values=[
            "HTML",
            "Relevancy",
            "Record Type",
            "Agency Identification",
            "Misc Metadata",
            "Submit Approved URLs"
        ]
    )


def downgrade() -> None:
    switch_enum_type(
        table_name='tasks',
        column_name='task_type',
        enum_name='task_type',
        new_enum_values=[
            "HTML",
            "Relevancy",
            "Record Type",
            "Agency Identification",
            "Misc Metadata",
        ]
    )