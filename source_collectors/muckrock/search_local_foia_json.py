"""
***DEPRECATED***

search_local_foia_json.py

"""

import json

from source_collectors.muckrock.utils import load_json_file, save_json_file

# Specify the JSON file path
json_file = "foia_data.json"
search_string = "use of force"

# Load the JSON data
data = load_json_file(json_file)

# List to store matching entries
matching_entries = []


def search_entry(entry):
    """
    search within an entry
    """
    # Check if 'status' is 'done'
    if entry.get("status") != "done":
        return False

    # Check if 'title' or 'tags' field contains the search string
    title_match = "title" in entry and search_string.lower() in entry["title"].lower()
    tags_match = "tags" in entry and any(
        search_string.lower() in tag.lower() for tag in entry["tags"]
    )

    return title_match or tags_match


# Iterate through the data and collect matching entries
for entry in data:
    if search_entry(entry):
        matching_entries.append(entry)

# Output the results
print(
    f"Found {len(matching_entries)} entries containing '{search_string}' in the title or tags."
)

# Optionally, write matching entries to a new JSON file
save_json_file(file_path="matching_entries.json", data=matching_entries)

print("Matching entries written to 'matching_entries.json'")
