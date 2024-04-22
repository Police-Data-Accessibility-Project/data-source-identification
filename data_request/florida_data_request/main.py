

"""
Types of queries to run:
1. Police department misconduct
2. Police department insurance coverage
"""
import dotenv

from data_request.florida_data_request.constants import DATABASE_NAME

from data_request.florida_data_request.request_dataclasses import QueryInfo
from data_request.florida_data_request.request_db_manager import database_exists, create_database_and_tables, \
    upload_search_results, create_queries, get_next_query, update_query_search_status
from util.google_searcher import GoogleSearcher, GoogleSearchResult, QuotaExceededError
from util.miscellaneous_functions import get_project_root

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


def run_google_search(query) -> list[GoogleSearchResult]:
    root_directory = get_project_root()
    env_path = root_directory / ".env"
    assert env_path.exists(), f"Environment file at {env_path} does not exist"
    dotenv.load_dotenv(env_path)
    google_searcher = GoogleSearcher(
        os.getenv("CUSTOM_SEARCH_API_KEY"),
        os.getenv("CUSTOM_SEARCH_ENGINE_ID")
    )
    return google_searcher.search(query)

def run_google_search_loop():
    while True:
        query: QueryInfo = get_next_query()
        try:
            results = run_google_search(query.query_text)
        except QuotaExceededError:
            print("Quota Exceeded for the day")
            return
        upload_search_results(results, query.query_id)


def create_database_and_queries():
    if not database_exists(DATABASE_NAME):
        create_database_and_tables()
        load_data_from_csv(
            csv_filename="police_departments.csv",
            db_name=DATABASE_NAME
        )
        create_queries()
    else:
        print("Database already exists")

def main():
    create_database_and_queries()
    run_google_search_loop()

"""
TODO: Re-review email
    Try searching for 'liability (insurance OR coverage) of MUNICIPALITY STATE' (no police agency mentioned
    Try google searching for annual budget reports for each municipality (or finding where they might be aggregated)
        - It's possible that these don't mention directly the insurance, and simply state 'insurance'

"""

if __name__ == "__main__":
    main()