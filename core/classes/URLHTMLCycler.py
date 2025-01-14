from collector_db.AsyncDatabaseClient import AsyncDatabaseClient
from collector_db.DTOs.URLErrorInfos import URLErrorPydanticInfo
from collector_db.DTOs.URLInfo import URLInfo
from core.DTOs.URLHTMLCycleInfo import URLHTMLCycleInfo
from core.classes.HTMLContentInfoGetter import HTMLContentInfoGetter
from html_tag_collector.ResponseParser import HTMLResponseParser
from html_tag_collector.URLRequestInterface import URLRequestInterface


class URLHTMLCycler:

    def __init__(
        self,
        url_request_interface: URLRequestInterface,
        adb_client: AsyncDatabaseClient,
        html_parser: HTMLResponseParser
    ):
        self.url_request_interface = url_request_interface
        self.adb_client = adb_client
        self.html_parser = html_parser
        self.cycle_infos: list[URLHTMLCycleInfo] = []

    async def cycle(self):
        cycle_infos = await self.get_pending_urls_without_html_data()
        await self.get_raw_html_data_for_urls(cycle_infos)
        success_cycles, error_cycles = await self.separate_success_and_error_cycles(cycle_infos)
        await self.update_errors_in_database(error_cycles)
        await self.process_html_data(success_cycles)
        await self.update_html_data_in_database(success_cycles)


    async def get_just_urls(self, cycle_infos: list[URLHTMLCycleInfo]):
        return [cycle_info.url_info.url for cycle_info in cycle_infos]

    async def get_pending_urls_without_html_data(self):
        pending_urls: list[URLInfo] = await self.adb_client.get_pending_urls_without_html_data()
        cycle_infos = [
            URLHTMLCycleInfo(
                url_info=url_info,
            ) for url_info in pending_urls
        ]
        return cycle_infos

    async def get_raw_html_data_for_urls(self, cycle_infos: list[URLHTMLCycleInfo]):
        just_urls = await self.get_just_urls(cycle_infos)
        url_response_infos = await self.url_request_interface.make_requests(just_urls)
        for cycle_info, url_response_info in zip(self.cycle_infos, url_response_infos):
            cycle_info.url_response_info = url_response_info

    async def separate_success_and_error_cycles(
            self,
            cycle_infos: list[URLHTMLCycleInfo]
    ) -> tuple[
        list[URLHTMLCycleInfo], # Successful
        list[URLHTMLCycleInfo]  # Error
    ]:
        errored_cycle_infos = []
        successful_cycle_infos = []
        for cycle_info in cycle_infos:
            if not cycle_info.url_response_info.success:
                errored_cycle_infos.append(cycle_info)
            else:
                successful_cycle_infos.append(cycle_info)
        return successful_cycle_infos, errored_cycle_infos

    async def update_errors_in_database(self, errored_cycle_infos: list[URLHTMLCycleInfo]):
        error_infos = []
        for errored_cycle_info in errored_cycle_infos:
            error_info = URLErrorPydanticInfo(
                url_id=errored_cycle_info.url_info.id,
                error=errored_cycle_info.url_response_info.response,
            )
            error_infos.append(error_info)
        await self.adb_client.add_url_error_infos(error_infos)

    async def process_html_data(self, cycle_infos: list[URLHTMLCycleInfo]):
        for cycle_info in cycle_infos:
            html_tag_info = await self.html_parser.parse(
                cycle_info.url_response_info.response
            )
            cycle_info.html_tag_info = html_tag_info

    async def update_html_data_in_database(self, cycle_infos: list[URLHTMLCycleInfo]):
        html_content_infos = []
        for cycle_info in cycle_infos:
            hcig = HTMLContentInfoGetter(
                response_html_info=cycle_info.html_tag_info,
                url_id=cycle_info.url_info.id
            )
            results = hcig.get_all_html_content()
            html_content_infos.extend(results)

        await self.adb_client.add_html_content_infos(html_content_infos)
