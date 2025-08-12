from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.impl.url.error_info.pydantic import URLErrorPydanticInfo
from src.db.enums import TaskType
from src.core.tasks.url.operators.record_type.tdo import URLRecordTypeTDO
from src.core.tasks.url.operators.base import URLTaskOperatorBase
from src.core.enums import RecordType
from src.core.tasks.url.operators.record_type.llm_api.record_classifier.openai import OpenAIRecordClassifier


class URLRecordTypeTaskOperator(URLTaskOperatorBase):

    def __init__(
            self,
            adb_client: AsyncDatabaseClient,
            classifier: OpenAIRecordClassifier
    ):
        super().__init__(adb_client)
        self.classifier = classifier

    @property
    def task_type(self):
        return TaskType.RECORD_TYPE

    async def meets_task_prerequisites(self):
        return await self.adb_client.has_urls_with_html_data_and_without_auto_record_type_suggestion()

    async def get_tdos(self) -> list[URLRecordTypeTDO]:
        urls_with_html = await self.adb_client.get_urls_with_html_data_and_without_auto_record_type_suggestion()
        tdos = [URLRecordTypeTDO(url_with_html=url_with_html) for url_with_html in urls_with_html]
        return tdos

    async def inner_task_logic(self):
        # Get pending urls from Source Collector
        # with HTML data and without Record Type Metadata
        tdos = await self.get_tdos()
        url_ids = [tdo.url_with_html.url_id for tdo in tdos]
        await self.link_urls_to_task(url_ids=url_ids)

        await self.get_ml_classifications(tdos)
        success_subset, error_subset = await self.separate_success_and_error_subsets(tdos)
        await self.put_results_into_database(success_subset)
        await self.update_errors_in_database(error_subset)

    async def update_errors_in_database(self, tdos: list[URLRecordTypeTDO]):
        error_infos = []
        for tdo in tdos:
            error_info = URLErrorPydanticInfo(
                task_id=self.task_id,
                url_id=tdo.url_with_html.url_id,
                error=tdo.error
            )
            error_infos.append(error_info)
        await self.adb_client.add_url_error_infos(error_infos)

    async def put_results_into_database(self, tdos: list[URLRecordTypeTDO]):
        suggestions = []
        for tdo in tdos:
            url_id = tdo.url_with_html.url_id
            record_type = tdo.record_type
            suggestions.append((url_id, record_type))
        await self.adb_client.add_auto_record_type_suggestions(suggestions)

    async def separate_success_and_error_subsets(self, tdos: list[URLRecordTypeTDO]):
        success_subset = [tdo for tdo in tdos if not tdo.is_errored()]
        error_subset = [tdo for tdo in tdos if tdo.is_errored()]
        return success_subset, error_subset

    async def get_ml_classifications(self, tdos: list[URLRecordTypeTDO]):
        for tdo in tdos:
            try:
                record_type_str = await self.classifier.classify_url(tdo.url_with_html.html_infos)
                tdo.record_type = RecordType(record_type_str)
            except Exception as e:
                tdo.error = str(e)