from collector_db.AsyncDatabaseClient import AsyncDatabaseClient
from collector_db.DTOs.URLWithHTML import URLWithHTML
from collector_db.enums import TaskType
from core.DTOs.task_data_objects.URLRelevanceHuggingfaceTDO import URLRelevanceHuggingfaceTDO
from core.classes.task_operators.TaskOperatorBase import TaskOperatorBase
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
        return await self.adb_client.has_urls_with_html_data_and_without_auto_relevant_suggestion()

    async def inner_task_logic(self):
        # Get pending urls from Source Collector
        # with HTML data and without Relevancy Metadata
        tdos = await self.get_pending_url_info()
        url_ids = [tdo.url_with_html.url_id for tdo in tdos]
        await self.link_urls_to_task(url_ids=url_ids)
        # Pipe into Huggingface
        await self.add_huggingface_relevancy(tdos)

        # Put results into Database
        await self.put_results_into_database(tdos)

    async def put_results_into_database(self, tdos):
        suggestions: list[tuple[int, bool]] = []
        for tdo in tdos:
            url_id = tdo.url_with_html.url_id
            relevant = tdo.relevant
            suggestions.append((url_id, relevant))

        await self.adb_client.add_auto_relevance_suggestions(suggestions)

    async def add_huggingface_relevancy(self, tdos: list[URLRelevanceHuggingfaceTDO]):
        urls_with_html = [tdo.url_with_html for tdo in tdos]
        results = await self.huggingface_interface.get_url_relevancy_async(urls_with_html)
        for tdo, result in zip(tdos, results):
            tdo.relevant = result

    async def get_pending_url_info(
            self,
    ) -> list[URLRelevanceHuggingfaceTDO]:
        tdos = []
        pending_urls: list[URLWithHTML] = await self.adb_client.get_urls_with_html_data_and_without_auto_relevant_suggestion()
        for url_with_html in pending_urls:
            tdo = URLRelevanceHuggingfaceTDO(
                url_with_html=url_with_html
            )
            tdos.append(tdo)
        return tdos
