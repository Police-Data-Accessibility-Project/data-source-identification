"""Create url_checked_for_duplicate table

Revision ID: 864107b703ae
Revises: 9d4002437ebe
Create Date: 2025-05-13 07:04:22.592396

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from src.util.alembic_helpers import switch_enum_type

# revision identifiers, used by Alembic.
revision: str = '864107b703ae'
down_revision: Union[str, None] = '9d4002437ebe'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'url_checked_for_duplicate',
        sa.Column(
            'id',
            sa.Integer(),
            primary_key=True
        ),
        sa.Column(
            'url_id',
            sa.Integer(),
            sa.ForeignKey(
                'urls.id',
                ondelete='CASCADE'
            ),
            nullable=False
        ),
        sa.Column(
            'created_at',
            sa.DateTime(),
            nullable=False,
            server_default=sa.text('now()')
        ),
    )

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
            "Submit Approved URLs",
            "Duplicate Detection"
        ]
    )


def downgrade() -> None:
    op.drop_table('url_checked_for_duplicate')

    # Delete tasks of type "Duplicate Detection"
    op.execute("DELETE FROM TASKS WHERE TASK_TYPE = 'Duplicate Detection';")

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
            "Submit Approved URLs",
        ]
    )
