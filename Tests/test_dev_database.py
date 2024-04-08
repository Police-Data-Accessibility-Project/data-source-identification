import os

from pytest_postgresql import factories
from dotenv import load_dotenv

from tests.database.ProdSchemaManager import ProdSchemaManager

"""
This requires a postgresql docker container set up and listening on port 5432"
The setup should mirror what is in start_database_setup.sh
"""


def create_postgresql_factory():
    load_dotenv()

    host = os.getenv("TEST_DATABASE_HOST")
    if host is None:
        raise ValueError("TEST_DATABASE_HOST environment variable is not set.")
    prod_schema_manager = ProdSchemaManager()
    return factories.postgresql_noproc(
        port="5432",
        user="myuser",
        password="mypassword",
        host=host,
        load=[prod_schema_manager.schema_path]
    )


postgresql_in_docker = create_postgresql_factory()
postgresql = factories.postgresql("postgresql_in_docker")


def test_get_agencies_without_homepage_urls(postgresql):
    cur = postgresql.cursor()
    sql_script = """
    SELECT tablename
    FROM pg_catalog.pg_tables
    WHERE schemaname != 'pg_catalog' AND schemaname != 'information_schema';
    """
    cur.execute(sql_script)
    results = cur.fetchall()
    print("results: ", results)
