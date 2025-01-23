"""
search_foia_data_db.py

This script provides search functionality for the `foia_data.db` SQLite database. The search looks in `title`s and
`tags` of FOIA requests that match an input string provided by the user.
Run this after companion script `create_foia_data_db.py`.

A successful run will output a JSON file containing entries matching the search string.

Functions:
    - parser_init()
    - search_foia_db()
    - parse_communications_column()
    - generate_json()
    - main()

Error Handling:
Errors encountered during database operations, JSON parsing, or file writing are printed to the console.
"""

import argparse
import json
from typing import Union, List, Dict

import pandas as pd

from source_collectors.muckrock.classes.FOIADBSearcher import FOIADBSearcher


def parser_init() -> argparse.ArgumentParser:
    """
    Initializes the argument parser for search_foia_data_db.py.

    Returns:
        argparse.ArgumentParser: The configured argument parser.
    """

    parser = argparse.ArgumentParser(
        description="Search foia_data.db and generate a JSON file of resulting matches"
    )
    parser.add_argument(
        "--search_for",
        type=str,
        required=True,
        metavar="<search_string>",
        help="Provide a string to search foia_data.db",
    )

    return parser


def search_foia_db(search_string: str) -> Union[pd.DataFrame, None]:
    searcher = FOIADBSearcher()
    return searcher.search(search_string)


def parse_communications_column(communications) -> List[Dict]:
    """
    Parses a communications column value, decoding it from JSON format.

    Args:
        communications : The input value to be parsed, which can be a JSON string or NaN.

    Returns:
        list (List[Dict]): A list containing the parsed JSON data. If the input is NaN (missing values) or
            there is a JSON decoding error, an empty list is returned.

    Raises:
        json.JSONDecodeError: If deserialization fails, prints error and returns empty list.
    """

    if pd.isna(communications):
        return []
    try:
        return json.loads(communications)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return []


def generate_json(df: pd.DataFrame, search_string: str) -> None:
    """
    Generates a JSON file from a pandas DataFrame.

    Args:
        df (pandas.DataFrame): The DataFrame containing the data to be written to the JSON file.

        search_string (str): The string used to name the output JSON file. Spaces in the string
            are replaced with underscores.

    Returns:
        None

    Raises:
        Exception: If writing to JSON file operation fails, prints error and returns.
    """

    output_json = f"{search_string.replace(' ', '_')}.json"

    try:
        df.to_json(output_json, orient="records", indent=4)
        print(f'Matching entries written to "{output_json}"')
    except Exception as e:
        print(f"An error occurred while writing JSON: {e}")


def main() -> None:
    """
    Function to search the foia_data.db database for entries matching a specified search string.

    Command Line Args:
        --search_for (str): A string to search for in the `title` and `tags` fields of FOIA requests.
    """

    parser = parser_init()
    args = parser.parse_args()
    search_string = args.search_for

    df = search_foia_db(search_string)
    if df is None:
        return
    update_communications_column(df)

    announce_matching_entries(df, search_string)

    generate_json(df, search_string)


def announce_matching_entries(df, search_string):
    print(
        f'Found {df.shape[0]} matching entries containing "{search_string}" in the title or tags'
    )


def update_communications_column(df):
    if not df["communications"].empty:
        df["communications"] = df["communications"].apply(parse_communications_column)


if __name__ == "__main__":
    main()
