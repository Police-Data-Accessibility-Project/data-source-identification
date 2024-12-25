from typing import Optional

from source_collectors.muckrock.classes.muckrock_fetchers import FOIAFetcher
from tqdm import tqdm


class SearchCompleteException(Exception):
    pass

class FOIASearcher:
    """
    Used for searching FOIA data from MuckRock
    """

    def __init__(self, fetcher: FOIAFetcher, search_term: Optional[str] = None):
        self.fetcher = fetcher
        self.search_term = search_term

    def fetch_page(self) -> dict | None:
        """
        Fetches the next page of results using the fetcher.
        """
        data = self.fetcher.fetch_next_page()
        if data is None or data.get("results") is None:
            return None
        return data

    def filter_results(self, results: list[dict]) -> list[dict]:
        """
        Filters the results based on the search term.
        Override or modify as needed for custom filtering logic.
        """
        if self.search_term:
            return [result for result in results if self.search_term.lower() in result["title"].lower()]
        return results

    def update_progress(self, pbar: tqdm, results: list[dict]) -> int:
        """
        Updates the progress bar and returns the count of results processed.
        """
        num_results = len(results)
        pbar.update(num_results)
        return num_results

    def search_to_count(self, max_count: int) -> list[dict]:
        """
        Fetches and processes results up to a maximum count.
        """
        count = max_count
        all_results = []
        with tqdm(total=max_count, desc="Fetching results", unit="result") as pbar:
            while count > 0:
                try:
                    results = self.get_next_page_results()
                except SearchCompleteException:
                    break

                all_results.extend(results)
                count -= self.update_progress(pbar, results)

        return all_results

    def get_next_page_results(self) -> list[dict]:
        """
        Fetches and processes the next page of results.
        """
        data = self.fetch_page()
        if not data:
            raise SearchCompleteException
        return self.filter_results(data["results"])

