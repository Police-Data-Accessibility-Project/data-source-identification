import itertools

from src.collectors.enums import CollectorType
from src.collectors.impl.base import AsyncCollectorBase
from src.collectors.impl.muckrock.collectors.simple.dto import MuckrockSimpleSearchCollectorInputDTO
from src.collectors.impl.muckrock.collectors.simple.searcher import FOIASearcher
from src.collectors.impl.muckrock.fetchers.foia.core import FOIAFetcher
from src.collectors.impl.muckrock.exceptions import SearchCompleteException
from src.core.preprocessors.muckrock import MuckrockPreprocessor


class MuckrockSimpleSearchCollector(AsyncCollectorBase):
    """
    Performs searches on MuckRock's database
    by matching a search string to title of request
    """
    collector_type = CollectorType.MUCKROCK_SIMPLE_SEARCH
    preprocessor = MuckrockPreprocessor

    def check_for_count_break(self, count, max_count) -> None:
        if max_count is None:
            return
        if count >= max_count:
            raise SearchCompleteException

    async def run_implementation(self) -> None:
        fetcher = FOIAFetcher()
        dto: MuckrockSimpleSearchCollectorInputDTO = self.dto
        searcher = FOIASearcher(
            fetcher=fetcher,
            search_term=dto.search_string
        )
        max_count = dto.max_results
        all_results = []
        results_count = 0
        for search_count in itertools.count():
            try:
                results = await searcher.get_next_page_results()
                all_results.extend(results)
                results_count += len(results)
                self.check_for_count_break(results_count, max_count)
            except SearchCompleteException:
                break
            await self.log(f"Search {search_count}: Found {len(results)} results")

        await self.log(f"Search Complete. Total results: {results_count}")
        self.data = {"urls": self.format_results(all_results)}

    def format_results(self, results: list[dict]) -> list[dict]:
        formatted_results = []
        for result in results:
            formatted_result = {
                "url": result["absolute_url"],
                "metadata": result
            }
            formatted_results.append(formatted_result)

        return formatted_results
