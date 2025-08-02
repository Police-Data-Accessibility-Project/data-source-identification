from typing import final
from typing_extensions import override

from src.core.tasks.url.operators.base import URLTaskOperatorBase
from src.core.tasks.url.operators.probe.tdo import URLProbeTDO
from src.db.models.instantiations.url.web_metadata.pydantic import URLWebMetadataPydantic
from src.external.url_request.core import URLRequestInterface
from src.db.client.async_ import AsyncDatabaseClient
from src.db.dtos.url.mapping import URLMapping
from src.db.enums import TaskType

@final
class URLProbeTaskOperator(URLTaskOperatorBase):

    def __init__(
        self,
        adb_client: AsyncDatabaseClient,
        url_request_interface: URLRequestInterface
    ):
        super().__init__(adb_client=adb_client)
        self.url_request_interface = url_request_interface


    @property
    @override
    def task_type(self) -> TaskType:
        return TaskType.PROBE_URL

    @override
    async def meets_task_prerequisites(self) -> bool:
        return await self.adb_client.has_urls_without_probe()

    async def get_urls_without_probe(self) -> list[URLProbeTDO]:
        url_mappings: list[URLMapping] = await self.adb_client.get_urls_without_probe()
        return [URLProbeTDO(url_mapping=url_mapping) for url_mapping in url_mappings]

    @override
    async def inner_task_logic(self) -> None:
        tdos = await self.get_urls_without_probe()
        await self.link_urls_to_task(
            url_ids=[tdo.url_mapping.url_id for tdo in tdos]
        )
        await self.probe_urls(tdos)
        await self.update_database(tdos)

    async def probe_urls(self, tdos: list[URLProbeTDO]) -> None:
        """Probe URLs and add responses to URLProbeTDO

        Modifies:
            URLProbeTDO.response
        """
        url_to_tdo: dict[str, URLProbeTDO] = {
            tdo.url_mapping.url: tdo for tdo in tdos
        }
        responses = await self.url_request_interface.probe_urls(
            urls=[tdo.url_mapping.url for tdo in tdos]
        )
        # Re-associate the responses with the URL mappings
        for response in responses:
            tdo = url_to_tdo[response.url]
            tdo.response = response

    async def update_database(self, tdos: list[URLProbeTDO]) -> None:
        web_metadata_objects: list[URLWebMetadataPydantic] = []
        for tdo in tdos:
            response = tdo.response
            web_metadata_object = URLWebMetadataPydantic(
                url_id=tdo.url_mapping.url_id,
                accessed=response.status_code is not None,
                status_code=response.status_code,
                content_type=response.content_type,
                error_message=response.error
            )
            web_metadata_objects.append(web_metadata_object)
        await self.adb_client.bulk_insert(web_metadata_objects)


