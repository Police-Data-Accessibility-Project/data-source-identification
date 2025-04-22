import os
import psycopg2
from psycopg2 import sql

from local_database.constants import LOCAL_DATA_SOURCES_DB_NAME, LOCAL_SOURCE_COLLECTOR_DB_NAME

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

def create_database_tables():
    conn = connect(LOCAL_DATA_SOURCES_DB_NAME)
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS test_table (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL
            )
        """)
        conn.commit()

def main():
    print("Creating databases...")
    create_database(LOCAL_DATA_SOURCES_DB_NAME)
    create_database(LOCAL_SOURCE_COLLECTOR_DB_NAME)

if __name__ == "__main__":
    main()
