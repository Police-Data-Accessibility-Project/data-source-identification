import logging

from collector_db.AsyncDatabaseClient import AsyncDatabaseClient
from collector_db.DTOs.TaskInfo import TaskInfo
from collector_db.DTOs.URLAnnotationInfo import URLAnnotationInfo
from collector_db.enums import TaskType
from core.DTOs.GetNextURLForRelevanceAnnotationResponse import GetNextURLForRelevanceAnnotationResponse
from core.DTOs.GetTasksResponse import GetTasksResponse
from core.DTOs.GetURLsResponseInfo import GetURLsResponseInfo
from core.DTOs.RelevanceAnnotationInfo import RelevanceAnnotationPostInfo
from core.DTOs.RelevanceAnnotationRequestInfo import RelevanceAnnotationRequestInfo
from core.classes.URLHTMLTaskOperator import URLHTMLTaskOperator
from core.classes.URLRecordTypeTaskOperator import URLRecordTypeTaskOperator
from core.classes.URLRelevanceHuggingfaceTaskOperator import URLRelevanceHuggingfaceTaskOperator
from core.enums import BatchStatus
from html_tag_collector.DataClassTags import convert_to_response_html_info
from html_tag_collector.ResponseParser import HTMLResponseParser
from html_tag_collector.URLRequestInterface import URLRequestInterface
from hugging_face.HuggingFaceInterface import HuggingFaceInterface
from llm_api_logic.DeepSeekRecordClassifier import DeepSeekRecordClassifier


class AsyncCore:

    def __init__(
            self,
            adb_client: AsyncDatabaseClient,
            huggingface_interface: HuggingFaceInterface,
            url_request_interface: URLRequestInterface,
            html_parser: HTMLResponseParser
    ):
        self.adb_client = adb_client
        self.huggingface_interface = huggingface_interface
        self.url_request_interface = url_request_interface
        self.html_parser = html_parser
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

    async def run_url_html_task(self):
        self.logger.info("Running URL HTML Task")
        operator = URLHTMLTaskOperator(
            adb_client=self.adb_client,
            url_request_interface=self.url_request_interface,
            html_parser=self.html_parser
        )
        await operator.run_task()

    async def run_url_relevance_huggingface_task(self):
        self.logger.info("Running URL Relevance Huggingface Task")
        operator = URLRelevanceHuggingfaceTaskOperator(
            adb_client=self.adb_client,
            huggingface_interface=self.huggingface_interface
        )
        await operator.run_task()

    async def run_url_record_type_task(self):
        self.logger.info("Running URL Record Type Task")
        operator = URLRecordTypeTaskOperator(
            adb_client=self.adb_client,
            classifier=DeepSeekRecordClassifier()
        )
        await operator.run_task()

    async def run_tasks(self):
        await self.run_url_html_task()
        await self.run_url_relevance_huggingface_task()
        await self.run_url_record_type_task()

    async def convert_to_relevance_annotation_request_info(self, url_info: URLAnnotationInfo) -> RelevanceAnnotationRequestInfo:
        response_html_info = convert_to_response_html_info(
            html_content_infos=url_info.html_infos
        )

        return RelevanceAnnotationRequestInfo(
            url=url_info.url,
            metadata_id=url_info.metadata_id,
            html_info=response_html_info
        )

    async def get_next_url_for_relevance_annotation(self, user_id: int) -> GetNextURLForRelevanceAnnotationResponse:
        response = GetNextURLForRelevanceAnnotationResponse()
        ua_info: URLAnnotationInfo = await self.adb_client.get_next_url_for_relevance_annotation(user_id=user_id)
        if ua_info is None:
            return response
        # Format result
        result = await self.convert_to_relevance_annotation_request_info(url_info=ua_info)
        response.next_annotation = result
        return response


    async def submit_url_relevance_annotation(
            self,
            user_id: int,
            metadata_id: int,
            annotation: RelevanceAnnotationPostInfo
    ) -> GetNextURLForRelevanceAnnotationResponse:
        await self.adb_client.add_relevance_annotation(
            user_id=user_id,
            metadata_id=metadata_id,
            annotation_info=annotation)
        return await self.get_next_url_for_relevance_annotation(user_id=user_id)

    async def get_urls(self, page: int, errors: bool) -> GetURLsResponseInfo:
        return await self.adb_client.get_urls(page=page, errors=errors)

    async def get_task_info(self, task_id: int) -> TaskInfo:
        return await self.adb_client.get_task_info(task_id=task_id)

    async def get_tasks(self, page: int, task_type: TaskType, task_status: BatchStatus) -> GetTasksResponse:
        return await self.adb_client.get_tasks(page=page, task_type=task_type, task_status=task_status)
