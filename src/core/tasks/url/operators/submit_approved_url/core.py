from src.db.client.async_ import AsyncDatabaseClient
from src.db.dtos.url.error import URLErrorPydanticInfo
from src.db.enums import TaskType
from src.core.tasks.url.operators.submit_approved_url.tdo import SubmitApprovedURLTDO
from src.core.tasks.url.operators.base import URLTaskOperatorBase
from src.external.pdap.client import PDAPClient


class SubmitApprovedURLTaskOperator(URLTaskOperatorBase):

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
        submitted_url_infos = await self.pdap_client.submit_urls(tdos)

        error_infos = await self.get_error_infos(submitted_url_infos)
        success_infos = await self.get_success_infos(submitted_url_infos)

        # Update the database for successful submissions
        await self.adb_client.mark_urls_as_submitted(infos=success_infos)

        # Update the database for failed submissions
        await self.adb_client.add_url_error_infos(error_infos)

    async def get_success_infos(self, submitted_url_infos):
        success_infos = [
            response_object for response_object in submitted_url_infos
            if response_object.data_source_id is not None
        ]
        return success_infos

    async def get_error_infos(self, submitted_url_infos):
        error_infos: list[URLErrorPydanticInfo] = []
        error_response_objects = [
            response_object for response_object in submitted_url_infos
            if response_object.request_error is not None
        ]
        for error_response_object in error_response_objects:
            error_info = URLErrorPydanticInfo(
                task_id=self.task_id,
                url_id=error_response_object.url_id,
                error=error_response_object.request_error,
            )
            error_infos.append(error_info)
        return error_infos
