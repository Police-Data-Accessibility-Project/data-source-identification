from http import HTTPStatus

from pydantic import BaseModel

from src.core.tasks.url.operators.probe_404.tdo import URL404ProbeTDO
from src.external.url_request.core import URLRequestInterface
from src.db.client.async_ import AsyncDatabaseClient
from src.db.enums import TaskType
from src.core.tasks.url.operators.base import URLTaskOperatorBase


class URL404ProbeTDOSubsets(BaseModel):
    successful: list[URL404ProbeTDO]
    is_404: list[URL404ProbeTDO]



class URL404ProbeTaskOperator(URLTaskOperatorBase):

    def __init__(
            self,
            url_request_interface: URLRequestInterface,
            adb_client: AsyncDatabaseClient,
    ):
        super().__init__(adb_client)
        self.url_request_interface = url_request_interface

    @property
    def task_type(self):
        return TaskType.PROBE_404

    async def meets_task_prerequisites(self):
        return await self.adb_client.has_pending_urls_not_recently_probed_for_404()

    async def probe_urls_for_404(self, tdos: list[URL404ProbeTDO]):
        responses = await self.url_request_interface.make_simple_requests(
            urls=[tdo.url for tdo in tdos]
        )
        for tdo, response in zip(tdos, responses):
            if response.status is None:
                continue
            tdo.is_404 = response.status == HTTPStatus.NOT_FOUND


    async def inner_task_logic(self):
        tdos = await self.get_pending_urls_not_recently_probed_for_404()
        url_ids = [task_info.url_id for task_info in tdos]
        await self.link_urls_to_task(url_ids=url_ids)
        await self.probe_urls_for_404(tdos)
        url_ids_404 = [tdo.url_id for tdo in tdos if tdo.is_404]

        await self.update_404s_in_database(url_ids_404)
        await self.mark_as_recently_probed_for_404(url_ids)

    async def get_pending_urls_not_recently_probed_for_404(self) -> list[URL404ProbeTDO]:
        return await self.adb_client.get_pending_urls_not_recently_probed_for_404()

    async def update_404s_in_database(self, url_ids_404: list[int]):
        await self.adb_client.mark_all_as_404(url_ids_404)

    async def mark_as_recently_probed_for_404(self, url_ids: list[int]):
        await self.adb_client.mark_all_as_recently_probed_for_404(url_ids)

