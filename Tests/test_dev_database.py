from pathlib import Path

import pytest
from pytest_postgresql import factories
from pytest_postgresql.janitor import DatabaseJanitor

from tests.database.ProdSchemaManager import ProdSchemaManager

"""
This requires a postgresql docker container set up and listening on port 5432"
The setup should mirror what is in start_database_setup.sh
"""
#
prod_schema_manager = ProdSchemaManager()
postgresql_in_docker = factories.postgresql_noproc(
    port="5432",
    user="myuser",
    password="mypassword",
    load=[prod_schema_manager.schema_path]
)
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
