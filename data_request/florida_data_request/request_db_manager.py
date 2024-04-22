import os
import sqlite3

from data_request.florida_data_request.constants import DATABASE_NAME
from data_request.florida_data_request.request_dataclasses import QueryInfo, QueryAndSearchResults, SearchResult, \
    MostRelevantResult
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

def create_queries():
    sql_script = """
    Insert into search_queries(agency_id, query_text, search_type)
    SELECT 
        a.id,
        a.agency_name || ' ' || a.state || ' ' || a.zip || ' Official ("Misconduct Report" OR "internal investigation") ext:PDF' as QUERY,
        'misconduct' as QUERY_TYPE
    FROM 
        agencies a
    UNION
    SELECT 
        a.id,
        a.agency_name || ' ' || a.state || ' ' || a.zip || ' ("liability insurance policy" OR "insurance coverage details") ext:PDF' as QUERY,
        'insurance' as QUERY_TYPE
    FROM 
        agencies a
    """
    with SQLiteCursorContext() as cur:
        cur.execute(sql_script)
    print("Queries inserted into search_queries")

def get_next_query_and_results() -> QueryAndSearchResults:
    sql_text = """
    SELECT 
	sq.id query_id,
	sq.query_text,
	sr.id result_id,
	sr.title,
	sr.url,
	sr.snippet
FROM
	search_results sr,
	search_queries sq
WHERE 
	sr.query_id = sq.id
	and (query_id, query_text) IN (
        SELECT id query_id, query_text
        FROM search_queries sq1
        WHERE query_id not in
        (
            SELECT query_id
            from relevant_search_gpt rs
        ) 
        LIMIT 1
	)
ORDER BY query_id
LIMIT 10
    """
    with SQLiteCursorContext() as cur:
        cur.execute(sql_text)
        results = cur.fetchall()
        qasr = QueryAndSearchResults(
            query_id=results[0][0],
            query_text=results[0][1],
            search_results=[]
        )
        for row in results:
            assert qasr.query_id == row[0]
            qasr.search_results.append(
                SearchResult(
                    result_id=row[2],
                    title=row[3],
                    url=row[4],
                    snippet=row[5]
                )
            )

        return qasr

def create_database_and_tables():

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

    create_table_query = """
    CREATE TABLE IF NOT EXISTS search_queries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        agency_id INTEGER,
        search_type TEXT CHECK(search_type IN ('misconduct', 'insurance')),
        query_text TEXT UNIQUE,
        FOREIGN KEY (agency_id) REFERENCES agencies(id)
    );
    """

    create_table_search_results = """
    CREATE TABLE IF NOT EXISTS search_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        query_id INTEGER NOT NULL,
        title TEXT,
        url TEXT,
        snippet TEXT,
        FOREIGN KEY (query_id) REFERENCES search_queries (id)
    );
    """

    create_table_relevant_search_gpt = """
        CREATE TABLE relevant_search_gpt (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        query_id INTEGER NOT NULL,
        search_id INTEGER,
        rationale TEXT,
        FOREIGN KEY (query_id) REFERENCES search_queries(id),
        FOREIGN KEY (search_id) REFERENCES search_results(id)
    );
        """

    with SQLiteCursorContext() as cur:
        # Execute the SQL commands to create the tables
        for sql_query in (create_table_agencies, create_table_query, create_table_search_results, create_table_relevant_search_gpt ):
            cur.execute(sql_query)

    print("Database created and tables added successfully.")


def upload_search_results(results: list[GoogleSearchResult], query_id: int):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # If results are empty, create an empty search result so that it's not looked up again
    if not results:
        results = [GoogleSearchResult(
            title=None,
            url=None,
            snippet=None
        )]

    insert_query = '''
        INSERT INTO search_results (query_id, title, url, snippet)
        VALUES (?, ?, ?, ?);
        '''

    print(f"Inserting results for query {query_id}")
    for result in results:
        # Data tuple to insert
        data = (query_id, result.title, result.url, result.snippet)

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
    q.id, 
    q.query_text
    from 
        search_queries q
    WHERE q.id NOT IN 
        (SELECT s.query_id
        FROM search_results s)
        LIMIT 1
    """
    with SQLiteCursorContext() as cur:
        cur.execute(sql_text)
        row = cur.fetchone()
        return QueryInfo(
            query_id=row[0],
            query_text=row[1],
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

def upload_most_relevant_result(most_relevant_result: MostRelevantResult, query_id: int):
    sql_text = """
    INSERT INTO relevant_search_gpt(query_id, search_id, rationale)
    VALUES(?, ?, ?)
    """
    if most_relevant_result.result_id == -1:
        result_id = None
    else:
        result_id = most_relevant_result.result_id
    with SQLiteCursorContext() as cur:
        try:
            cur.execute(sql_text, (query_id, result_id, most_relevant_result.rationale))
            print(f"Most relevant result for query {query_id} inserted successfully.")
        except sqlite3.Error as error:
            print("Error while inserting into relevant_search_gpt:", error)

def get_completed_queries_and_rationale():
    sql_text = """
    SELECT
	sq.query_text,
	sr.title,
	sr.url,
	sr.snippet,
	rs.rationale
FROM 
	search_results sr,
	search_queries sq
	LEFT JOIN relevant_search_gpt rs
	ON rs.search_id = sr.id
WHERE sr.query_id = sq.id
and sq.id in (
	SELECT rs.query_id
	FROM relevant_search_gpt rs
	WHERE rs.query_id = sq.id
)
    """
    with SQLiteCursorContext() as cur:
        cur.execute(sql_text)
        results = cur.fetchall()
        raise NotImplementedError("Not sure what format to put this info in.")

