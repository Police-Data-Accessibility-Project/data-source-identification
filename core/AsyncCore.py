from collector_db.AsyncDatabaseClient import AsyncDatabaseClient
from collector_db.DTOs.URLErrorInfos import URLErrorPydanticInfo
from collector_db.DTOs.URLHTMLContentInfo import URLHTMLContentInfo, HTMLContentType
from collector_db.DTOs.URLInfo import URLInfo
from collector_db.DTOs.URLMetadataInfo import URLMetadataInfo
from collector_db.models import URLAttributeType, ValidationStatus, ValidationSource
from collector_manager.enums import URLStatus
from core.DTOs.URLHTMLCycleInfo import URLHTMLCycleInfo
from core.DTOs.URLRelevanceHuggingfaceCycleInfo import URLRelevanceHuggingfaceCycleInfo
from html_tag_collector.DataClassTags import ResponseHTMLInfo
from html_tag_collector.ResponseParser import HTMLResponseParser
from html_tag_collector.URLRequestInterface import URLRequestInterface
from hugging_face.HuggingFaceInterface import HuggingFaceInterface
from label_studio_interface.LabelStudioAPIManager import LabelStudioAPIManager
from util.huggingface_api_manager import HuggingfaceInterface

class HTMLContentInfoGetter:

    def __init__(self, response_html_info: ResponseHTMLInfo, url_id: int):
        self.response_html_info = response_html_info
        self.url_id = url_id
        self.html_content_infos = []

    def get_all_html_content(self) -> list[URLHTMLContentInfo]:
        for content_type in HTMLContentType:
            self.add_html_content(content_type)
        return self.html_content_infos

    def add_html_content(self, content_type: HTMLContentType):
        lower_str = content_type.value.lower()
        val = getattr(self.response_html_info, lower_str)
        if val is None or val.strip() == "":
            return
        uhci = URLHTMLContentInfo(
            url_id=self.url_id,
            content_type=content_type,
            content=val
        )
        self.html_content_infos.append(uhci)

class URLRelevanceHuggingfaceCycler:

    def __init__(
            self,
            adb_client: AsyncDatabaseClient,
            huggingface_interface: HuggingFaceInterface
    ):
        self.adb_client = adb_client
        self.huggingface_interface = huggingface_interface

    def cycle(self):
        # Get pending urls from Source Collector
        # with HTML data and without Relevancy Metadata
        cycle_infos = self.get_pending_url_info()
        # Pipe into Huggingface
        self.add_huggingface_relevancy(cycle_infos)

        # Put results into Database
        self.put_results_into_database(cycle_infos)

    def put_results_into_database(self, cycle_infos):
        url_metadatas = []
        for cycle_info in cycle_infos:
            url_metadata = URLMetadataInfo(
                url_id=cycle_info.url_info.url_id,
                attribute=URLAttributeType.RELEVANT,
                value=cycle_info.relevant,
                validation_status=ValidationStatus.PENDING_LABEL_STUDIO,
                validation_source=ValidationSource.MACHINE_LEARNING
            )
            url_metadatas.append(url_metadata)
        self.adb_client.add_url_metadatas(url_metadatas)

    def add_huggingface_relevancy(self, cycle_infos):
        urls = [cycle_info.url_info.url for cycle_info in cycle_infos]
        results = self.huggingface_interface.get_url_relevancy(urls)
        for cycle_info, result in zip(cycle_infos, results):
            cycle_info.relevant = result

    def get_pending_url_info(self):
        cycle_infos = []
        pending_urls: list[URLInfo] = self.adb_client.get_urls_with_html_data_and_no_relevancy_metadata()
        for url_info in pending_urls:
            cycle_info = URLRelevanceHuggingfaceCycleInfo(
                url_info=url_info
            )
            cycle_infos.append(cycle_info)
        return cycle_infos


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





class AsyncCore:

    def __init__(
            self,
            adb_client: AsyncDatabaseClient,
            label_studio_api_manager: LabelStudioAPIManager,
            huggingface_interface: HuggingfaceInterface,
            url_request_interface: URLRequestInterface,
            html_parser: HTMLResponseParser
    ):
        self.adb_client = adb_client
        self.label_studio_api_manager = label_studio_api_manager
        self.huggingface_interface = huggingface_interface
        self.url_request_interface = url_request_interface
        self.html_parser = html_parser

    async def run_url_html_cycle(self):
        cycler = URLHTMLCycler(
            adb_client=self.adb_client,
            url_request_interface=self.url_request_interface,
            html_parser=self.html_parser
        )
        await cycler.cycle()




    async def process(self):
        await self.relevant_to_label_studio()

    async def relevant_to_label_studio(self):
        """
        Pipelines url relevancy scores to Huggingface,
        then label studio,
        adding URL metadata to database
        """
        url_metadata = await self.adb_client.get_url_metadata_by_status(
            url_status=URLStatus.PENDING
        )