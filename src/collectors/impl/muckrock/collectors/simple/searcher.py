from typing import Optional

from src.collectors.impl.muckrock.fetchers.foia.core import FOIAFetcher
from src.collectors.impl.muckrock.exceptions import SearchCompleteException


class FOIASearcher:
    """
    Used for searching FOIA data from MuckRock
    """

    def __init__(self, fetcher: FOIAFetcher, search_term: Optional[str] = None):
        self.fetcher = fetcher
        self.search_term = search_term

    async def fetch_page(self) -> list[dict] | None:
        """
        Fetches the next page of results using the fetcher.
        """
        data = await self.fetcher.fetch_next_page()
        if data is None or data.get("results") is None:
            return None
        return data.get("results")

    def filter_results(self, results: list[dict]) -> list[dict]:
        """
        Filters the results based on the search term.
        Override or modify as needed for custom filtering logic.
        """
        if self.search_term:
            return [result for result in results if self.search_term.lower() in result["title"].lower()]
        return results


    async def get_next_page_results(self) -> list[dict]:
        """
        Fetches and processes the next page of results.
        """
        results = await self.fetch_page()
        if not results:
            raise SearchCompleteException
        return self.filter_results(results)

