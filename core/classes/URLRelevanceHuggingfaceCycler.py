from collector_db.AsyncDatabaseClient import AsyncDatabaseClient
from collector_db.DTOs.URLMetadataInfo import URLMetadataInfo
from collector_db.DTOs.URLWithHTML import URLWithHTML
from collector_db.enums import URLMetadataAttributeType, ValidationStatus, ValidationSource
from core.DTOs.URLRelevanceHuggingfaceCycleInfo import URLRelevanceHuggingfaceCycleInfo
from hugging_face.HuggingFaceInterface import HuggingFaceInterface


class URLRelevanceHuggingfaceCycler:

    def __init__(
            self,
            adb_client: AsyncDatabaseClient,
            huggingface_interface: HuggingFaceInterface
    ):
        self.adb_client = adb_client
        self.huggingface_interface = huggingface_interface

    async def cycle(self):
        # Get pending urls from Source Collector
        # with HTML data and without Relevancy Metadata
        cycle_infos = await self.get_pending_url_info()
        # Pipe into Huggingface
        await self.add_huggingface_relevancy(cycle_infos)

        # Put results into Database
        await self.put_results_into_database(cycle_infos)

    async def put_results_into_database(self, cycle_infos):
        url_metadatas = []
        for cycle_info in cycle_infos:
            url_metadata = URLMetadataInfo(
                url_id=cycle_info.url_with_html.url_id,
                attribute=URLMetadataAttributeType.RELEVANT,
                value=str(cycle_info.relevant),
                validation_status=ValidationStatus.PENDING_VALIDATION,
                validation_source=ValidationSource.MACHINE_LEARNING
            )
            url_metadatas.append(url_metadata)
        await self.adb_client.add_url_metadatas(url_metadatas)

    async def add_huggingface_relevancy(self, cycle_infos: list[URLRelevanceHuggingfaceCycleInfo]):
        urls_with_html = [cycle_info.url_with_html for cycle_info in cycle_infos]
        results = self.huggingface_interface.get_url_relevancy(urls_with_html)
        for cycle_info, result in zip(cycle_infos, results):
            cycle_info.relevant = result

    async def get_pending_url_info(self) -> list[URLRelevanceHuggingfaceCycleInfo]:
        cycle_infos = []
        pending_urls: list[URLWithHTML] = await self.adb_client.get_urls_with_html_data_and_no_relevancy_metadata()
        for url_with_html in pending_urls:
            cycle_info = URLRelevanceHuggingfaceCycleInfo(
                url_with_html=url_with_html
            )
            cycle_infos.append(cycle_info)
        return cycle_infos
