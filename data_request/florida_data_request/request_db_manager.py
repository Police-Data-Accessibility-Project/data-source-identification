import os
import sqlite3

from data_request.florida_data_request.constants import DATABASE_NAME
from data_request.florida_data_request.query_constructor import QueryInfo
from util.google_searcher import GoogleSearchResult


def database_exists(db_name):
    # Get the current script's directory
    script_directory = os.path.abspath(os.path.dirname(__file__))

    # Construct the full path to the database file
    db_path = os.path.join(script_directory, db_name)

    # Check if the database file exists
    return os.path.exists(db_path)


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


def get_next_agency_without_misconduct_query():
    # Connect to SQLite database
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # SQL query to find the next row where search_misconduct is not 1
    query = '''
    SELECT 
        AGENCY_ID,
        AGENCY_NAME,
        STATE,
        ZIP 
    FROM agencies
    WHERE search_misconduct = 0
    ORDER BY agency_id ASC
    LIMIT 1;
    '''

    # Execute the query
    cursor.execute(query)

    # Fetch one result
    result = cursor.fetchone()

    # Close the connection
    conn.close()

    # Check if a result was found
    if result:
        print("Next agency found:", result)
        return QueryInfo(
            agency_id=result[0],
            agency_name=result[1],
            state=result[2],
            zip=result[3]
        )
    else:
        print("No agency found with search_misconduct not set to 1.")
        return None


def update_misconduct_state(agency_id: str):
    # Connect to SQLite database
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # SQL query to update search_misconduct for a specific agency
    update_query = '''
    UPDATE agencies
    SET search_misconduct = 1
    WHERE agency_id = ?;
    '''

    try:
        # Execute the query with the agency_id parameter
        cursor.execute(update_query, (agency_id,))

        # Commit the changes
        conn.commit()
        print("Updated agency_id:", agency_id, ". Rows affected:", cursor.rowcount)
    except sqlite3.Error as error:
        print("Error while updating search_misconduct for agency_id:", agency_id, error)
    finally:
        # Close the connection
        conn.close()
