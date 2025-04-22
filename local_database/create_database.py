import argparse
import os
import subprocess

import psycopg2
from psycopg2 import sql

from local_database.DockerInfos import get_data_sources_data_dumper_info
from local_database.classes.DockerManager import DockerManager
from local_database.constants import LOCAL_DATA_SOURCES_DB_NAME, LOCAL_SOURCE_COLLECTOR_DB_NAME, RESTORE_SH_DOCKER_PATH

# Defaults (can be overridden via environment variables)
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "host.docker.internal")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
POSTGRES_USER = os.getenv("POSTGRES_USER", "test_source_collector_user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "HanviliciousHamiltonHilltops")


# Connect to the default 'postgres' database to create other databases
def connect(database="postgres", autocommit=True):
    conn = psycopg2.connect(
        dbname=database,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        host=POSTGRES_HOST,
        port=POSTGRES_PORT
    )
    if autocommit:
        conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    return conn

def create_database(db_name):
    conn = connect("postgres")
    with conn.cursor() as cur:
        cur.execute(sql.SQL("""
            SELECT pg_terminate_backend(pid)
            FROM pg_stat_activity
            WHERE datname = %s AND pid <> pg_backend_pid()
        """), [db_name])

        # Drop the database if it exists
        cur.execute(sql.SQL("DROP DATABASE IF EXISTS {}").format(sql.Identifier(db_name)))
        print(f"🗑️  Dropped existing database: {db_name}")

        try:
            cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name)))
            print(f"✅ Created database: {db_name}")
        except psycopg2.errors.DuplicateDatabase:
            print(f"⚠️  Database {db_name} already exists")
        except Exception as e:
            print(f"❌ Failed to create {db_name}: {e}")

def main():
    print("Creating databases...")
    create_database(LOCAL_DATA_SOURCES_DB_NAME)
    create_database(LOCAL_SOURCE_COLLECTOR_DB_NAME)

if __name__ == "__main__":
    main()
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--use-shell",
        action="store_true",
        help="Use shell to run restore script"
    )

    args = parser.parse_args()

    if args.use_shell:
        subprocess.run(
            [
                "bash",
                "-c",
                RESTORE_SH_DOCKER_PATH
            ],
            env={
                "RESTORE_HOST": POSTGRES_HOST,
                "RESTORE_USER": POSTGRES_USER,
                "RESTORE_PORT": str(POSTGRES_PORT),
                "RESTORE_DB_NAME": LOCAL_DATA_SOURCES_DB_NAME,
                "RESTORE_PASSWORD": POSTGRES_PASSWORD
            }
        )
        os.system(RESTORE_SH_DOCKER_PATH)
        exit(0)

    docker_manager = DockerManager()
    data_sources_docker_info = get_data_sources_data_dumper_info()
    container = docker_manager.run_container(
        data_sources_docker_info,
        force_rebuild=True
    )
    try:
        container.run_command(RESTORE_SH_DOCKER_PATH)
    finally:
        container.stop()

