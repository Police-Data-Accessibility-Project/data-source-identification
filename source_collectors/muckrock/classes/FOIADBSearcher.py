import os
import sqlite3

import pandas as pd

from source_collectors.muckrock.constants import FOIA_DATA_DB

check_results_table_query = """
                SELECT name FROM sqlite_master
                WHERE (type = 'table')
                AND (name = 'results')
                """

search_foia_query = """
        SELECT * FROM results
        WHERE (title LIKE ? OR tags LIKE ?)
        AND (status = 'done')
        """


class FOIADBSearcher:

    def __init__(self, db_path = FOIA_DATA_DB):
        self.db_path = db_path
        if not os.path.exists(self.db_path):
            raise FileNotFoundError("foia_data.db does not exist.\nRun create_foia_data_db.py first to create and populate it.")


    def search(self, search_string: str) -> pd.DataFrame | None:
        """
        Searches the foia_data.db database for FOIA request entries matching the provided search string.

        Args:
            search_string (str): The string to search for in the `title` and `tags` of the `results` table.

        Returns:
            Union[pandas.DataFrame, None]:
                - pandas.DataFrame: A DataFrame containing the matching entries from the database.
                - None: If an error occurs during the database operation.

        Raises:
            sqlite3.Error: If any database operation fails, prints error and returns None.
            Exception: If any unexpected error occurs, prints error and returns None.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                results_table = pd.read_sql_query(check_results_table_query, conn)
                if results_table.empty:
                    print("The `results` table does not exist in the database.")
                    return None

                df = pd.read_sql_query(
                    sql=search_foia_query,
                    con=conn,
                    params=[f"%{search_string}%", f"%{search_string}%"]
                )

        except sqlite3.Error as e:
            print(f"Sqlite error: {e}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None

        return df