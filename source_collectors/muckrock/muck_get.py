"""
A straightforward standalone script for downloading data from MuckRock
and searching for it with a specific search string.
"""
from source_collectors.muckrock.classes.FOIASearcher import FOIASearcher
from source_collectors.muckrock.classes.muckrock_fetchers import FOIAFetcher
from source_collectors.muckrock.utils import save_json_file

if __name__ == "__main__":
    search_term = "use of force"
    fetcher = FOIAFetcher()
    searcher = FOIASearcher(fetcher=fetcher, search_term=search_term)
    results = searcher.search_to_count(20)
    json_out_file = search_term.replace(" ", "_") + ".json"
    save_json_file(file_path=json_out_file, data=results)
    print(f"List dumped into {json_out_file}")
