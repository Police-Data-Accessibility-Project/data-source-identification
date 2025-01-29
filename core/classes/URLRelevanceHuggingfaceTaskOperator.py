from collector_db.AsyncDatabaseClient import AsyncDatabaseClient
from collector_db.DTOs.URLMetadataInfo import URLMetadataInfo
from collector_db.DTOs.URLWithHTML import URLWithHTML
from collector_db.enums import URLMetadataAttributeType, ValidationStatus, ValidationSource, TaskType
from core.DTOs.task_data_objects.URLRelevanceHuggingfaceTDO import URLRelevanceHuggingfaceTDO
from core.classes.TaskOperatorBase import TaskOperatorBase
from hugging_face.HuggingFaceInterface import HuggingFaceInterface


class URLRelevanceHuggingfaceTaskOperator(TaskOperatorBase):

    def __init__(
            self,
            adb_client: AsyncDatabaseClient,
            huggingface_interface: HuggingFaceInterface
    ):
        super().__init__(adb_client)
        self.huggingface_interface = huggingface_interface

    @property
    def task_type(self):
        return TaskType.RELEVANCY

    async def meets_task_prerequisites(self):
        return await self.adb_client.has_pending_urls_with_html_data_and_without_metadata_type()

    async def inner_task_logic(self):
        # Get pending urls from Source Collector
        # with HTML data and without Relevancy Metadata
        tdos = await self.get_pending_url_info(
            without_metadata_attribute=URLMetadataAttributeType.RELEVANT
        )
        url_ids = [tdo.url_with_html.url_id for tdo in tdos]
        await self.link_urls_to_task(url_ids=url_ids)
        # Pipe into Huggingface
        await self.add_huggingface_relevancy(tdos)

        # Put results into Database
        await self.put_results_into_database(tdos)

    async def put_results_into_database(self, tdos):
        url_metadatas = []
        for tdo in tdos:
            url_metadata = URLMetadataInfo(
                url_id=tdo.url_with_html.url_id,
                attribute=URLMetadataAttributeType.RELEVANT,
                value=str(tdo.relevant),
                validation_status=ValidationStatus.PENDING_VALIDATION,
                validation_source=ValidationSource.MACHINE_LEARNING
            )
            url_metadatas.append(url_metadata)
        await self.adb_client.add_url_metadatas(url_metadatas)

    async def add_huggingface_relevancy(self, tdos: list[URLRelevanceHuggingfaceTDO]):
        urls_with_html = [tdo.url_with_html for tdo in tdos]
        results = self.huggingface_interface.get_url_relevancy(urls_with_html)
        for tdo, result in zip(tdos, results):
            tdo.relevant = result

    async def get_pending_url_info(
            self,
            without_metadata_attribute: URLMetadataAttributeType
    ) -> list[URLRelevanceHuggingfaceTDO]:
        tdos = []
        pending_urls: list[URLWithHTML] = await self.adb_client.get_urls_with_html_data_and_without_metadata_type(
            without_metadata_type=without_metadata_attribute
        )
        for url_with_html in pending_urls:
            tdo = URLRelevanceHuggingfaceTDO(
                url_with_html=url_with_html
            )
            tdos.append(tdo)
        return tdos
