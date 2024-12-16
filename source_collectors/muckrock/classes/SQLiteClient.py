import logging
import sqlite3


class SQLClientError(Exception):
    pass


class SQLiteClient:

    def __init__(self, db_path: str) -> None:
        self.conn = sqlite3.connect(db_path)

    def execute_query(self, query: str, many=None):

        try:
            if many is not None:
                self.conn.executemany(query, many)
            else:
                self.conn.execute(query)
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"SQLite error: {e}")
            error_msg = f"Failed to execute query due to SQLite error: {e}"
            logging.error(error_msg)
            self.conn.rollback()
            raise SQLClientError(error_msg)

class SQLiteClientContextManager:

    def __init__(self, db_path: str) -> None:
        self.client = SQLiteClient(db_path)

    def __enter__(self):
        return self.client

    def __exit__(self, exc_type, exc_value, traceback):
        self.client.conn.close()