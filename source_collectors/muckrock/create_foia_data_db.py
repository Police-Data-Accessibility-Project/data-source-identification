"""
create_foia_data_db.py

This script fetches data from the MuckRock FOIA API and stores it in a SQLite database.
Run this prior to companion script `search_foia_data_db.py`.

A successful run will output a SQLite database `foia_data.db` with one table `results`.
The database will contain all FOIA requests available through MuckRock.

Functions:
    - create_db()
    - fetch_page()
    - transform_page_data()
    - populate_db()
    - main()

Error Handling:
Errors encountered during API requests or database operations are logged to an `errors.log` file
and/or printed to the console.
"""

import json
import logging
import os
import time
from typing import List, Tuple, Dict, Any

from tqdm import tqdm

from source_collectors.muckrock.classes.SQLiteClient import SQLiteClientContextManager, SQLClientError
from source_collectors.muckrock.classes.muckrock_fetchers import FOIAFetcher
from source_collectors.muckrock.classes.muckrock_fetchers.MuckrockFetcher import MuckrockNoMoreDataError

logging.basicConfig(
    filename="errors.log", level=logging.ERROR, format="%(levelname)s: %(message)s"
)

# TODO: Why are we pulling every single FOIA request?

last_page_fetched = "last_page_fetched.txt"

NO_MORE_DATA = -1  # flag for program exit
JSON = Dict[str, Any]  # type alias


create_table_query = """
            CREATE TABLE IF NOT EXISTS results (
                id INTEGER PRIMARY KEY,
                title TEXT,
                slug TEXT,
                status TEXT,
                embargo_status TEXT,
                user INTEGER,
                username TEXT,
                agency INTEGER,
                datetime_submitted TEXT,
                date_due TEXT,
                days_until_due INTEGER,
                date_followup TEXT,
                datetime_done TEXT,
                datetime_updated TEXT,
                date_embargo TEXT,
                tracking_id TEXT,
                price TEXT,
                disable_autofollowups BOOLEAN,
                tags TEXT,
                communications TEXT,
                absolute_url TEXT
            )
            """


foia_insert_query = """
        INSERT INTO results (id, title, slug, status, embargo_status, user, username, agency,
                            datetime_submitted, date_due, days_until_due, date_followup,
                            datetime_done, datetime_updated, date_embargo, tracking_id,
                            price, disable_autofollowups, tags, communications, absolute_url)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """


def create_db() -> bool:
    """
    Creates foia_data.db SQLite database with one table named `results`.

    Returns:
        bool: True, if database is successfully created; False otherwise.

    Raises:
        sqlite3.Error: If the table creation operation fails,
        prints error and returns False.
    """
    with SQLiteClientContextManager("foia_data.db") as client:
        try:
            client.execute_query(create_table_query)
            return True
        except SQLClientError as e:
            print(f"SQLite error: {e}.")
            logging.error(f"Failed to create foia_data.db due to SQLite error: {e}")
            return False

def transform_page_data(data_to_transform: JSON) -> List[Tuple[Any, ...]]:
    """
    Transforms the data received from the MuckRock FOIA API
    into a structured format for insertion into a database with `populate_db()`.

    Transforms JSON input into a list of tuples,
    as well as serializes the nested `tags` and `communications` fields
    into JSON strings.

    Args:
        data_to_transform: The JSON data from the API response.
    Returns:
        A list of tuples, where each tuple contains the fields
        of a single FOIA request.
    """

    transformed_data = []

    for result in data_to_transform.get("results", []):
        result["tags"] = json.dumps(result.get("tags", []))
        result["communications"] = json.dumps(result.get("communications", []))

        transformed_data.append(
            (
                result["id"],
                result["title"],
                result["slug"],
                result["status"],
                result["embargo_status"],
                result["user"],
                result["username"],
                result["agency"],
                result["datetime_submitted"],
                result["date_due"],
                result["days_until_due"],
                result["date_followup"],
                result["datetime_done"],
                result["datetime_updated"],
                result["date_embargo"],
                result["tracking_id"],
                result["price"],
                result["disable_autofollowups"],
                result["tags"],
                result["communications"],
                result["absolute_url"],
            )
        )
    return transformed_data


def populate_db(transformed_data: List[Tuple[Any, ...]], page: int) -> None:
    """
    Populates foia_data.db SQLite database with the transfomed FOIA request data.

    Args:
        transformed_data (List[Tuple[Any, ...]]): A list of tuples, where each tuple contains the fields of a single FOIA request.
        page (int): The current page number for printing and logging errors.

    Returns:
        None

    Raises:
        sqlite3.Error: If the insertion operation fails, attempts to retry operation (max_retries = 2). If retries are
                       exhausted, logs error and exits.
    """
    with SQLiteClientContextManager("foia_data.db") as client:
        retries = 0
        max_retries = 2
        while retries < max_retries:
            try:
                client.execute_query(foia_insert_query, many=transformed_data)
                print("Successfully inserted data!")
                return
            except SQLClientError as e:
                print(f"{e}. Retrying...")
                retries += 1
                time.sleep(1)

        if retries == max_retries:
            report_max_retries_error(max_retries, page)


def report_max_retries_error(max_retries, page):
    print(
        f"Failed to insert data from page {page} after {
        max_retries} attempts. Skipping to next page."
    )
    logging.error(
        f"Failed to insert data from page {page} after {
        max_retries} attempts."
    )


def main() -> None:
    """
    Main entry point for create_foia_data_db.py.

    This function orchestrates the process of fetching
    FOIA requests data from the MuckRock FOIA API, transforming it,
    and storing it in a SQLite database.
    """

    if not os.path.exists("foia_data.db"):
        print("Creating foia_data.db...")
        success = create_db()
        if success == False:
            print("Failed to create foia_data.db")
            return

    start_page = get_start_page()
    fetcher = FOIAFetcher(
        start_page=start_page
    )

    with tqdm(initial=start_page, unit="page") as pbar:
        while True:

            # TODO: Build collector that does similar logic
            try:
                pbar.update()
                page_data = fetcher.fetch_next_page()
            except MuckrockNoMoreDataError:
                # Exit program because no more data exists
                break
            if page_data is None:
                continue
            transformed_data = transform_page_data(page_data)
            populate_db(transformed_data, fetcher.current_page)

            with open(last_page_fetched, mode="w") as file:
                file.write(str(fetcher.current_page))

    print("create_foia_data_db.py run finished")


def get_start_page():
    """
    Returns the page number to start fetching from.

    If the file `last_page_fetched` exists,
    reads the page number from the file and returns it + 1.
    Otherwise, returns 1.
    """
    if os.path.exists(last_page_fetched):
        with open(last_page_fetched, mode="r") as file:
            page = int(file.read()) + 1
    else:
        page = 1
    return page


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        print(
            "Check errors.log to review errors. Run create_foia_data_db.py again to continue"
        )
