from collector_db.AsyncDatabaseClient import AsyncDatabaseClient
from collector_db.DTOs.URLMetadataInfo import URLMetadataInfo
from collector_db.DTOs.URLWithHTML import URLWithHTML
from collector_db.enums import URLMetadataAttributeType, ValidationStatus, ValidationSource
from core.DTOs.URLRelevanceHuggingfaceTaskInfo import URLRelevanceHuggingfaceTaskInfo
from hugging_face.HuggingFaceInterface import HuggingFaceInterface


class URLRelevanceHuggingfaceTaskOperator:

    def __init__(
            self,
            adb_client: AsyncDatabaseClient,
            huggingface_interface: HuggingFaceInterface
    ):
        self.adb_client = adb_client
        self.huggingface_interface = huggingface_interface

    async def run_task(self):
        # Get pending urls from Source Collector
        # with HTML data and without Relevancy Metadata
        task_infos = await self.get_pending_url_info(
            without_metadata_attribute=URLMetadataAttributeType.RELEVANT
        )
        # Pipe into Huggingface
        await self.add_huggingface_relevancy(task_infos)

        # Put results into Database
        await self.put_results_into_database(task_infos)

    async def put_results_into_database(self, task_infos):
        url_metadatas = []
        for task_info in task_infos:
            url_metadata = URLMetadataInfo(
                url_id=task_info.url_with_html.url_id,
                attribute=URLMetadataAttributeType.RELEVANT,
                value=str(task_info.relevant),
                validation_status=ValidationStatus.PENDING_VALIDATION,
                validation_source=ValidationSource.MACHINE_LEARNING
            )
            url_metadatas.append(url_metadata)
        await self.adb_client.add_url_metadatas(url_metadatas)

    async def add_huggingface_relevancy(self, task_infos: list[URLRelevanceHuggingfaceTaskInfo]):
        urls_with_html = [task_info.url_with_html for task_info in task_infos]
        results = self.huggingface_interface.get_url_relevancy(urls_with_html)
        for task_info, result in zip(task_infos, results):
            task_info.relevant = result

    async def get_pending_url_info(
            self,
            without_metadata_attribute: URLMetadataAttributeType
    ) -> list[URLRelevanceHuggingfaceTaskInfo]:
        task_infos = []
        pending_urls: list[URLWithHTML] = await self.adb_client.get_urls_with_html_data_and_without_metadata_type(
            without_metadata_type=without_metadata_attribute
        )
        for url_with_html in pending_urls:
            task_info = URLRelevanceHuggingfaceTaskInfo(
                url_with_html=url_with_html
            )
            task_infos.append(task_info)
        return task_infos
