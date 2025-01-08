import time
from dataclasses import dataclass

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, Inspector, inspect, MetaData, Connection, Engine
from sqlalchemy.orm import Session, sessionmaker, scoped_session

from collector_db.helper_functions import get_postgres_connection_string
from collector_db.models import Base, URL, Batch


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
        command.downgrade(self.alembic_config, revision)

    def stamp(self, revision: str):
        command.stamp(self.alembic_config, revision)

@pytest.fixture()
def alembic_runner(connection, alembic_config) -> AlembicRunner:
    alembic_config.attributes["connection"] = connection
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
        # Drop tables and stamp base revision
        Base.metadata.drop_all(connection)
        runner.stamp("base")
    yield runner




def test_base(alembic_runner):
    table_names = alembic_runner.inspector.get_table_names()
    assert table_names == [
        'alembic_version',
    ]

    alembic_runner.upgrade("d11f07224d1f")

    # Reflect the updated database state
    alembic_runner.reflect()

    table_names = alembic_runner.inspector.get_table_names()
    assert table_names == [
        'batches',
        'logs',
        'missing',
        'urls',
        'duplicates',
        'alembic_version',
    ]

def test_add_url_updated_at(alembic_runner):
    alembic_runner.upgrade("d11f07224d1f")

    columns = [col["name"] for col in alembic_runner.inspector.get_columns("urls")]
    assert "updated_at" not in columns

    alembic_runner.upgrade("a4750e7ff8e7")

    # Reflect the updated database state
    alembic_runner.reflect()

    columns = [col["name"] for col in alembic_runner.inspector.get_columns("urls")]
    assert "updated_at" in columns

    with alembic_runner.session() as session:
        # Add a batch
        batch = Batch(
            strategy="test",
            user_id=1,
            status="complete",
            total_url_count=0,
            original_url_count=0,
            duplicate_url_count=0
        )
        session.add(batch)

        # Add a url
        url = URL(batch_id=1, url="https://example.com", url_metadata={}, outcome="success")
        session.add(url)
        session.flush()
        session.commit()

    # alembic_runner.session.refresh()



    with alembic_runner.session() as session:
        url = session.query(URL).first()
        assert url.url == "https://example.com"
        updated_1 = url.updated_at
        print(updated_1)

        time.sleep(1)
        # Update the url
        url.url = "https://example.com/new"
        session.commit()
        url = session.query(URL).first()
        assert url.url == "https://example.com/new"
        updated_2 = url.updated_at

        # assert updated_1 < updated_2

    # Create a new URL entry

