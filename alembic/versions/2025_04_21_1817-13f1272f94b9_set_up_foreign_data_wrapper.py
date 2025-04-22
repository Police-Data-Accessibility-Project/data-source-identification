"""Set up foreign data wrapper

Revision ID: 13f1272f94b9
Revises: e285e6e7cf71
Create Date: 2025-04-21 18:17:34.593973

"""
import os
from typing import Sequence, Union

from alembic import op
from dotenv import load_dotenv

# revision identifiers, used by Alembic.
revision: str = '13f1272f94b9'
down_revision: Union[str, None] = 'e285e6e7cf71'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    load_dotenv()
    remote_host = os.getenv("DATA_SOURCES_HOST")
    user = os.getenv("DATA_SOURCES_USER")
    password = os.getenv("DATA_SOURCES_PASSWORD")
    db_name = os.getenv("DATA_SOURCES_DB")
    port = os.getenv("DATA_SOURCES_PORT")

    op.execute(f"CREATE EXTENSION IF NOT EXISTS postgres_fdw;")

    op.execute(f"""
        CREATE SERVER data_sources_server
        FOREIGN DATA WRAPPER postgres_fdw
        OPTIONS (host '{remote_host}', dbname '{db_name}', port '{port}');
    """)

    op.execute(f"""
        CREATE USER MAPPING FOR {user}
        SERVER data_sources_server
        OPTIONS (user '{user}', password '{password}');
    """)

    op.execute('CREATE SCHEMA if not exists "remote";')

    # Users table
    op.execute("""
    CREATE FOREIGN TABLE IF NOT EXISTS "remote".users
    (
        id bigint,
        created_at timestamp with time zone,
        updated_at timestamp with time zone,
        email text,
        password_digest text,
        api_key character varying,
        role text 
    )
    SERVER data_sources_server
    OPTIONS (
        schema_name 'public',
        table_name 'users'
    );
    """)

    # Agencies
    # -Enums
    # --Jurisdiction Type
    op.execute("""
    CREATE  TYPE jurisdiction_type AS ENUM
        ('school', 'county', 'local', 'port', 'tribal', 'transit', 'state', 'federal');
    """)
    # --Agency Type
    op.execute("""
    CREATE  TYPE agency_type AS ENUM
    ('incarceration', 'law enforcement', 'aggregated', 'court', 'unknown');
    """)

    # -Table
    op.execute("""
    CREATE FOREIGN TABLE IF NOT EXISTS "remote".agencies
    (
        name character  ,
        homepage_url character ,
        jurisdiction_type jurisdiction_type ,
        lat double precision,
        lng double precision,
        defunct_year character ,
        airtable_uid character ,
        agency_type agency_type ,
        multi_agency boolean  ,
        no_web_presence boolean  ,
        airtable_agency_last_modified timestamp with time zone,
        rejection_reason character ,
        last_approval_editor character ,
        submitter_contact character,
        agency_created timestamp with time zone,
        id integer,
        approval_status text,
        creator_user_id integer
    )
    SERVER data_sources_server
    OPTIONS (
        schema_name 'public',
        table_name 'agencies'
    );
    """)

    # Locations Table
    # -Enums
    # --Location Type
    op.execute("""
        CREATE  TYPE location_type AS ENUM
        ('State', 'County', 'Locality');
    """)

    # -Table
    op.execute("""
    CREATE FOREIGN TABLE IF NOT EXISTS "remote".locations
    (
        id bigint,
        type location_type,
        state_id bigint,
        county_id bigint,
        locality_id bigint
    )
    SERVER data_sources_server
    OPTIONS (
        schema_name 'public',
        table_name 'locations'
    );
    """)

    # Data Sources Table

    # -Enums
    # -- access_type
    op.execute("""
        CREATE  TYPE access_type AS ENUM
        ('Download', 'Webpage', 'API');
    """)

    # -- agency_aggregation
    op.execute("""
        CREATE  TYPE agency_aggregation AS ENUM
        ('county', 'local', 'state', 'federal');
    """)
    # -- update_method
    op.execute("""
        CREATE  TYPE update_method AS ENUM
        ('Insert', 'No updates', 'Overwrite');
    """)

    # -- detail_level
    op.execute("""
    CREATE  TYPE detail_level AS ENUM
    ('Individual record', 'Aggregated records', 'Summarized totals');
    """)

    # -- retention_schedule
    op.execute("""
        CREATE  TYPE retention_schedule AS ENUM
        ('< 1 day', '1 day', '< 1 week', '1 week', '1 month', '< 1 year', '1-10 years', '> 10 years', 'Future only');
    """)

    # -Table
    op.execute("""
    CREATE FOREIGN TABLE IF NOT EXISTS "remote".data_sources
    (
        name character varying ,
        description character ,
        source_url character ,
        agency_supplied boolean,
        supplying_entity character ,
        agency_originated boolean,
        agency_aggregation agency_aggregation,
        coverage_start date,
        coverage_end date,
        updated_at timestamp with time zone ,
        detail_level detail_level,
        record_download_option_provided boolean,
        data_portal_type character ,
        update_method update_method,
        readme_url character ,
        originating_entity character ,
        retention_schedule retention_schedule,
        airtable_uid character ,
        scraper_url character ,
        created_at timestamp with time zone ,
        submission_notes character ,
        rejection_note character ,
        submitter_contact_info character ,
        agency_described_not_in_database character ,
        data_portal_type_other character ,
        data_source_request character ,
        broken_source_url_as_of timestamp with time zone,
        access_notes text ,
        url_status text ,
        approval_status text ,
        record_type_id integer,
        access_types access_type[],
        tags text[] ,
        record_formats text[] ,
        id integer,
        approval_status_updated_at timestamp with time zone ,
        last_approval_editor bigint
    )
    SERVER data_sources_server
    OPTIONS (
        schema_name 'public',
        table_name 'data_sources'
    );
    """)



def downgrade() -> None:
    # Drop foreign schema
    op.execute('DROP SCHEMA IF EXISTS "remote" CASCADE;')

    # Drop enums
    enums = [
        "jurisdiction_type",
        "agency_type",
        "location_type",
        "access_type",
        "agency_aggregation",
        "update_method",
        "detail_level",
        "retention_schedule",
    ]
    for enum in enums:
        op.execute(f"""
        DROP TYPE IF EXISTS {enum};
        """)

    # Drop user mapping
    user = os.getenv("DATA_SOURCES_USER")
    op.execute(f"""
    DROP USER MAPPING FOR {user} SERVER data_sources_server;
    """)

    # Drop server
    op.execute("""
    DROP SERVER IF EXISTS data_sources_server CASCADE;
    """)

    # Drop FDW
    op.execute("""
    DROP EXTENSION IF EXISTS postgres_fdw CASCADE;
    """)
