from collector_db.AsyncDatabaseClient import AsyncDatabaseClient
from collector_db.enums import TaskType
from core.DTOs.task_data_objects.UrlHtmlTDO import UrlHtmlTDO
from core.classes.TaskOperatorBase import TaskOperatorBase
from pdap_api_client.PDAPClient import PDAPClient


class SubmitApprovedURLTaskOperator(TaskOperatorBase):

    def __init__(
            self,
            adb_client: AsyncDatabaseClient,
            pdap_client: PDAPClient
    ):
        super().__init__(adb_client)
        self.pdap_client = pdap_client

    @property
    def task_type(self):
        return TaskType.SUBMIT_APPROVED

    async def meets_task_prerequisites(self):
        return await self.adb_client.has_validated_urls()

    async def inner_task_logic(self):
        raise NotImplementedError

    async def update_errors_in_database(self, error_tdos: list[UrlHtmlTDO]):
        raise NotImplementedError