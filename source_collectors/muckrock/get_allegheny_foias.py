"""
Get Allegheny County FOIA requests
and save them to a JSON file

"""

from source_collectors.muckrock.classes.muckrock_fetchers.FOIALoopFetcher import FOIALoopFetcher
from source_collectors.muckrock.classes.fetch_requests.FOIALoopFetchRequest import FOIALoopFetchRequest
from source_collectors.muckrock.classes.muckrock_fetchers import JurisdictionLoopFetchRequest, \
    JurisdictionLoopFetcher
from source_collectors.muckrock.utils import save_json_file


def fetch_jurisdiction_ids(town_file, level="l", parent=126):
    """
    fetch jurisdiction IDs based on town names from a text file
    """
    with open(town_file, "r") as file:
        town_names = [line.strip() for line in file]

    request = JurisdictionLoopFetchRequest(
        level=level, parent=parent, town_names=town_names
    )

    fetcher = JurisdictionLoopFetcher(request)
    fetcher.loop_fetch()
    return fetcher.jurisdictions



def fetch_foia_data(jurisdiction_ids):
    """
    fetch FOIA data for each jurisdiction ID and save it to a JSON file
    """
    all_data = []
    for name, id_ in jurisdiction_ids.items():
        print(f"\nFetching records for {name}...")
        request = FOIALoopFetchRequest(jurisdiction=id_)
        fetcher = FOIALoopFetcher(request)
        fetcher.loop_fetch()
        all_data.extend(fetcher.ffm.results)

    # Save the combined data to a JSON file
    save_json_file(file_path="foia_data_combined.json", data=all_data)
    print(f"Saved {len(all_data)} records to foia_data_combined.json")


def main():
    """
    Execute the script
    """
    town_file = "allegheny-county-towns.txt"
    # Fetch jurisdiction IDs based on town names
    jurisdiction_ids = fetch_jurisdiction_ids(
        town_file,
        level="l",
        parent=126
    )
    print(f"Jurisdiction IDs fetched: {jurisdiction_ids}")

    # Fetch FOIA data for each jurisdiction ID
    fetch_foia_data(jurisdiction_ids)


# Run the main function
if __name__ == "__main__":
    main()
