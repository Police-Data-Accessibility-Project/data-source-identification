"""
A straightforward standalone script for downloading data from MuckRock
and searching for it with a specific search string.
"""

import requests
import json

# Define the base API endpoint
base_url = "https://www.muckrock.com/api_v1/foia/"

def dump_list(all_results: list[dict], search_string: str) -> None:
    """
    Dumps a list of dictionaries into a JSON file.
    """
    json_out_file = search_string.replace(" ", "_") + ".json"
    with open(json_out_file, "w") as json_file:
        json.dump(all_results, json_file)

    print(f"List dumped into {json_out_file}")

def search_for_foia(search_string: str, per_page: int = 100, max_count: int = 20) -> list[dict]:
    """
    Search for FOIA data based on a search string.
    :param search_string: The search string to use.
    :param per_page: The number of results to retrieve per page.
    :param max_count: The maximum number of results to retrieve. Search stops once this number is reached or exceeded.
    """
    page = 1
    all_results = []

    while True:

        # Make the GET request with the search string as a query parameter
        response = requests.get(
            base_url, params={"page": page, "page_size": per_page, "format": "json"}
        )

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the JSON response
            data = response.json()

            if not data["results"]:
                break


            # Filter results according to whether the search string is in the title
            filtered_results = [
                item
                for item in data["results"]
                if search_string.lower() in item["title"].lower()
            ]

            all_results.extend(filtered_results)

            if len(filtered_results) > 0:
                num_results = len(filtered_results)
                print(f"found {num_results} more matching result(s)...")

            if len(all_results) >= max_count:
                print(f"max count ({max_count}) reached... exiting")
                break

            page += 1

        else:
            print(f"Error: {response.status_code}")
            break
    return all_results

if __name__ == "__main__":
    search_string = "use of force"
    all_results = search_for_foia(search_string)
    dump_list(all_results, search_string)
