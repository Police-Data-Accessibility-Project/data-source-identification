"""Add url_agency_suggestions

Revision ID: 19bf57df581a
Revises: 072b32a45b1c
Create Date: 2025-02-02 10:33:02.029875

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from collector_db.enums import PGEnum
# revision identifiers, used by Alembic.
revision: str = '19bf57df581a'
down_revision: Union[str, None] = '072b32a45b1c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


suggestion_type_enum = PGEnum('Suggestion', 'Unknown', 'New Agency', 'Confirmed', name='url_agency_suggestion_type')

def upgrade() -> None:
    op.create_table('url_agency_suggestions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('url_id', sa.Integer(), nullable=False),
        sa.Column('suggestion_type', suggestion_type_enum, nullable=False),
        sa.Column('agency_id', sa.Integer(), nullable=True),
        sa.Column('agency_name', sa.String(), nullable=False),
        sa.Column('state', sa.String(), nullable=True),
        sa.Column('county', sa.String(), nullable=True),
        sa.Column('locality', sa.String(), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['url_id'], ['urls.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('url_agency_suggestions')
    suggestion_type_enum.drop(op.get_bind(), checkfirst=True)
