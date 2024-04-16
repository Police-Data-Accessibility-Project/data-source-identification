import os
import sqlite3

from data_request.florida_data_request.constants import DATABASE_NAME
from data_request.florida_data_request.request_dataclasses import QueryInfo
from data_request.florida_data_request.request_enums import QueryType
from util.google_searcher import GoogleSearchResult


def database_exists(db_name):
    # Get the current script's directory
    script_directory = os.path.abspath(os.path.dirname(__file__))

    # Construct the full path to the database file
    db_path = os.path.join(script_directory, db_name)

    # Check if the database file exists
    return os.path.exists(db_path)


class SQLiteCursorContext:
    def __init__(self, db_path=DATABASE_NAME):
        self.db_path = db_path
        self.conn = None
        self.cursor = None

    def __enter__(self):
        # Connect to the database
        self.conn = sqlite3.connect(self.db_path)
        # Create a cursor object
        self.cursor = self.conn.cursor()
        # Return the cursor to be used within the with block
        return self.cursor

    def __exit__(self, exc_type, exc_value, traceback):
        # Close the cursor
        self.cursor.close()
        # Commit any changes and close the connection
        if exc_type is None:
            self.conn.commit()
        else:
            self.conn.rollback()
        self.conn.close()


def upload_query(agency_id: str, query_type: QueryType, query: str):
    insert_query = '''
        INSERT INTO search_queries (agency_id, search_type, query_text)
        VALUES (?, ?, ?);
    '''

    with SQLiteCursorContext() as cur:
        try:
            cur.execute(insert_query, (agency_id, query_type.value, query))
            row_id = cur.lastrowid
        except sqlite3.Error as error:
            print("Error while inserting into search_queries:", error)
    print(f"Query inserted into search_queries: {row_id}")


def create_queries():
    sql_script = """
    Insert into search_queries(agency_id, query_text, search_type)
    SELECT 
        agency_id,
        agency_name || ' ' || state || ' ' || zip || ' Misconduct Reports' as QUERY,
        'misconduct' as QUERY_TYPE
    FROM agencies a
    UNION
    SELECT 
        agency_id,
        agency_name || ' ' || state || ' ' || zip || ' Liability Insurance' as QUERY,
        'insurance' as QUERY_TYPE
    FROM agencies a
    """
    with SQLiteCursorContext() as cur:
        cur.execute(sql_script)
    print("Queries inserted into search_queries")


def table_exists(table_name: str) -> bool:
    """
    Checks if the given table exists in the database
    Args:
        table_name: str, name of the table to check the existence of
    Returns: True if table exists, False otherwise
    """
    with SQLiteCursorContext() as cur:
        sql_script = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
        cur.execute(sql_script, (table_name,))
        result = cur.fetchone()
        return result is not None


def create_search_queries_table():
    create_table_query = """
    CREATE TABLE IF NOT EXISTS search_queries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        agency_id INTEGER,
        search_type TEXT CHECK(search_type IN ('misconduct', 'insurance')),
        query_text TEXT UNIQUE,
        FOREIGN KEY (agency_id) REFERENCES agencies(id)
    );
    """

    with SQLiteCursorContext() as cur:
        try:
            cur.execute(create_table_query)
        except sqlite3.Error as error:
            print("Error occurred:", error)
    print("Table 'search_queries' created successfully.")


def create_database_and_tables(db_name):
    # Connect to SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    create_table_agencies = """
    CREATE TABLE IF NOT EXISTS agencies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        agency_name TEXT NOT NULL,
        agency_id INTEGER NOT NULL,
        city TEXT,
        state TEXT,
        zip TEXT,
        county TEXT,
        search_misconduct BOOLEAN,
        search_insurance BOOLEAN
    );
    """

    # SQL to create 'search_results' table
    create_table_search_results = """
    CREATE TABLE IF NOT EXISTS search_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        agency_id INTEGER NOT NULL,
        search_type TEXT NOT NULL,
        title TEXT NOT NULL,
        url TEXT NOT NULL,
        snippet TEXT,
        FOREIGN KEY (agency_id) REFERENCES agencies (id)
    );
    """

    # Execute the SQL commands to create the tables
    cursor.execute(create_table_agencies)
    cursor.execute(create_table_search_results)

    # Commit the changes
    conn.commit()

    # Close the connection
    conn.close()

    print("Database created and tables added successfully.")


def upload_search_results(results: list[GoogleSearchResult], search_type: str, agency_id: str):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    insert_query = '''
        INSERT INTO search_results (agency_id, search_type, title, url, snippet)
        VALUES (?, ?, ?, ?, ?);
        '''

    for result in results:
        # Data tuple to insert
        data = (agency_id, search_type, result.title, result.url, result.snippet)

        try:
            # Execute the query
            cursor.execute(insert_query, data)

            # Commit the changes
            conn.commit()
            print("Insert successful, ID of new record:", cursor.lastrowid)
        except sqlite3.Error as error:
            print("Error while inserting into search_results:", error)
    # Close the connection
    conn.close()


def get_next_query() -> QueryInfo:
    sql_text = """
    SELECT 
	a.AGENCY_ID, 
	s.query_text,
	s.search_type
    from 
        agencies a,
        search_queries s
    where s.agency_id = a.agency_id
    and a.search_misconduct = 0
    and s.search_type = 'misconduct'
    UNION
    SELECT 
        a.agency_id,
        s.query_text,
        s.search_type
    from 
        agencies a,
        search_queries s
    where s.agency_id = a.agency_id
    and a.search_insurance = 0
    and s.search_type = 'insurance'
    LIMIT 1
    """
    with SQLiteCursorContext() as cur:
        cur.execute(sql_text)
        row = cur.fetchone()
        if row[2] == "misconduct":
            query_type = QueryType.MISCONDUCT
        elif row[2] == "insurance":
            query_type = QueryType.INSURANCE
        else:
            raise ValueError("Invalid query type")
        return QueryInfo(
            agency_id=row[0],
            query_text=row[1],
            query_type=query_type
        )


def update_query_search_status(agency_id, query_type: QueryType):
    if query_type == QueryType.INSURANCE:
        set_column = "search_insurance"
    elif query_type == QueryType.MISCONDUCT:
        set_column = "search_misconduct"
    else:
        raise ValueError(f"Invalid query type: {query_type}")
    update_query = f"""
        UPDATE agencies
        SET {set_column} = 1
        WHERE agency_id = ?
    """
    with SQLiteCursorContext() as cur:
        try:
            cur.execute(update_query, (agency_id,))
            print("Updated agency_id:", agency_id, ". Rows affected:", cur.rowcount)
        except sqlite3.Error as error:
            print("Error while updating search_misconduct for agency_id:", agency_id, error)
