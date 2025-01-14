from collector_db.AsyncDatabaseClient import AsyncDatabaseClient
from collector_manager.enums import URLStatus
from core.classes.URLHTMLCycler import URLHTMLCycler
from core.classes.URLRelevanceHuggingfaceCycler import URLRelevanceHuggingfaceCycler
from html_tag_collector.ResponseParser import HTMLResponseParser
from html_tag_collector.URLRequestInterface import URLRequestInterface
from hugging_face.HuggingFaceInterface import HuggingFaceInterface
from label_studio_interface.LabelStudioAPIManager import LabelStudioAPIManager


class AsyncCore:

    def __init__(
            self,
            adb_client: AsyncDatabaseClient,
            label_studio_api_manager: LabelStudioAPIManager,
            huggingface_interface: HuggingFaceInterface,
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

    async def run_url_relevance_huggingface_cycle(self):
        cycler = URLRelevanceHuggingfaceCycler(
            adb_client=self.adb_client,
            huggingface_interface=self.huggingface_interface
        )
        cycler.cycle()




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