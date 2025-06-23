"""Update relevancy logic

- Add new status to URL Status outcome: `individual record`
- Change URL Status value `rejected` to `not relevant` , for specificity
- Create `user_suggested_status` enum
- ` Add `suggested_status` column to `user_relevant_suggestions`
- Migrate `user_relevant_suggestions:relevant` to `user_relevant_suggestions:user_suggested_status`

Revision ID: 00cc949e0347
Revises: b5f079b6b8cb
Create Date: 2025-05-16 10:31:04.417203

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from src.util.alembic_helpers import switch_enum_type

# revision identifiers, used by Alembic.
revision: str = '00cc949e0347'
down_revision: Union[str, None] = 'b5f079b6b8cb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


suggested_status_enum = sa.Enum(
    'relevant',
    'not relevant',
    'individual record',
    'broken page/404 not found',
    name='suggested_status'
)

def upgrade() -> None:
    suggested_status_enum.create(op.get_bind())
    # Replace `relevant` column with `suggested_status` column
    op.add_column(
        'user_relevant_suggestions',
        sa.Column(
            'suggested_status',
            suggested_status_enum,
            nullable=True
        )
    )
    # Migrate existing entries
    op.execute("""
        UPDATE user_relevant_suggestions
        SET suggested_status = 'relevant'
        WHERE relevant = true
    """)
    op.execute("""
        UPDATE user_relevant_suggestions
        SET suggested_status = 'not relevant'
        WHERE relevant = false
    """)
    op.alter_column(
        'user_relevant_suggestions',
        'suggested_status',
        nullable=False
    )
    op.drop_column(
        'user_relevant_suggestions',
        'relevant'
    )

    # Update `url_status` enum to include
    # `individual record`
    # And change `rejected` to `not relevant`
    op.execute("""
    ALTER TYPE url_status RENAME VALUE 'rejected' TO 'not relevant';
    """)
    switch_enum_type(
        table_name='urls',
        column_name='outcome',
        enum_name='url_status',
        new_enum_values=[
            'pending',
            'submitted',
            'validated',
            'duplicate',
            'not relevant',
            'error',
            '404 not found',
            'individual record'
        ],
        check_constraints_to_drop=['url_name_not_null_when_validated']
    )
    op.execute(
    """
    ALTER TABLE urls
        ADD CONSTRAINT url_name_not_null_when_validated
            CHECK ((name IS NOT NULL) OR (outcome <> 'validated'::url_status))
           """
    )


def downgrade() -> None:
    # Update `url_status` enum to remove
    # `individual record`
    # And change `not relevant` to `rejected`
    op.execute("""
    ALTER TYPE url_status RENAME VALUE 'not relevant' TO 'rejected';
    """)
    op.execute("""
    UPDATE urls
    SET outcome = 'rejected'
    WHERE outcome = 'individual record'
    """)
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
            'error',
            '404 not found',
        ],
        check_constraints_to_drop=['url_name_not_null_when_validated']
    )
    op.execute(
    """
    ALTER TABLE urls
        ADD CONSTRAINT url_name_not_null_when_validated
            CHECK ((name IS NOT NULL) OR (outcome <> 'validated'::url_status))
           """
    )

    # Replace `suggested_status` column with `relevant` column
    op.add_column(
        'user_relevant_suggestions',
        sa.Column(
            'relevant',
            sa.BOOLEAN(),
            nullable=True
        )
    )
    op.execute("""
        UPDATE user_relevant_suggestions
        SET relevant = true
        WHERE suggested_status = 'relevant'
    """)
    op.execute("""
        UPDATE user_relevant_suggestions
        SET relevant = false
        WHERE suggested_status = 'not relevant'
    """)
    op.alter_column(
        'user_relevant_suggestions',
        'relevant',
        nullable=False
    )
    op.drop_column(
        'user_relevant_suggestions',
        'suggested_status'
    )
    suggested_status_enum.drop(op.get_bind(), checkfirst=True)
