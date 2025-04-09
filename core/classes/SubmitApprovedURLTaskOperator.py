from collector_db.AsyncDatabaseClient import AsyncDatabaseClient
from collector_db.DTOs.URLErrorInfos import URLErrorPydanticInfo
from collector_db.enums import TaskType
from core.DTOs.task_data_objects.SubmitApprovedURLTDO import SubmitApprovedURLTDO
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
        # Retrieve all URLs that are validated and not submitted
        tdos: list[SubmitApprovedURLTDO] = await self.adb_client.get_validated_urls()

        # Link URLs to this task
        await self.link_urls_to_task(url_ids=[tdo.url_id for tdo in tdos])

        # Submit each URL, recording errors if they exist
        error_infos: list[URLErrorPydanticInfo] = []
        success_tdos: list[SubmitApprovedURLTDO] = []
        for tdo in tdos:
            try:
                data_source_id = await self.pdap_client.submit_url(tdo)
                tdo.data_source_id = data_source_id
                success_tdos.append(tdo)
            except Exception as e:
                error_info = URLErrorPydanticInfo(
                    task_id=self.task_id,
                    url_id=tdo.url_id,
                    error=str(e),
                )
                error_infos.append(error_info)

        # Update the database for successful submissions
        await self.adb_client.mark_urls_as_submitted(tdos=success_tdos)

        # Update the database for failed submissions
        await self.adb_client.add_url_error_infos(error_infos)
