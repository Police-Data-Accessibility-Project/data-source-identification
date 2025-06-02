from http import HTTPStatus

from aiohttp import ClientResponseError

from src.db.client.async_ import AsyncDatabaseClient
from src.db.enums import TaskType
from src.core.tasks.operators.url_duplicate.tdo import URLDuplicateTDO
from src.core.tasks.operators.base import TaskOperatorBase
from src.pdap_api.client import PDAPClient


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
