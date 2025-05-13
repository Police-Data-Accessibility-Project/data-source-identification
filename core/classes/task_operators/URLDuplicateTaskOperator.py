from http import HTTPStatus

from aiohttp import ClientResponseError

from collector_db.AsyncDatabaseClient import AsyncDatabaseClient
from collector_db.enums import TaskType
from core.DTOs.task_data_objects.URLDuplicateTDO import URLDuplicateTDO
from core.classes.task_operators.TaskOperatorBase import TaskOperatorBase
from pdap_api_client.PDAPClient import PDAPClient


class URLDuplicateTaskOperator(TaskOperatorBase):

    def __init__(
        self,
        adb_client: AsyncDatabaseClient,
        pdap_client: PDAPClient
    ):
        super().__init__(adb_client)
        self.pdap_client = pdap_client

    @property
    def task_type(self):
        return TaskType.DUPLICATE_DETECTION

    async def meets_task_prerequisites(self):
        return await self.adb_client.has_pending_urls_not_checked_for_duplicates()

    async def inner_task_logic(self):
        tdos: list[URLDuplicateTDO] = await self.adb_client.get_pending_urls_not_checked_for_duplicates()
        url_ids = [tdo.url_id for tdo in tdos]
        await self.link_urls_to_task(url_ids=url_ids)
        checked_tdos = []
        for tdo in tdos:
            try:
                tdo.is_duplicate = await self.pdap_client.is_url_duplicate(tdo.url)
                checked_tdos.append(tdo)
            except ClientResponseError as e:
                print("ClientResponseError:", e.status)
                if e.status == HTTPStatus.TOO_MANY_REQUESTS:
                    break
                raise e

        duplicate_url_ids = [tdo.url_id for tdo in checked_tdos if tdo.is_duplicate]
        checked_url_ids = [tdo.url_id for tdo in checked_tdos]
        await self.adb_client.mark_all_as_duplicates(duplicate_url_ids)
        await self.adb_client.mark_as_checked_for_duplicates(checked_url_ids)
