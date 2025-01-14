import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine

from collector_db.helper_functions import get_postgres_connection_string
from collector_db.models import Base

@pytest.fixture(autouse=True, scope="session")
def setup_and_teardown():
    conn = get_postgres_connection_string()
    engine = create_engine(conn)
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.attributes["connection"] = engine.connect()
    alembic_cfg.set_main_option(
        "sqlalchemy.url",
        get_postgres_connection_string()
    )
    command.upgrade(alembic_cfg, "head")
    engine.dispose()
    yield

@pytest.fixture
def wipe_database():
    """
    Wipe all data from database
    Returns:

    """
    conn = get_postgres_connection_string()
    engine = create_engine(conn)
    with engine.connect() as connection:
        for table in reversed(Base.metadata.sorted_tables):
            connection.execute(table.delete())
        connection.commit()