"""Set user annotation tables to allow only one annotation per url

Revision ID: 997f5bf53772
Revises: ed06a5633d2e
Create Date: 2025-04-16 19:54:59.798580

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '997f5bf53772'
down_revision: Union[str, None] = 'ed06a5633d2e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Delete entries with more than one annotation
    # Relevance
    op.execute("""
    with ranked as(
        SELECT
            id,
            ROW_NUMBER() OVER (PARTITION BY URL_ID ORDER BY id) as rn
        FROM
            USER_RELEVANT_SUGGESTIONS
    )
    DELETE FROM user_relevant_suggestions
    USING ranked
    WHERE USER_RELEVANT_SUGGESTIONS.id = ranked.id
    and ranked.rn > 1
    """)
    # Record Type
    op.execute("""
    with ranked as(
        SELECT
            id,
            ROW_NUMBER() OVER (PARTITION BY URL_ID ORDER BY id) as rn
        FROM
            USER_RECORD_TYPE_SUGGESTIONS    
    )
    DELETE FROM user_record_type_suggestions
    USING ranked
    WHERE USER_RECORD_TYPE_SUGGESTIONS.id = ranked.id
    and ranked.rn > 1
    """)

    # Add unique constraint to url_id column
    op.create_unique_constraint('uq_user_relevant_suggestions_url_id', 'user_relevant_suggestions', ['url_id'])
    op.create_unique_constraint('uq_user_record_type_suggestions_url_id', 'user_record_type_suggestions', ['url_id'])
    op.create_unique_constraint('uq_user_agency_suggestions_url_id', 'user_url_agency_suggestions', ['url_id'])



def downgrade() -> None:
    op.drop_constraint('uq_user_relevant_suggestions_url_id', 'user_relevant_suggestions', type_='unique')
    op.drop_constraint('uq_user_record_type_suggestions_url_id', 'user_record_type_suggestions', type_='unique')
    op.drop_constraint('uq_user_agency_suggestions_url_id', 'user_url_agency_suggestions', type_='unique')