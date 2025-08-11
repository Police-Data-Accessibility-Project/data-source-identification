from src.collectors.enums import CollectorType
from src.collectors.impl.base import AsyncCollectorBase
from src.collectors.impl.muckrock.collectors.all_foia.dto import MuckrockAllFOIARequestsCollectorInputDTO
from src.collectors.impl.muckrock.fetchers.foia.core import FOIAFetcher
from src.collectors.impl.muckrock.exceptions import MuckrockNoMoreDataError
from src.core.preprocessors.muckrock import MuckrockPreprocessor


class MuckrockAllFOIARequestsCollector(AsyncCollectorBase):
    """
    Retrieves urls associated with all Muckrock FOIA requests
    """
    collector_type = CollectorType.MUCKROCK_ALL_SEARCH
    preprocessor = MuckrockPreprocessor

    async def run_implementation(self) -> None:
        dto: MuckrockAllFOIARequestsCollectorInputDTO = self.dto
        start_page = dto.start_page
        fetcher = FOIAFetcher(
            start_page=start_page,
        )
        total_pages = dto.total_pages
        all_page_data = await self.get_page_data(fetcher, start_page, total_pages)
        all_transformed_data = self.transform_data(all_page_data)
        self.data = {"urls": all_transformed_data}


    async def get_page_data(self, fetcher, start_page, total_pages):
        all_page_data = []
        for page in range(start_page, start_page + total_pages):
            await self.log(f"Fetching page {fetcher.current_page}")
            try:
                page_data = await fetcher.fetch_next_page()
            except MuckrockNoMoreDataError:
                await self.log(f"No more data to fetch at page {fetcher.current_page}")
                break
            if page_data is None:
                continue
            all_page_data.append(page_data)
        return all_page_data

    def transform_data(self, all_page_data):
        all_transformed_data = []
        for page_data in all_page_data:
            for data in page_data["results"]:
                all_transformed_data.append({
                    "url": data["absolute_url"],
                    "metadata": data
                })
        return all_transformed_data
