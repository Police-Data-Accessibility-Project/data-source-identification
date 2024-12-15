"""
A straightforward standalone script for downloading data from MuckRock
and searching for it with a specific search string.
"""

import requests
import json

from source_collectors.muckrock.FOIAFetcher import FOIAFetcher
from source_collectors.muckrock.utils import save_json_file

# Define the base API endpoint
base_url = "https://www.muckrock.com/api_v1/foia/"

def dump_list(all_results: list[dict], search_string: str) -> None:
    """
    Dumps a list of dictionaries into a JSON file.
    """
    json_out_file = search_string.replace(" ", "_") + ".json"
    save_json_file(file_path=json_out_file, data=all_results)
    print(f"List dumped into {json_out_file}")

def search_for_foia(search_string: str, per_page: int = 100, max_count: int = 20) -> list[dict]:
    """
    Search for FOIA data based on a search string.
    :param search_string: The search string to use.
    :param per_page: The number of results to retrieve per page.
    :param max_count: The maximum number of results to retrieve. Search stops once this number is reached or exceeded.
    """
    fetcher = FOIAFetcher(per_page=per_page)
    all_results = []

    while True:

        data = fetcher.fetch_next_page()

        if data is None:
            break

        if not data["results"]:
            break


        # Filter results according to whether the search string is in the title
        filtered_results = [
            item
            for item in data["results"]
            if search_string.lower() in item["title"].lower()
        ]

        all_results.extend(filtered_results)

        num_results = len(filtered_results)
        if num_results > 0:
            print(f"found {num_results} more matching result(s)...")

        if len(all_results) >= max_count:
            print(f"max count ({max_count}) reached... exiting")
            break


    return all_results

if __name__ == "__main__":
    search_string = "use of force"
    all_results = search_for_foia(search_string)
    dump_list(all_results, search_string)
