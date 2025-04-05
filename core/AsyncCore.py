import logging
from typing import Optional

from aiohttp import ClientSession

from agency_identifier.MuckrockAPIInterface import MuckrockAPIInterface
from collector_db.AsyncDatabaseClient import AsyncDatabaseClient
from collector_db.DTOs.TaskInfo import TaskInfo
from collector_db.DTOs.URLAnnotationInfo import URLAnnotationInfo
from collector_db.enums import TaskType, URLMetadataAttributeType
from core.DTOs.FinalReviewApprovalInfo import FinalReviewApprovalInfo
from core.DTOs.GetNextRecordTypeAnnotationResponseInfo import GetNextRecordTypeAnnotationResponseOuterInfo
from core.DTOs.GetNextRelevanceAnnotationResponseInfo import GetNextRelevanceAnnotationResponseOuterInfo
from core.DTOs.GetNextURLForAgencyAnnotationResponse import GetNextURLForAgencyAnnotationResponse, \
    URLAgencyAnnotationPostInfo
from core.DTOs.GetNextURLForAnnotationResponse import GetNextURLForAnnotationResponse
from core.DTOs.GetTasksResponse import GetTasksResponse
from core.DTOs.GetURLsResponseInfo import GetURLsResponseInfo
from core.DTOs.AnnotationRequestInfo import AnnotationRequestInfo
from core.DTOs.TaskOperatorRunInfo import TaskOperatorRunInfo, TaskOperatorOutcome
from core.classes.AgencyIdentificationTaskOperator import AgencyIdentificationTaskOperator
from core.classes.TaskOperatorBase import TaskOperatorBase
from core.classes.URLHTMLTaskOperator import URLHTMLTaskOperator
from core.classes.URLMiscellaneousMetadataTaskOperator import URLMiscellaneousMetadataTaskOperator
from core.classes.URLRecordTypeTaskOperator import URLRecordTypeTaskOperator
from core.classes.URLRelevanceHuggingfaceTaskOperator import URLRelevanceHuggingfaceTaskOperator
from core.enums import BatchStatus, SuggestionType, RecordType
from html_tag_collector.DataClassTags import convert_to_response_html_info
from html_tag_collector.ResponseParser import HTMLResponseParser
from html_tag_collector.URLRequestInterface import URLRequestInterface
from hugging_face.HuggingFaceInterface import HuggingFaceInterface
from llm_api_logic.OpenAIRecordClassifier import OpenAIRecordClassifier
from pdap_api_client.AccessManager import AccessManager
from pdap_api_client.PDAPClient import PDAPClient
from security_manager.SecurityManager import AccessInfo
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
        self.logger.addHandler(logging.StreamHandler())
        self.logger.setLevel(logging.INFO)


    async def get_urls(self, page: int, errors: bool) -> GetURLsResponseInfo:
        return await self.adb_client.get_urls(page=page, errors=errors)


    #region Task Operators
    async def get_url_html_task_operator(self):
        self.logger.info("Running URL HTML Task")
        operator = URLHTMLTaskOperator(
            adb_client=self.adb_client,
            url_request_interface=self.url_request_interface,
            html_parser=self.html_parser
        )
        return operator

    async def get_url_relevance_huggingface_task_operator(self):
        self.logger.info("Running URL Relevance Huggingface Task")
        operator = URLRelevanceHuggingfaceTaskOperator(
            adb_client=self.adb_client,
            huggingface_interface=self.huggingface_interface
        )
        return operator

    async def get_url_record_type_task_operator(self):
        operator = URLRecordTypeTaskOperator(
            adb_client=self.adb_client,
            classifier=OpenAIRecordClassifier()
        )
        return operator

    async def get_agency_identification_task_operator(self):
        pdap_client = PDAPClient(
            access_manager=AccessManager(
                email=get_from_env("PDAP_EMAIL"),
                password=get_from_env("PDAP_PASSWORD"),
                api_key=get_from_env("PDAP_API_KEY"),
            ),
        )
        muckrock_api_interface = MuckrockAPIInterface()
        operator = AgencyIdentificationTaskOperator(
            adb_client=self.adb_client,
            pdap_client=pdap_client,
            muckrock_api_interface=muckrock_api_interface
        )
        return operator

    async def get_url_miscellaneous_metadata_task_operator(self):
        operator = URLMiscellaneousMetadataTaskOperator(
            adb_client=self.adb_client
        )
        return operator

    async def get_task_operators(self) -> list[TaskOperatorBase]:
        return [
            await self.get_url_html_task_operator(),
            await self.get_url_relevance_huggingface_task_operator(),
            await self.get_url_record_type_task_operator(),
            await self.get_agency_identification_task_operator(),
            await self.get_url_miscellaneous_metadata_task_operator()
        ]

    #endregion

    #region Tasks
    async def run_tasks(self):
        operators = await self.get_task_operators()
        for operator in operators:
            meets_prereq = await operator.meets_task_prerequisites()
            if not meets_prereq:
                self.logger.info(f"Skipping {operator.task_type.value} Task")
                continue
            task_id = await self.initiate_task_in_db(task_type=operator.task_type)
            run_info: TaskOperatorRunInfo = await operator.run_task(task_id)
            await self.conclude_task(run_info)

    async def conclude_task(self, run_info):
        await self.adb_client.link_urls_to_task(task_id=run_info.task_id, url_ids=run_info.linked_url_ids)
        await self.handle_outcome(run_info)

    async def initiate_task_in_db(self, task_type: TaskType) -> int:
        self.logger.info(f"Initiating {task_type.value} Task")
        task_id = await self.adb_client.initiate_task(task_type=task_type)
        return task_id

    async def handle_outcome(self, run_info: TaskOperatorRunInfo):
        match run_info.outcome:
            case TaskOperatorOutcome.ERROR:
                await self.handle_task_error(run_info)
            case TaskOperatorOutcome.SUCCESS:
                await self.adb_client.update_task_status(
                    task_id=run_info.task_id,
                    status=BatchStatus.COMPLETE
                )

    async def handle_task_error(self, run_info: TaskOperatorRunInfo):
        await self.adb_client.update_task_status(task_id=run_info.task_id, status=BatchStatus.ERROR)
        await self.adb_client.add_task_error(task_id=run_info.task_id, error=run_info.message)

    async def get_task_info(self, task_id: int) -> TaskInfo:
        return await self.adb_client.get_task_info(task_id=task_id)

    async def get_tasks(self, page: int, task_type: TaskType, task_status: BatchStatus) -> GetTasksResponse:
        return await self.adb_client.get_tasks(page=page, task_type=task_type, task_status=task_status)


    #endregion

    #region Annotations and Review

    async def submit_url_relevance_annotation(
            self,
            user_id: int,
            url_id: int,
            relevant: bool
    ):
        return await self.adb_client.add_user_relevant_suggestion(
            user_id=user_id,
            url_id=url_id,
            relevant=relevant
        )

    async def get_next_url_for_relevance_annotation(
            self,
            user_id: int,
            batch_id: Optional[int]
    ) -> GetNextRelevanceAnnotationResponseOuterInfo:
        next_annotation = await self.adb_client.get_next_url_for_relevance_annotation(
            user_id=user_id,
            batch_id=batch_id
        )
        return GetNextRelevanceAnnotationResponseOuterInfo(
            next_annotation=next_annotation
        )

    async def get_next_url_for_record_type_annotation(
            self,
            user_id: int,
            batch_id: Optional[int]
    ) -> GetNextRecordTypeAnnotationResponseOuterInfo:
        next_annotation = await self.adb_client.get_next_url_for_record_type_annotation(
            user_id=user_id,
            batch_id=batch_id
        )
        return GetNextRecordTypeAnnotationResponseOuterInfo(
            next_annotation=next_annotation
        )

    async def submit_url_record_type_annotation(
            self,
            user_id: int,
            url_id: int,
            record_type: RecordType,
    ):
        await self.adb_client.add_user_record_type_suggestion(
            user_id=user_id,
            url_id=url_id,
            record_type=record_type
        )


    async def get_next_url_agency_for_annotation(
            self,
            user_id: int,
            batch_id: Optional[int]
    ) -> GetNextURLForAgencyAnnotationResponse:
        return await self.adb_client.get_next_url_agency_for_annotation(
            user_id=user_id,
            batch_id=batch_id
        )

    async def submit_url_agency_annotation(
            self,
            user_id: int,
            url_id: int,
            agency_post_info: URLAgencyAnnotationPostInfo
    ) -> GetNextURLForAgencyAnnotationResponse:
        if not agency_post_info.is_new and not agency_post_info.suggested_agency:
            raise ValueError("suggested_agency must be provided if is_new is False")

        if agency_post_info.is_new:
            agency_suggestion_id = None
        else:
            agency_suggestion_id = agency_post_info.suggested_agency
        return await self.adb_client.add_agency_manual_suggestion(
            user_id=user_id,
            url_id=url_id,
            agency_id=agency_suggestion_id,
            is_new=agency_post_info.is_new,
        )

    async def get_next_source_for_review(
            self,
            batch_id: Optional[int]
    ):
        return await self.adb_client.get_next_url_for_final_review(
            batch_id=batch_id
        )

    async def approve_url(
            self,
            approval_info: FinalReviewApprovalInfo,
            access_info: AccessInfo
    ):
        await self.adb_client.approve_url(
            approval_info=approval_info,
            user_id=access_info.user_id
        )


    async def reject_url(
            self,
            url_id: int,
            access_info: AccessInfo,
    ):
        await self.adb_client.reject_url(
            url_id=url_id,
            user_id=access_info.user_id
        )

