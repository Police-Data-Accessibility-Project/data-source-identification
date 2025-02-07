import logging

from aiohttp import ClientSession

from agency_identifier.MuckrockAPIInterface import MuckrockAPIInterface
from collector_db.AsyncDatabaseClient import AsyncDatabaseClient
from collector_db.DTOs.TaskInfo import TaskInfo
from collector_db.DTOs.URLAnnotationInfo import URLAnnotationInfo
from collector_db.enums import TaskType, URLMetadataAttributeType
from core.DTOs.GetNextURLForAgencyAnnotationResponse import GetNextURLForAgencyAnnotationResponse, \
    URLAgencyAnnotationPostInfo
from core.DTOs.GetNextURLForAnnotationResponse import GetNextURLForAnnotationResponse
from core.DTOs.GetTasksResponse import GetTasksResponse
from core.DTOs.GetURLsResponseInfo import GetURLsResponseInfo
from core.DTOs.AnnotationRequestInfo import AnnotationRequestInfo
from core.classes.AgencyIdentificationTaskOperator import AgencyIdentificationTaskOperator
from core.classes.URLHTMLTaskOperator import URLHTMLTaskOperator
from core.classes.URLRecordTypeTaskOperator import URLRecordTypeTaskOperator
from core.classes.URLRelevanceHuggingfaceTaskOperator import URLRelevanceHuggingfaceTaskOperator
from core.enums import BatchStatus, SuggestionType
from html_tag_collector.DataClassTags import convert_to_response_html_info
from html_tag_collector.ResponseParser import HTMLResponseParser
from html_tag_collector.URLRequestInterface import URLRequestInterface
from hugging_face.HuggingFaceInterface import HuggingFaceInterface
from llm_api_logic.OpenAIRecordClassifier import OpenAIRecordClassifier
from pdap_api_client.AccessManager import AccessManager
from pdap_api_client.PDAPClient import PDAPClient
from util.helper_functions import get_from_env


class AsyncCore:

    def __init__(
            self,
            adb_client: AsyncDatabaseClient,
            huggingface_interface: HuggingFaceInterface,
            url_request_interface: URLRequestInterface,
            html_parser: HTMLResponseParser,
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
            classifier=OpenAIRecordClassifier()
        )
        await operator.run_task()

    async def run_agency_identification_task(self):
        self.logger.info("Running Agency Identification Task")
        async with ClientSession() as session:
            pdap_client = PDAPClient(
                access_manager=AccessManager(
                    email=get_from_env("PDAP_EMAIL"),
                    password=get_from_env("PDAP_PASSWORD"),
                    api_key=get_from_env("PDAP_API_KEY"),
                    session=session
                ),
            )
            muckrock_api_interface = MuckrockAPIInterface(session=session)
            operator = AgencyIdentificationTaskOperator(
                adb_client=self.adb_client,
                pdap_client=pdap_client,
                muckrock_api_interface=muckrock_api_interface
            )
            await operator.run_task()

    async def run_tasks(self):
        await self.run_url_html_task()
        await self.run_url_relevance_huggingface_task()
        await self.run_url_record_type_task()
        await self.run_agency_identification_task()

    async def convert_to_annotation_request_info(self, url_info: URLAnnotationInfo) -> AnnotationRequestInfo:
        response_html_info = convert_to_response_html_info(
            html_content_infos=url_info.html_infos
        )

        return AnnotationRequestInfo(
            url=url_info.url,
            metadata_id=url_info.metadata_id,
            html_info=response_html_info,
            suggested_value=url_info.suggested_value
        )

    async def get_next_url_for_annotation(self, user_id: int, metadata_type: URLMetadataAttributeType) -> GetNextURLForAnnotationResponse:
        response = GetNextURLForAnnotationResponse()
        ua_info: URLAnnotationInfo = await self.adb_client.get_next_url_for_annotation(
            user_id=user_id,
            metadata_type=metadata_type
        )
        if ua_info is None:
            return response
        # Format result
        result = await self.convert_to_annotation_request_info(url_info=ua_info)
        response.next_annotation = result
        return response

    async def submit_and_get_next_url_for_annotation(
            self,
            user_id: int,
            metadata_id: int,
            annotation: str,
            metadata_type: URLMetadataAttributeType
    ) -> GetNextURLForAnnotationResponse:
        await self.submit_url_annotation(
            user_id=user_id,
            metadata_id=metadata_id,
            annotation=annotation,
            metadata_type=metadata_type
        )
        result = await self.get_next_url_for_annotation(
            user_id=user_id,
            metadata_type=metadata_type
        )
        return result

    async def submit_url_annotation(
            self,
            user_id: int,
            metadata_id: int,
            annotation: str,
            metadata_type: URLMetadataAttributeType
    ) -> GetNextURLForAnnotationResponse:
        await self.adb_client.add_relevance_annotation(
            user_id=user_id,
            metadata_id=metadata_id,
            annotation=annotation)
        return await self.get_next_url_for_annotation(user_id=user_id, metadata_type=metadata_type)

    async def get_urls(self, page: int, errors: bool) -> GetURLsResponseInfo:
        return await self.adb_client.get_urls(page=page, errors=errors)

    async def get_task_info(self, task_id: int) -> TaskInfo:
        return await self.adb_client.get_task_info(task_id=task_id)

    async def get_tasks(self, page: int, task_type: TaskType, task_status: BatchStatus) -> GetTasksResponse:
        return await self.adb_client.get_tasks(page=page, task_type=task_type, task_status=task_status)

    async def get_next_url_agency_for_annotation(
            self,
            user_id: int
    ) -> GetNextURLForAgencyAnnotationResponse:
        return await self.adb_client.get_next_url_agency_for_annotation(user_id=user_id)

    async def submit_url_agency_annotation(
            self,
            user_id: int,
            url_id: int,
            agency_post_info: URLAgencyAnnotationPostInfo
    ) -> GetNextURLForAgencyAnnotationResponse:
        if agency_post_info.suggested_agency == "NEW":
            suggestion_type = SuggestionType.NEW_AGENCY
            agency_suggestion_id = None
        else:
            suggestion_type = SuggestionType.MANUAL_SUGGESTION
            agency_suggestion_id = agency_post_info.suggested_agency
        return await self.adb_client.submit_url_agency_annotation(
            user_id=user_id,
            url_id=url_id,
            suggestion_type=suggestion_type,
            agency_suggestion_id=agency_suggestion_id
        )
