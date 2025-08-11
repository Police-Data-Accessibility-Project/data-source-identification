from src.collectors.impl.auto_googler.dtos.query_results import GoogleSearchQueryResultsInnerDTO
from src.collectors.impl.auto_googler.searcher import GoogleSearcher
from src.collectors.impl.auto_googler.dtos.config import SearchConfig


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

