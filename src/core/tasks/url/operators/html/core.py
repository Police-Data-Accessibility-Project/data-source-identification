from src.core.tasks.url.operators.base import URLTaskOperatorBase
from src.core.tasks.url.operators.html.filter import filter_just_urls, filter_404_subset
from src.core.tasks.url.operators.html.queries.insert.query import InsertURLHTMLInfoQueryBuilder
from src.core.tasks.url.operators.html.scraper.parser.core import HTMLResponseParser
from src.core.tasks.url.operators.html.tdo import UrlHtmlTDO
from src.db.client.async_ import AsyncDatabaseClient
from src.db.enums import TaskType
from src.db.models.impl.url.core.pydantic.info import URLInfo
from src.external.url_request.core import URLRequestInterface


class URLHTMLTaskOperator(URLTaskOperatorBase):

    def __init__(
            self,
            url_request_interface: URLRequestInterface,
            adb_client: AsyncDatabaseClient,
            html_parser: HTMLResponseParser
    ):
        super().__init__(adb_client)
        self.url_request_interface = url_request_interface
        self.html_parser = html_parser

    @property
    def task_type(self) -> TaskType:
        return TaskType.HTML

    async def meets_task_prerequisites(self) -> bool:
        return await self.adb_client.has_non_errored_urls_without_html_data()

    async def inner_task_logic(self) -> None:
        tdos = await self._get_non_errored_urls_without_html_data()
        url_ids = [task_info.url_info.id for task_info in tdos]
        await self.link_urls_to_task(url_ids=url_ids)

        await self._get_raw_html_data_for_urls(tdos)
        await self._process_html_data(tdos)

        tdos_404 = await filter_404_subset(tdos)
        await self._update_404s_in_database(tdos_404)
        await self._update_html_data_in_database(tdos)


    async def _get_non_errored_urls_without_html_data(self) -> list[UrlHtmlTDO]:
        pending_urls: list[URLInfo] = await self.adb_client.get_non_errored_urls_without_html_data()
        tdos = [
            UrlHtmlTDO(
                url_info=url_info,
            ) for url_info in pending_urls
        ]
        return tdos

    async def _get_raw_html_data_for_urls(self, tdos: list[UrlHtmlTDO]) -> None:
        just_urls = await filter_just_urls(tdos)
        url_response_infos = await self.url_request_interface.make_requests_with_html(just_urls)
        for tdto, url_response_info in zip(tdos, url_response_infos):
            tdto.url_response_info = url_response_info

    async def _update_404s_in_database(self, tdos_404: list[UrlHtmlTDO]) -> None:
        url_ids = [tdo.url_info.id for tdo in tdos_404]
        await self.adb_client.mark_all_as_404(url_ids)


    async def _process_html_data(self, tdos: list[UrlHtmlTDO]) -> None:
        """
        Modifies:
            tdto.html_tag_info
        """
        for tdto in tdos:
            if not tdto.url_response_info.success:
                continue
            html_tag_info = await self.html_parser.parse(
                url=tdto.url_info.url,
                html_content=tdto.url_response_info.html,
                content_type=tdto.url_response_info.content_type
            )
            tdto.html_tag_info = html_tag_info

    async def _update_html_data_in_database(self, tdos: list[UrlHtmlTDO]) -> None:
        await self.adb_client.run_query_builder(
            InsertURLHTMLInfoQueryBuilder(tdos, task_id=self.task_id)
        )


