import os

import dotenv


def get_postgres_connection_string(is_async = False):
    dotenv.load_dotenv()
    username = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    host = os.getenv("POSTGRES_HOST")
    port = os.getenv("POSTGRES_PORT")
    database = os.getenv("POSTGRES_DB")
    driver = "postgresql"
    if is_async:
        driver += "+asyncpg"
    return f"{driver}://{username}:{password}@{host}:{port}/{database}"