from src.collectors.enums import CollectorType
from src.collectors.impl.base import AsyncCollectorBase
from src.collectors.impl.muckrock.collectors.county.dto import MuckrockCountySearchCollectorInputDTO
from src.collectors.impl.muckrock.fetch_requests.foia_loop import FOIALoopFetchRequest
from src.collectors.impl.muckrock.fetch_requests.jurisdiction_loop import \
    JurisdictionLoopFetchRequest
from src.collectors.impl.muckrock.fetchers.foia.loop import FOIALoopFetcher
from src.collectors.impl.muckrock.fetchers.jurisdiction.generator import \
    JurisdictionGeneratorFetcher
from src.core.preprocessors.muckrock import MuckrockPreprocessor


class MuckrockCountyLevelSearchCollector(AsyncCollectorBase):
    """
    Searches for any and all requests in a certain county
    """
    collector_type = CollectorType.MUCKROCK_COUNTY_SEARCH
    preprocessor = MuckrockPreprocessor

    async def run_implementation(self) -> None:
        jurisdiction_ids = await self.get_jurisdiction_ids()
        if jurisdiction_ids is None:
            await self.log("No jurisdictions found")
            return
        all_data = await self.get_foia_records(jurisdiction_ids)
        formatted_data = self.format_data(all_data)
        self.data = {"urls": formatted_data}

    def format_data(self, all_data):
        formatted_data = []
        for data in all_data:
            formatted_data.append({
                "url": data["absolute_url"],
                "metadata": data
            })
        return formatted_data

    async def get_foia_records(self, jurisdiction_ids):
        all_data = []
        for name, id_ in jurisdiction_ids.items():
            await self.log(f"Fetching records for {name}...")
            request = FOIALoopFetchRequest(jurisdiction=id_)
            fetcher = FOIALoopFetcher(request)
            await fetcher.loop_fetch()
            all_data.extend(fetcher.ffm.results)
        return all_data

    async def get_jurisdiction_ids(self):
        dto: MuckrockCountySearchCollectorInputDTO = self.dto
        parent_jurisdiction_id = dto.parent_jurisdiction_id
        request = JurisdictionLoopFetchRequest(
            level="l",
            parent=parent_jurisdiction_id,
            town_names=dto.town_names
        )
        fetcher = JurisdictionGeneratorFetcher(initial_request=request)
        async for message in fetcher.generator_fetch():
            await self.log(message)
        jurisdiction_ids = fetcher.jfm.jurisdictions
        return jurisdiction_ids
