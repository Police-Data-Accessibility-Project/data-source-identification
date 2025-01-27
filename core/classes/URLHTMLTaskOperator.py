from collector_db.AsyncDatabaseClient import AsyncDatabaseClient
from collector_db.DTOs.URLErrorInfos import URLErrorPydanticInfo
from collector_db.DTOs.URLInfo import URLInfo
from core.DTOs.URLHTMLTaskInfo import URLHTMLTaskInfo
from core.classes.HTMLContentInfoGetter import HTMLContentInfoGetter
from html_tag_collector.ResponseParser import HTMLResponseParser
from html_tag_collector.URLRequestInterface import URLRequestInterface


class URLHTMLTaskOperator:

    def __init__(
        self,
        url_request_interface: URLRequestInterface,
        adb_client: AsyncDatabaseClient,
        html_parser: HTMLResponseParser
    ):
        self.url_request_interface = url_request_interface
        self.adb_client = adb_client
        self.html_parser = html_parser

    async def run_task(self):
        print("Running URL HTML Task...")
        task_infos = await self.get_pending_urls_without_html_data()
        await self.get_raw_html_data_for_urls(task_infos)
        success_subset, error_subset = await self.separate_success_and_error_subsets(task_infos)
        await self.update_errors_in_database(error_subset)
        await self.process_html_data(success_subset)
        await self.update_html_data_in_database(success_subset)


    async def get_just_urls(self, task_infos: list[URLHTMLTaskInfo]):
        return [task_info.url_info.url for task_info in task_infos]

    async def get_pending_urls_without_html_data(self):
        pending_urls: list[URLInfo] = await self.adb_client.get_pending_urls_without_html_data()
        task_infos = [
            URLHTMLTaskInfo(
                url_info=url_info,
            ) for url_info in pending_urls
        ]
        return task_infos

    async def get_raw_html_data_for_urls(self, task_infos: list[URLHTMLTaskInfo]):
        just_urls = await self.get_just_urls(task_infos)
        url_response_infos = await self.url_request_interface.make_requests(just_urls)
        for task_info, url_response_info in zip(task_infos, url_response_infos):
            task_info.url_response_info = url_response_info

    async def separate_success_and_error_subsets(
            self,
            task_infos: list[URLHTMLTaskInfo]
    ) -> tuple[
        list[URLHTMLTaskInfo], # Successful
        list[URLHTMLTaskInfo]  # Error
    ]:
        errored_task_infos = []
        successful_task_infos = []
        for task_info in task_infos:
            if not task_info.url_response_info.success:
                errored_task_infos.append(task_info)
            else:
                successful_task_infos.append(task_info)
        return successful_task_infos, errored_task_infos

    async def update_errors_in_database(self, errored_task_infos: list[URLHTMLTaskInfo]):
        error_infos = []
        for error_task_info in errored_task_infos:
            error_info = URLErrorPydanticInfo(
                url_id=error_task_info.url_info.id,
                error=str(error_task_info.url_response_info.exception),
            )
            error_infos.append(error_info)
        await self.adb_client.add_url_error_infos(error_infos)

    async def process_html_data(self, task_infos: list[URLHTMLTaskInfo]):
        for task_info in task_infos:
            html_tag_info = await self.html_parser.parse(
                url=task_info.url_info.url,
                html_content=task_info.url_response_info.html,
                content_type=task_info.url_response_info.content_type
            )
            task_info.html_tag_info = html_tag_info

    async def update_html_data_in_database(self, task_infos: list[URLHTMLTaskInfo]):
        html_content_infos = []
        for task_info in task_infos:
            hcig = HTMLContentInfoGetter(
                response_html_info=task_info.html_tag_info,
                url_id=task_info.url_info.id
            )
            results = hcig.get_all_html_content()
            html_content_infos.extend(results)

        await self.adb_client.add_html_content_infos(html_content_infos)
