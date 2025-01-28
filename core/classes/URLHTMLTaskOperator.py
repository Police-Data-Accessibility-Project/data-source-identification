from collector_db.AsyncDatabaseClient import AsyncDatabaseClient
from collector_db.DTOs.URLErrorInfos import URLErrorPydanticInfo
from collector_db.DTOs.URLInfo import URLInfo
from collector_db.enums import TaskType
from core.DTOs.task_data_objects.UrlHtmlTDO import UrlHtmlTDO
from core.classes.HTMLContentInfoGetter import HTMLContentInfoGetter
from core.classes.TaskOperatorBase import TaskOperatorBase
from html_tag_collector.ResponseParser import HTMLResponseParser
from html_tag_collector.URLRequestInterface import URLRequestInterface


class URLHTMLTaskOperator(TaskOperatorBase):

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
    def task_type(self):
        return TaskType.HTML

    async def meets_task_prerequisites(self):
        return await self.adb_client.has_pending_urls_without_html_data()

    async def inner_task_logic(self):
        print("Running URL HTML Task...")
        tdos = await self.get_pending_urls_without_html_data()
        url_ids = [task_info.url_info.id for task_info in tdos]
        await self.link_urls_to_task(url_ids=url_ids)
        await self.get_raw_html_data_for_urls(tdos)
        success_subset, error_subset = await self.separate_success_and_error_subsets(tdos)
        await self.update_errors_in_database(error_subset)
        await self.process_html_data(success_subset)
        await self.update_html_data_in_database(success_subset)


    async def get_just_urls(self, tdos: list[UrlHtmlTDO]):
        return [task_info.url_info.url for task_info in tdos]

    async def get_pending_urls_without_html_data(self):
        pending_urls: list[URLInfo] = await self.adb_client.get_pending_urls_without_html_data()
        tdos = [
            UrlHtmlTDO(
                url_info=url_info,
            ) for url_info in pending_urls
        ]
        return tdos

    async def get_raw_html_data_for_urls(self, tdos: list[UrlHtmlTDO]):
        just_urls = await self.get_just_urls(tdos)
        url_response_infos = await self.url_request_interface.make_requests(just_urls)
        for tdto, url_response_info in zip(tdos, url_response_infos):
            tdto.url_response_info = url_response_info

    async def separate_success_and_error_subsets(
            self,
            tdos: list[UrlHtmlTDO]
    ) -> tuple[
        list[UrlHtmlTDO], # Successful
        list[UrlHtmlTDO]  # Error
    ]:
        errored_tdos = []
        successful_tdos = []
        for tdto in tdos:
            if not tdto.url_response_info.success:
                errored_tdos.append(tdto)
            else:
                successful_tdos.append(tdto)
        return successful_tdos, errored_tdos

    async def update_errors_in_database(self, error_tdos: list[UrlHtmlTDO]):
        error_infos = []
        for error_tdo in error_tdos:
            error_info = URLErrorPydanticInfo(
                task_id=self.task_id,
                url_id=error_tdo.url_info.id,
                error=str(error_tdo.url_response_info.exception),
            )
            error_infos.append(error_info)
        await self.adb_client.add_url_error_infos(error_infos)

    async def process_html_data(self, tdos: list[UrlHtmlTDO]):
        for tdto in tdos:
            html_tag_info = await self.html_parser.parse(
                url=tdto.url_info.url,
                html_content=tdto.url_response_info.html,
                content_type=tdto.url_response_info.content_type
            )
            tdto.html_tag_info = html_tag_info

    async def update_html_data_in_database(self, tdos: list[UrlHtmlTDO]):
        html_content_infos = []
        for tdto in tdos:
            hcig = HTMLContentInfoGetter(
                response_html_info=tdto.html_tag_info,
                url_id=tdto.url_info.id
            )
            results = hcig.get_all_html_content()
            html_content_infos.extend(results)

        await self.adb_client.add_html_content_infos(html_content_infos)
