
import psycopg2


class DBManager:
    """
    Manages access to PostgreSQL database.
    """

    def __init__(self, db_name, user, password, host, port):
        self.conn = psycopg2.connect(
            dbname=db_name,
            user=user,
            password=password,
            host=host,
            port=port
        )
        self.cursor = self.conn.cursor()

    def __del__(self):
        self.conn.close()

    def execute(self, query, params=None):
        self.cursor.execute(query, params)
        self.conn.commit()
        return self.cursor.fetchall()

    def fetchall(self):
        return self.cursor.fetchall()

    def fetchone(self):
        return self.cursor.fetchone()

    def fetchmany(self, size):
        return self.cursor.fetchmany(size)

    def close(self):
        self.conn.close()
