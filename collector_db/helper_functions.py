import os

import dotenv


def get_postgres_connection_string(with_async: bool = True) -> str:
    dotenv.load_dotenv()
    username = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    host = os.getenv("POSTGRES_HOST")
    port = os.getenv("POSTGRES_PORT")
    database = os.getenv("POSTGRES_DB")
    if with_async:
        return f"postgresql+asyncpg://{username}:{password}@{host}:{port}/{database}"
    else:
        return f"postgresql://{username}:{password}@{host}:{port}/{database}"
