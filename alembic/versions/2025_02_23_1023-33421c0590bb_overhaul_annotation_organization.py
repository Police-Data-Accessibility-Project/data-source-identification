"""Overhaul annotation organization

New Tables
- AutoRelevantSuggestions
- AutoRecordTypeSuggestions
- UserRelevantSuggestions
- UserRecordTypeSuggestions

New Columns for `URL`
- `agency_id`
- `record_type`
- `relevant`

Removed Tables
- `URLMetadata`
- `ConfirmedURLAgency`
- `MetadataAnnotation`

Update URL Status to just three enum value:
- VALIDATED
- SUBMITTED
- PENDING

Revision ID: 33421c0590bb
Revises: 0c6dc00806ce
Create Date: 2025-02-23 10:23:19.696248

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import UniqueConstraint

from src.util.alembic_helpers import switch_enum_type

# revision identifiers, used by Alembic.
revision: str = '33421c0590bb'
down_revision: Union[str, None] = '0c6dc00806ce'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

record_type_values = [
    "Accident Reports",
    "Arrest Records",
    "Calls for Service",
    "Car GPS",
    "Citations",
    "Dispatch Logs",
    "Dispatch Recordings",
    "Field Contacts",
    "Incident Reports",
    "Misc Police Activity",
    "Officer Involved Shootings",
    "Stops",
    "Surveys",
    "Use of Force Reports",
    "Vehicle Pursuits",
    "Complaints & Misconduct",
    "Daily Activity Logs",
    "Training & Hiring Info",
    "Personnel Records",
    "Annual & Monthly Reports",
    "Budgets & Finances",
    "Contact Info & Agency Meta",
    "Geographic",
    "List of Data Sources",
    "Policies & Contracts",
    "Crime Maps & Reports",
    "Crime Statistics",
    "Media Bulletins",
    "Records Request Info",
    "Resources",
    "Sex Offender Registry",
    "Wanted Persons",
    "Booking Reports",
    "Court Cases",
    "Incarceration Records",
    "Other"
]


record_type_enum = sa.Enum(*record_type_values, name='record_type')

def run_data_migrations():

    op.execute(
        """
        INSERT INTO AUTO_RELEVANT_SUGGESTIONS (url_id, relevant) 
            SELECT url_id, LOWER(value)::boolean
            FROM public.url_metadata
            WHERE validation_source = 'Machine Learning'
            and attribute = 'Relevant'
	    """
    )

    op.execute(
        """
        INSERT INTO AUTO_RECORD_TYPE_SUGGESTIONS(url_id, record_type)
        SELECT url_id, value::record_type
        FROM public.url_metadata
        WHERE validation_source = 'Machine Learning'
        and attribute = 'Record Type'
        """
    )

    op.execute(
        """
        INSERT INTO USER_RELEVANT_SUGGESTIONS(url_id, relevant, user_id)
        SELECT um.url_id, LOWER(um.value)::boolean, ma.user_id
        FROM public.url_metadata um
        INNER join metadata_annotations ma on um.id = ma.metadata_id
        where um.attribute = 'Relevant'
        """
    )

    op.execute(
        """
        INSERT INTO USER_RECORD_TYPE_SUGGESTIONS(url_id, record_type, user_id)
        SELECT um.url_id, um.value::record_type, ma.user_id
        FROM public.url_metadata um
        INNER join metadata_annotations ma on um.id = ma.metadata_id
        where um.attribute = 'Record Type'

        """
    )

def upgrade() -> None:

    # Create the new tables
    op.create_table(
        'auto_relevant_suggestions',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('url_id', sa.Integer(), sa.ForeignKey('urls.id', ondelete='CASCADE'), nullable=False),
        sa.Column('relevant', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('now()'), onupdate=sa.text('now()')),
        UniqueConstraint(
            'url_id',
            name='auto_relevant_suggestions_uq_url_id'
        )
    )

    op.create_table(
        'auto_record_type_suggestions',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column(
            'url_id',
            sa.Integer(),
            sa.ForeignKey('urls.id', ondelete='CASCADE'),
            nullable=False
        ),
        sa.Column('record_type', record_type_enum, nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('now()'), onupdate=sa.text('now()')),
        UniqueConstraint(
            'url_id',
            name='auto_record_type_suggestions_uq_url_id'
        )
    )

    op.create_table(
        'user_relevant_suggestions',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column(
            'url_id',
            sa.Integer(),
            sa.ForeignKey('urls.id', ondelete='CASCADE'),
            nullable=False
        ),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('relevant', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('now()'), onupdate=sa.text('now()')),
        sa.UniqueConstraint("url_id", "user_id", name="uq_user_relevant_suggestions")
    )

    op.create_table(
        'user_record_type_suggestions',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column(
            'url_id',
            sa.Integer(),
            sa.ForeignKey('urls.id', ondelete='CASCADE'),
            nullable=False
        ),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('record_type', record_type_enum, nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('now()'), onupdate=sa.text('now()')),
        sa.UniqueConstraint("url_id", "user_id", name="uq_user_record_type_suggestions")
    )

    # Add the new columns
    op.add_column(
        'urls',
        sa.Column('record_type', record_type_enum, nullable=True)
    )

    op.add_column(
        'urls',
        sa.Column('relevant', sa.Boolean(), nullable=True)
    )

    op.add_column(
        'urls',
        sa.Column(
            'agency_id',
            sa.Integer(),
            sa.ForeignKey('agencies.agency_id', ondelete='NO ACTION'),
            nullable=True
        )
    )

    run_data_migrations()

    # Delete the old tables
    op.drop_table('metadata_annotations')
    op.drop_table('url_metadata')
    op.drop_table('confirmed_url_agency')

    switch_enum_type(
        table_name='urls',
        column_name='outcome',
        enum_name='url_status',
        new_enum_values=['pending', 'submitted', 'validated', 'error', 'duplicate']
    )





def downgrade() -> None:
    # Drop the new tables
    op.drop_table('auto_relevant_suggestions')
    op.drop_table('auto_record_type_suggestions')
    op.drop_table('user_relevant_suggestions')
    op.drop_table('user_record_type_suggestions')

    # Drop the new columns
    op.drop_column('urls', 'record_type')
    op.drop_column('urls', 'relevant')
    op.drop_column('urls', 'agency_id')

    # Create the old tables
    op.create_table(
        'url_metadata',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('url_id', sa.Integer(), sa.ForeignKey('urls.id', ondelete='CASCADE'), nullable=False),
        sa.Column('attribute', sa.String(), nullable=False),
        sa.Column('value', sa.String(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('now()'), onupdate=sa.text('now()')),
        sa.UniqueConstraint(
            "url_id",
            "attribute",
            name="uq_url_id_attribute"),
    )

    op.create_table(
        'confirmed_url_agency',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('url_id', sa.Integer(), sa.ForeignKey('urls.id', ondelete='CASCADE'), nullable=False),
        sa.Column(
            'agency_id',
            sa.Integer(),
            sa.ForeignKey('agencies.agency_id', ondelete='CASCADE'), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('now()'), onupdate=sa.text('now()')),
        sa.UniqueConstraint("url_id", name="uq_confirmed_url_agency")
    )

    op.create_table(
        'metadata_annotations',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('metadata_id', sa.Integer(), sa.ForeignKey('url_metadata.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('now()'), onupdate=sa.text('now()')),
        sa.UniqueConstraint(
            "user_id",
            "metadata_id",
            name="metadata_annotations_uq_user_id_metadata_id"),
    )

    switch_enum_type(
        table_name='urls',
        column_name='outcome',
        enum_name='url_status',
        new_enum_values=['pending', 'submitted', 'human_labeling', 'rejected', 'duplicate', 'error']
    )

    # Drop enum
    record_type_enum.drop(op.get_bind())
