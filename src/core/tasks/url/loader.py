"""
The task loader loads task a task operator and all dependencies.
"""

from src.collectors.source_collectors.muckrock.api_interface.core import MuckrockAPIInterface
from src.core.tasks.url.operators.agency_identification.core import AgencyIdentificationTaskOperator
from src.core.tasks.url.operators.agency_identification.subtasks.loader import AgencyIdentificationSubtaskLoader
from src.core.tasks.url.operators.auto_relevant.core import URLAutoRelevantTaskOperator
from src.core.tasks.url.operators.base import URLTaskOperatorBase
from src.core.tasks.url.operators.probe.core import URLProbeTaskOperator
from src.core.tasks.url.operators.probe_404.core import URL404ProbeTaskOperator
from src.core.tasks.url.operators.record_type.core import URLRecordTypeTaskOperator
from src.core.tasks.url.operators.record_type.llm_api.record_classifier.openai import OpenAIRecordClassifier
from src.core.tasks.url.operators.submit_approved.core import SubmitApprovedURLTaskOperator
from src.core.tasks.url.operators.duplicate.core import URLDuplicateTaskOperator
from src.core.tasks.url.operators.html.core import URLHTMLTaskOperator
from src.core.tasks.url.operators.html.scraper.parser.core import HTMLResponseParser
from src.external.url_request.core import URLRequestInterface
from src.core.tasks.url.operators.misc_metadata.core import URLMiscellaneousMetadataTaskOperator
from src.db.client.async_ import AsyncDatabaseClient
from src.external.huggingface.inference.client import HuggingFaceInferenceClient
from src.external.pdap.client import PDAPClient


class URLTaskOperatorLoader:

    def __init__(
            self,
            adb_client: AsyncDatabaseClient,
            url_request_interface: URLRequestInterface,
            html_parser: HTMLResponseParser,
            pdap_client: PDAPClient,
            muckrock_api_interface: MuckrockAPIInterface,
            hf_inference_client: HuggingFaceInferenceClient
    ):
        # Dependencies
        self.adb_client = adb_client
        self.url_request_interface = url_request_interface
        self.html_parser = html_parser

        # External clients and interfaces
        self.pdap_client = pdap_client
        self.muckrock_api_interface = muckrock_api_interface
        self.hf_inference_client = hf_inference_client

    async def get_url_html_task_operator(self):
        operator = URLHTMLTaskOperator(
            adb_client=self.adb_client,
            url_request_interface=self.url_request_interface,
            html_parser=self.html_parser
        )
        return operator

    async def get_url_record_type_task_operator(self):
        operator = URLRecordTypeTaskOperator(
            adb_client=self.adb_client,
            classifier=OpenAIRecordClassifier()
        )
        return operator

    async def get_agency_identification_task_operator(self):
        operator = AgencyIdentificationTaskOperator(
            adb_client=self.adb_client,
            loader=AgencyIdentificationSubtaskLoader(
                pdap_client=self.pdap_client,
                muckrock_api_interface=self.muckrock_api_interface
            )
        )
        return operator

    async def get_submit_approved_url_task_operator(self):
        operator = SubmitApprovedURLTaskOperator(
            adb_client=self.adb_client,
            pdap_client=self.pdap_client
        )
        return operator

    async def get_url_miscellaneous_metadata_task_operator(self):
        operator = URLMiscellaneousMetadataTaskOperator(
            adb_client=self.adb_client
        )
        return operator

    async def get_url_duplicate_task_operator(self):
        operator = URLDuplicateTaskOperator(
            adb_client=self.adb_client,
            pdap_client=self.pdap_client
        )
        return operator

    async def get_url_404_probe_task_operator(self):
        operator = URL404ProbeTaskOperator(
            adb_client=self.adb_client,
            url_request_interface=self.url_request_interface
        )
        return operator

    async def get_url_auto_relevance_task_operator(self):
        operator = URLAutoRelevantTaskOperator(
            adb_client=self.adb_client,
            hf_client=self.hf_inference_client
        )
        return operator

    async def get_url_probe_task_operator(self):
        operator = URLProbeTaskOperator(
            adb_client=self.adb_client,
            url_request_interface=self.url_request_interface
        )
        return operator

    async def get_task_operators(self) -> list[URLTaskOperatorBase]:
        return [
            await self.get_url_probe_task_operator(),
            await self.get_url_html_task_operator(),
            await self.get_url_duplicate_task_operator(),
            await self.get_url_404_probe_task_operator(),
            await self.get_url_record_type_task_operator(),
            await self.get_agency_identification_task_operator(),
            await self.get_url_miscellaneous_metadata_task_operator(),
            await self.get_submit_approved_url_task_operator(),
            await self.get_url_auto_relevance_task_operator()
        ]
