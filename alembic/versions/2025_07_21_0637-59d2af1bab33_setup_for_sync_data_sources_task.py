"""Setup for sync data sources task

Revision ID: 59d2af1bab33
Revises: 9552d354ccf4
Create Date: 2025-07-21 06:37:51.043504

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

from src.util.alembic_helpers import switch_enum_type, id_column

# revision identifiers, used by Alembic.
revision: str = '59d2af1bab33'
down_revision: Union[str, None] = '9552d354ccf4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SYNC_STATE_TABLE_NAME = "data_sources_sync_state"
URL_DATA_SOURCES_METADATA_TABLE_NAME = "url_data_sources_metadata"

CONFIRMED_AGENCY_TABLE_NAME = "confirmed_url_agency"
LINK_URLS_AGENCIES_TABLE_NAME = "link_urls_agencies"
CHANGE_LOG_TABLE_NAME = "change_log"

AGENCIES_TABLE_NAME = "agencies"

TABLES_TO_LOG = [
    LINK_URLS_AGENCIES_TABLE_NAME,
    "urls",
    "url_data_sources",
    "agencies",
]

OperationTypeEnum = sa.Enum("UPDATE", "DELETE", "INSERT", name="operation_type")


def upgrade() -> None:
    _create_data_sources_sync_state_table()
    _create_data_sources_sync_task()

    _rename_confirmed_url_agency_to_link_urls_agencies()
    _create_change_log_table()
    _add_jsonb_diff_val_function()
    _create_log_table_changes_trigger()


    _add_table_change_log_triggers()
    _add_agency_id_column()



def downgrade() -> None:
    _drop_data_sources_sync_task()
    _drop_data_sources_sync_state_table()
    _drop_change_log_table()
    _drop_table_change_log_triggers()
    _drop_jsonb_diff_val_function()
    _drop_log_table_changes_trigger()

    _rename_link_urls_agencies_to_confirmed_url_agency()

    OperationTypeEnum.drop(op.get_bind())
    _drop_agency_id_column()



def _add_jsonb_diff_val_function() -> None:
    op.execute(
        """
        CREATE OR REPLACE FUNCTION jsonb_diff_val(val1 JSONB, val2 JSONB)
            RETURNS JSONB AS
        $$
        DECLARE
            result JSONB;
            v      RECORD;
        BEGIN
            result = val1;
            FOR v IN SELECT * FROM jsonb_each(val2)
                LOOP
                    IF result @> jsonb_build_object(v.key, v.value)
                    THEN
                        result = result - v.key;
                    ELSIF result ? v.key THEN
                        CONTINUE;
                    ELSE
                        result = result || jsonb_build_object(v.key, 'null');
                    END IF;
                END LOOP;
            RETURN result;
        END;
        $$ LANGUAGE plpgsql;
        """
    )

def _drop_jsonb_diff_val_function() -> None:
    op.execute("DROP FUNCTION IF EXISTS jsonb_diff_val(val1 JSONB, val2 JSONB)")

def _create_log_table_changes_trigger() -> None:
    op.execute(
        f"""
        CREATE OR REPLACE FUNCTION public.log_table_changes()
        RETURNS trigger
        LANGUAGE 'plpgsql'
        COST 100
        VOLATILE NOT LEAKPROOF
    AS $BODY$
            DECLARE
                old_values JSONB;
                new_values JSONB;
                old_to_new JSONB;
                new_to_old JSONB;
            BEGIN
                -- Handle DELETE operations (store entire OLD row since all data is lost)
                IF (TG_OP = 'DELETE') THEN
                    old_values = row_to_json(OLD)::jsonb;

                    INSERT INTO {CHANGE_LOG_TABLE_NAME} (operation_type, table_name, affected_id, old_data)
                    VALUES ('DELETE', TG_TABLE_NAME, OLD.id, old_values);

                    RETURN OLD;

                -- Handle UPDATE operations (only log the changed columns)
                ELSIF (TG_OP = 'UPDATE') THEN
                    old_values = row_to_json(OLD)::jsonb;
                    new_values = row_to_json(NEW)::jsonb;
                    new_to_old = jsonb_diff_val(old_values, new_values);
                    old_to_new = jsonb_diff_val(new_values, old_values);

                    -- Skip logging if both old_to_new and new_to_old are NULL or empty JSON objects
                    IF (new_to_old IS NOT NULL AND new_to_old <> '{{}}') OR
                       (old_to_new IS NOT NULL AND old_to_new <> '{{}}') THEN
                        INSERT INTO {CHANGE_LOG_TABLE_NAME} (operation_type, table_name, affected_id, old_data, new_data)
                        VALUES ('UPDATE', TG_TABLE_NAME, OLD.id, new_to_old, old_to_new);
                    END IF;

                    RETURN NEW;

                -- Handle INSERT operations
                ELSIF (TG_OP = 'INSERT') THEN
                    new_values = row_to_json(NEW)::jsonb;

                    -- Skip logging if new_values is NULL or an empty JSON object
                    IF new_values IS NOT NULL AND new_values <> '{{}}' THEN
                        INSERT INTO {CHANGE_LOG_TABLE_NAME} (operation_type, table_name, affected_id, new_data)
                        VALUES ('INSERT', TG_TABLE_NAME, NEW.id, new_values);
                    END IF;

                    RETURN NEW;
                END IF;
            END;
    $BODY$;
    """
    )

def _drop_log_table_changes_trigger() -> None:
    op.execute(f"DROP TRIGGER IF EXISTS log_table_changes ON {URL_DATA_SOURCES_METADATA_TABLE_NAME}")

def _create_data_sources_sync_state_table() -> None:
    table = op.create_table(
        SYNC_STATE_TABLE_NAME,
        id_column(),
        sa.Column('last_full_sync_at', sa.DateTime(), nullable=True),
        sa.Column('current_cutoff_date', sa.Date(), nullable=True),
        sa.Column('current_page', sa.Integer(), nullable=True),
    )
    # Add row to `data_sources_sync_state` table
    op.bulk_insert(
        table,
        [
            {
                "last_full_sync_at": None,
                "current_cutoff_date": None,
                "current_page": None
            }
        ]
    )

def _drop_data_sources_sync_state_table() -> None:
    op.drop_table(SYNC_STATE_TABLE_NAME)

def _create_data_sources_sync_task() -> None:
    switch_enum_type(
        table_name='tasks',
        column_name='task_type',
        enum_name='task_type',
        new_enum_values=[
            'HTML',
            'Relevancy',
            'Record Type',
            'Agency Identification',
            'Misc Metadata',
            'Submit Approved URLs',
            'Duplicate Detection',
            '404 Probe',
            'Sync Agencies',
            'Sync Data Sources'
        ]
    )

def _drop_data_sources_sync_task() -> None:
    switch_enum_type(
        table_name='tasks',
        column_name='task_type',
        enum_name='task_type',
        new_enum_values=[
            'HTML',
            'Relevancy',
            'Record Type',
            'Agency Identification',
            'Misc Metadata',
            'Submit Approved URLs',
            'Duplicate Detection',
            '404 Probe',
            'Sync Agencies',
        ]
    )

def _create_change_log_table() -> None:
    # Create change_log table
    op.create_table(
        CHANGE_LOG_TABLE_NAME,
        id_column(),
        sa.Column("operation_type", OperationTypeEnum, nullable=False),
        sa.Column("table_name", sa.String(), nullable=False),
        sa.Column("affected_id", sa.Integer(), nullable=False),
        sa.Column("old_data", JSONB, nullable=True),
        sa.Column("new_data", JSONB, nullable=True),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False
        ),
    )

def _drop_change_log_table() -> None:
    op.drop_table(CHANGE_LOG_TABLE_NAME)

def _rename_confirmed_url_agency_to_link_urls_agencies() -> None:
    op.rename_table(CONFIRMED_AGENCY_TABLE_NAME, LINK_URLS_AGENCIES_TABLE_NAME)

def _rename_link_urls_agencies_to_confirmed_url_agency() -> None:
    op.rename_table(LINK_URLS_AGENCIES_TABLE_NAME, CONFIRMED_AGENCY_TABLE_NAME)

def _add_table_change_log_triggers() -> None:
    # Create trigger for tables:
    def create_table_trigger(table_name: str) -> None:
        op.execute(
            """
        CREATE OR REPLACE TRIGGER log_{table_name}_changes
        BEFORE INSERT OR DELETE OR UPDATE
        ON public.{table_name}
        FOR EACH ROW
        EXECUTE FUNCTION public.log_table_changes();
        """.format(table_name=table_name)
        )

    for table_name in TABLES_TO_LOG:
        create_table_trigger(table_name)

def _drop_table_change_log_triggers() -> None:
    def drop_table_trigger(table_name: str) -> None:
        op.execute(
            f"""
            DROP TRIGGER log_{table_name}_changes
            ON public.{table_name}
            """
        )

    for table_name in TABLES_TO_LOG:
        drop_table_trigger(table_name)

def _add_agency_id_column():
    op.add_column(
        AGENCIES_TABLE_NAME,
        id_column(),
    )


def _drop_agency_id_column():
    op.drop_column(
        AGENCIES_TABLE_NAME,
        'id',
    )
