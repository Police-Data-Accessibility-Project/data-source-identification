"""Alter relevant annotations table

Revision ID: d6519a3ca5c9
Revises: 4b0f43f61598
Create Date: 2025-07-15 11:06:36.534900

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'd6519a3ca5c9'
down_revision: Union[str, None] = '4b0f43f61598'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

HTML_TABLE_NAME = 'url_compressed_html'
AUTO_RELEVANT_TABLE_NAME = 'auto_relevant_suggestions'

CONFIDENCE_COLUMN_NAME = 'confidence'
MODEL_NAME_COLUMN_NAME = 'model_name'

CHECK_CONSTRAINT_NAME = f'ck_{AUTO_RELEVANT_TABLE_NAME}_{CONFIDENCE_COLUMN_NAME}_between_0_and_1'


def _alter_auto_relevant_table() -> None:
    # Add confidence column
    op.add_column(
        AUTO_RELEVANT_TABLE_NAME,
        sa.Column(CONFIDENCE_COLUMN_NAME, sa.Float(), nullable=True)
    )
    # Add check constraint that confidence is between 0 and 1
    op.create_check_constraint(
        CHECK_CONSTRAINT_NAME,
        AUTO_RELEVANT_TABLE_NAME,
        f'{CONFIDENCE_COLUMN_NAME} BETWEEN 0 AND 1'
    )

    # Add model name column
    op.add_column(
        AUTO_RELEVANT_TABLE_NAME,
        sa.Column(MODEL_NAME_COLUMN_NAME, sa.String(), nullable=True)
    )


def _revert_auto_relevant_table() -> None:
    op.drop_column(AUTO_RELEVANT_TABLE_NAME, CONFIDENCE_COLUMN_NAME)
    op.drop_column(AUTO_RELEVANT_TABLE_NAME, MODEL_NAME_COLUMN_NAME)



def upgrade() -> None:
    _alter_auto_relevant_table()


def downgrade() -> None:
    _revert_auto_relevant_table()
