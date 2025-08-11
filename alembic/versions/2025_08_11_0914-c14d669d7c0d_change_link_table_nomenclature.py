"""Change Link table nomenclature

Revision ID: c14d669d7c0d
Revises: 5930e70660c5
Create Date: 2025-08-11 09:14:08.034093

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c14d669d7c0d'
down_revision: Union[str, None] = '5930e70660c5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

OLD_URL_DATA_SOURCE_NAME = "url_data_sources"
NEW_URL_DATA_SOURCE_NAME = "url_data_source"

def upgrade() -> None:
    op.rename_table(OLD_URL_DATA_SOURCE_NAME, NEW_URL_DATA_SOURCE_NAME)


def downgrade() -> None:
    op.rename_table(NEW_URL_DATA_SOURCE_NAME, OLD_URL_DATA_SOURCE_NAME)
