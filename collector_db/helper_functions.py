import os

import dotenv


def get_postgres_connection_string():
    dotenv.load_dotenv()
    username = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    host = os.getenv("POSTGRES_HOST")
    port = os.getenv("POSTGRES_PORT")
    database = os.getenv("POSTGRES_DB")
    return f"postgresql://{username}:{password}@{host}:{port}/{database}"