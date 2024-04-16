from dotenv import load_dotenv
import psycopg


class DBManager:
    """
    Manages access to PostgreSQL database.
    """

    def __init__(self, database_url: str):
        self.conn = psycopg.connect(database_url)
        self.cursor = self.conn.cursor()

    def __del__(self):
        self.conn.close()

    def execute(self, query, params=None) -> list:
        self.cursor.execute(query, params)
        self.conn.commit()
        return self.cursor.fetchall()

    def executemany(self, query, params=None) -> list:
        self.cursor.executemany(query, params)
        self.conn.commit()
        try:
            return self.cursor.fetchall()
        except psycopg.ProgrammingError:
            return []

    def fetchall(self):
        return self.cursor.fetchall()

    def fetchone(self):
        return self.cursor.fetchone()

    def fetchmany(self, size):
        return self.cursor.fetchmany(size)

    def close(self):
        self.conn.close()
