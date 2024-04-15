

"""
Types of queries to run:
1. Police department misconduct
2. Police department insurance coverage
"""

DATABASE_NAME = "florida_data_request.db"

"""
Create SQLite database to store results. 
Initially load all csv entries.

Table: agencies
Columns:
    id
    agency_name
    agency_id
    city
    state 
    zip
    county
    search_misconduct (bool)
    search_insurance (bool)
    
Table: search_results
Columns:
    id:
    agency_id:
    search_type (misconduct or insurance)
    title
    url
    snippet
"""

import os
import sqlite3
import csv
from dataclasses import dataclass

@dataclass
class QueryInfo:
    agency_id: str
    agency_name: str
    state: str
    zip: str



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

    # Create a cursor object using the cursor() method
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


def load_data_from_csv(csv_filename, db_name):
    # Determine the directory of the current script
    script_directory = os.path.abspath(os.path.dirname(__file__))

    # Construct the full path to the CSV file
    csv_file_path = os.path.join(script_directory, csv_filename)

    # Connect to SQLite database
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Open the CSV file and read data
    with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter='\t')

        # Prepare an SQL query for inserting data into the agencies table
        insert_query = '''
        INSERT INTO agencies (agency_name, agency_id, city, state, zip, county, search_misconduct, search_insurance)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        '''

        # Read each row in the CSV file and insert it into the database
        for row in reader:
            cursor.execute(insert_query, (
                row['AGENCYNAME'],
                row['AGENCYID'],
                row['CITY'],
                row['STATE'],
                row['ZIP'],
                row['COUNTY'],
                0,  # search_misconduct set to false
                0  # search_insurance set to false
            ))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()
    print("Data loaded successfully into the agencies table.")

def get_next_agency_without_misconduct_query()
    # Connect to SQLite database
    conn = sqlite3.connect('example.db')
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

def build_misconduct_query(query_info: QueryInfo) -> str:
    return f"{query_info.agency_name} {query_info.state} {query_info.zip} Misconduct Reports"

def main():
    # Run this loop only once at a time, for testing.

    if not database_exists(DATABASE_NAME):
        create_database_and_tables(DATABASE_NAME)
        load_data_from_csv(
            csv_filename="police_departments.csv",
            db_name=DATABASE_NAME
        )
    else:
        print("Database already exists")

    # Get all searches in order of agency id (start with misconduct, move to insurance)
    query_info = get_next_agency_without_misconduct_query()
    # For all whose status is not yet searched, run search


    # If search is completed, even if no results, mark appropriate value in agencies table



if __name__ == "__main__":
    main()