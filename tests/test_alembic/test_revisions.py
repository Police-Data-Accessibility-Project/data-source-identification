"""
This module tests that revisions perform as expected.

Specifically, they test that:
* Columns are added, removed, or renamed as expected after appropriate migrations
* Data is properly modified (or not modified) after migrations

They do not test the overall integrity of the schema;
 such tests are reserved for database structure tests,
 which test only the most recent version of the schema.

"""


from dataclasses import dataclass
from itertools import product


import pytest
from alembic import command
from alembic.config import Config

from sqlalchemy import create_engine, Inspector, inspect, MetaData, Connection, text

from sqlalchemy.orm import sessionmaker, scoped_session

from collector_db.helper_functions import get_postgres_connection_string
from collector_db.models import Batch

import sqlalchemy as sa

@pytest.fixture()
def alembic_config():
    alembic_cfg = Config("alembic.ini")
    yield alembic_cfg

@pytest.fixture()
def db_engine():
    engine = create_engine(get_postgres_connection_string())
    yield engine
    engine.dispose()

@pytest.fixture()
def connection(db_engine):
    connection = db_engine.connect()
    yield connection
    connection.close()

@dataclass
class AlembicRunner:
    connection: Connection
    alembic_config: Config
    inspector: Inspector
    metadata: MetaData
    session: scoped_session

    def reflect(self):
        self.metadata.clear()
        self.metadata.reflect(bind=self.connection)
        self.inspector = inspect(self.connection)

    def upgrade(self, revision: str):
        command.upgrade(self.alembic_config, revision)

    def downgrade(self, revision: str):
        print("Downgrading...")
        command.downgrade(self.alembic_config, revision)

    def stamp(self, revision: str):
        command.stamp(self.alembic_config, revision)

    def reset_schema(self):
        self.connection.exec_driver_sql("DROP SCHEMA public CASCADE;")
        self.connection.exec_driver_sql("CREATE SCHEMA public;")
        self.connection.commit()

@pytest.fixture()
def alembic_runner(connection, alembic_config) -> AlembicRunner:
    alembic_config.attributes["connection"] = connection
    alembic_config.set_main_option(
        "sqlalchemy.url",
        get_postgres_connection_string()
    )
    runner = AlembicRunner(
        alembic_config=alembic_config,
        inspector=inspect(connection),
        metadata=MetaData(),
        connection=connection,
        session=scoped_session(sessionmaker(bind=connection)),
    )
    try:
        runner.downgrade("base")
    except Exception as e:
        runner.reset_schema()
        runner.stamp("base")
    print("Running test")
    yield runner
    print("Test complete")
    runner.session.close()
    try:
        runner.downgrade("base")
    except Exception as e:
        runner.reset_schema()
        runner.stamp("base")




def test_base(alembic_runner):
    table_names = alembic_runner.inspector.get_table_names()
    assert table_names == [
        'alembic_version',
    ]

    alembic_runner.upgrade("d11f07224d1f")

    # Reflect the updated database state
    alembic_runner.reflect()

    table_names = alembic_runner.inspector.get_table_names()
    assert table_names.sort() == [
        'batches',
        'logs',
        'missing',
        'urls',
        'duplicates',
        'alembic_version',
    ].sort()

def test_add_url_updated_at(alembic_runner):
    alembic_runner.upgrade("d11f07224d1f")

    columns = [col["name"] for col in alembic_runner.inspector.get_columns("urls")]
    assert "updated_at" not in columns

    alembic_runner.upgrade("a4750e7ff8e7")

    # # Reflect the updated database state
    alembic_runner.reflect()

    columns = [col["name"] for col in alembic_runner.inspector.get_columns("urls")]
    assert "updated_at" in columns
    #
    with alembic_runner.session() as session:
        pass
        # # Add a batch
        session.execute(text(
            """
            INSERT INTO
            BATCHES(strategy, user_id, status, total_url_count, original_url_count, duplicate_url_count)
            VALUES('test', 1, 'complete', 0, 0, 0);
            COMMIT;
            """
        ))

        result = session.execute(text(
            """
            INSERT INTO URLS(batch_id, url, url_metadata, outcome)
            VALUES(1, 'https://example.com', '{}', 'success')
            RETURNING id;
            """
        ))
        url_id = result.scalar()
    with alembic_runner.session() as session:
        updated_1 = session.execute(text(
            f"""SELECT UPDATED_AT FROM URLS WHERE ID = {url_id};"""
        )).scalar()

        session.execute(text(
            f"""
                UPDATE URLS SET url = 'https://example.com/new'
                WHERE id = {url_id};
                COMMIT;
            """
        ))

        result = session.execute(text(
            f"""
            SELECT url, updated_at FROM URLs WHERE id = {url_id}; 
            """
        )).fetchone()

        assert result[0] == "https://example.com/new"
        updated_2 = result[1]

        assert updated_1 < updated_2

    # Create a new URL entry





def test_add_url_metadata(alembic_runner):
    alembic_runner.upgrade("a4750e7ff8e7")

    columns = [col["name"] for col in alembic_runner.inspector.get_columns("urls")]
    assert "collector_metadata" not in columns
    assert "url_metadata" in columns

    alembic_runner.upgrade("86692fc1d862")

    # Reflect the updated database state
    alembic_runner.reflect()

    columns = [col["name"] for col in alembic_runner.inspector.get_columns("urls")]

    assert "collector_metadata" in columns
    assert "url_metadata" not in columns
    assert 'url_metadata' in alembic_runner.inspector.get_table_names()

    columns = [col["name"] for col in alembic_runner.inspector.get_columns("url_metadata")]
    assert columns.sort() == [
        'id',
        'url_id',
        'attribute',
        'value',
        'validation_status',
        'validation_source',
        'created_at',
        'updated_at',
    ].sort()



    # Test happy path

    # Test unique constraint

    # Test foreign key

    # Test each enum violation

def test_convert_batch_strategy_status_to_enum(alembic_runner):
    alembic_runner.upgrade("86692fc1d862")

    # Add batches with the following columns

    existing_strategy_strings = [
        "ckan",
        "muckrock_county_search",
        "auto_googler",
        "muckrock_all_search",
        "muckrock_simple_search",
        "common_crawler"
    ]
    existing_status_strings = [
        "complete",
        "error",
        "in-process",
        "aborted"
    ]
    d = {}
    with alembic_runner.session() as session:
        for strategy, status in product(existing_strategy_strings, existing_status_strings):
            # Execute inserts and store each ID
            id_ = session.execute(text(
                f"""
                INSERT INTO BATCHES 
                (strategy, user_id, status, total_url_count, original_url_count, duplicate_url_count) 
                VALUES(
                    '{strategy}',
                    1,
                    '{status}',
                    0,
                    0,
                    0
                )
                RETURNING ID;
                """
            )).scalar()
            d[id_] = [strategy, status]
            session.commit()

    alembic_runner.upgrade('db6d60feda7d')
    with alembic_runner.session() as session:
        # Assert all strategies and statuses remain the same
        for id_ in d.keys():
            strategy, status = d[id_]
            result = session.execute(text(
                f"""
                SELECT strategy, status FROM BATCHES WHERE id = {id_};
                """
            )).fetchone()
            assert result[0] == strategy
            assert result [1] == status


def test_convert_url_outcome_to_enum(alembic_runner):
    alembic_runner.upgrade('db6d60feda7d')
    existing_outcome_strings = [
        'pending',
        'submitted',
        'human_labeling',
        'rejected',
        'duplicate',
    ]
    d = {}
    with alembic_runner.session() as session:
        batch_id = session.execute(text(
            """INSERT INTO BATCHES
            (strategy, user_id, status, total_url_count, original_url_count, duplicate_url_count) 
            VALUES(
                    'ckan',
                    1,
                    'in-process',
                    0,
                    0,
                    0
                )
                RETURNING ID;
            """
        )).scalar()

        for outcome in existing_outcome_strings:
            id_ = session.execute(text(
                f"""
                INSERT INTO URLS 
                (batch_id, url, collector_metadata, outcome)
                VALUES (
                    '{batch_id}',
                    'https://example.com/{outcome}',
                    '{{}}',
                    '{outcome}'
                )
                RETURNING ID;
                """
            )).scalar()
            d[id_] = outcome
            session.commit()

    alembic_runner.upgrade('e27c5f8409a3')

    with alembic_runner.session() as session:
        for id_ in d.keys():
            outcome = d[id_]

            result = session.execute(text(
                f"""SELECT OUTCOME FROM URLS WHERE ID = {id_};"""
            )).scalar()

            assert result == outcome

def test_create_htmlcontent_and_rooturl_tables(alembic_runner):
    alembic_runner.upgrade('e27c5f8409a3')
    assert 'url_html_content' not in alembic_runner.inspector.get_table_names()
    assert 'root_urls' not in alembic_runner.inspector.get_table_names()

    alembic_runner.upgrade('9afd8a5633c9')
    alembic_runner.reflect()

    assert 'url_html_content' in alembic_runner.inspector.get_table_names()
    assert 'root_urls' in alembic_runner.inspector.get_table_names()