from src.source_collectors.auto_googler.DTOs import GoogleSearchQueryResultsInnerDTO
from src.source_collectors.auto_googler.GoogleSearcher import GoogleSearcher
from src.source_collectors.auto_googler.SearchConfig import SearchConfig


class AutoGoogler:
    """
    The AutoGoogler orchestrates the process of fetching urls from Google Search
     and processing them for source collection

    """
    def __init__(self, search_config: SearchConfig, google_searcher: GoogleSearcher):
        self.search_config = search_config
        self.google_searcher = google_searcher
        self.data: dict[str, list[GoogleSearchQueryResultsInnerDTO]] = {
            query : [] for query in search_config.queries
        }

    async def run(self) -> str:
        """
        Runs the AutoGoogler
        Yields status messages
        """
        for query in self.search_config.queries:
            yield f"Searching for '{query}' ..."
            results = await self.google_searcher.search(query)
            yield f"Found {len(results)} results for '{query}'."
            if results is not None:
                self.data[query] = results
        yield "Done."

