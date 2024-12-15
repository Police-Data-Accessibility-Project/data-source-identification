"""
***DEPRECATED***

download_muckrock_foia.py

This script fetches data from the MuckRock FOIA API and stores the results in a JSON file.

"""


# TODO: Logic redundant with `muck_get.py`. Generalize

import requests
import csv
import time
import json

from source_collectors.muckrock.FOIAFetcher import FOIAFetcher
from source_collectors.muckrock.utils import save_json_file

# Set initial parameters
all_data = []
output_file = "foia_data.json"

# Fetch and store data from all pages
fetcher = FOIAFetcher()
while True:
    print(f"Fetching page {fetcher.current_page}...")
    data = fetcher.fetch_next_page()
    if data is None:
        print(f"Skipping page {fetcher.current_page}...")
        continue

    all_data.extend(data["results"])
    if not data["next"]:
        break


# Write data to CSV
save_json_file(file_path=output_file, data=all_data)

print(f"Data written to {output_file}")
