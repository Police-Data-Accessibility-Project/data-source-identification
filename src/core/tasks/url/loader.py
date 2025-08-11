"""
The task loader loads task a task operator and all dependencies.
"""

from environs import Env

from src.collectors.impl.muckrock.api_interface.core import MuckrockAPIInterface
from src.core.tasks.url.models.entry import URLTaskEntry
from src.core.tasks.url.operators.agency_identification.core import AgencyIdentificationTaskOperator
from src.core.tasks.url.operators.agency_identification.subtasks.loader import AgencyIdentificationSubtaskLoader
from src.core.tasks.url.operators.auto_relevant.core import URLAutoRelevantTaskOperator
from src.core.tasks.url.operators.duplicate.core import URLDuplicateTaskOperator
from src.core.tasks.url.operators.html.core import URLHTMLTaskOperator
from src.core.tasks.url.operators.html.scraper.parser.core import HTMLResponseParser
from src.core.tasks.url.operators.misc_metadata.core import URLMiscellaneousMetadataTaskOperator
from src.core.tasks.url.operators.probe.core import URLProbeTaskOperator
from src.core.tasks.url.operators.probe_404.core import URL404ProbeTaskOperator
from src.core.tasks.url.operators.record_type.core import URLRecordTypeTaskOperator
from src.core.tasks.url.operators.record_type.llm_api.record_classifier.openai import OpenAIRecordClassifier
from src.core.tasks.url.operators.submit_approved.core import SubmitApprovedURLTaskOperator
from src.db.client.async_ import AsyncDatabaseClient
from src.external.huggingface.inference.client import HuggingFaceInferenceClient
from src.external.pdap.client import PDAPClient
from src.external.url_request.core import URLRequestInterface


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
        self.env = Env()

        # External clients and interfaces
        self.pdap_client = pdap_client
        self.muckrock_api_interface = muckrock_api_interface
        self.hf_inference_client = hf_inference_client

    async def _get_url_html_task_operator(self) -> URLTaskEntry:
        operator = URLHTMLTaskOperator(
            adb_client=self.adb_client,
            url_request_interface=self.url_request_interface,
            html_parser=self.html_parser
        )
        return URLTaskEntry(
            operator=operator,
            enabled=self.env.bool(
                "URL_HTML_TASK_FLAG",
                default=True
            )
        )

    async def _get_url_record_type_task_operator(self) -> URLTaskEntry:
        operator = URLRecordTypeTaskOperator(
            adb_client=self.adb_client,
            classifier=OpenAIRecordClassifier()
        )
        return URLTaskEntry(
            operator=operator,
            enabled=self.env.bool(
                "URL_RECORD_TYPE_TASK_FLAG",
                default=True
            )
        )

    async def _get_agency_identification_task_operator(self) -> URLTaskEntry:
        operator = AgencyIdentificationTaskOperator(
            adb_client=self.adb_client,
            loader=AgencyIdentificationSubtaskLoader(
                pdap_client=self.pdap_client,
                muckrock_api_interface=self.muckrock_api_interface
            )
        )
        return URLTaskEntry(
            operator=operator,
            enabled=self.env.bool(
                "URL_AGENCY_IDENTIFICATION_TASK_FLAG",
                default=True
            )
        )

    async def _get_submit_approved_url_task_operator(self) -> URLTaskEntry:
        operator = SubmitApprovedURLTaskOperator(
            adb_client=self.adb_client,
            pdap_client=self.pdap_client
        )
        return URLTaskEntry(
            operator=operator,
            enabled=self.env.bool(
                "URL_SUBMIT_APPROVED_TASK_FLAG",
                default=True
            )
        )

    async def _get_url_miscellaneous_metadata_task_operator(self) -> URLTaskEntry:
        operator = URLMiscellaneousMetadataTaskOperator(
            adb_client=self.adb_client
        )
        return URLTaskEntry(
            operator=operator,
            enabled=self.env.bool(
                "URL_MISC_METADATA_TASK_FLAG",
                default=True
            )
        )

    async def _get_url_duplicate_task_operator(self) -> URLTaskEntry:
        operator = URLDuplicateTaskOperator(
            adb_client=self.adb_client,
            pdap_client=self.pdap_client
        )
        return URLTaskEntry(
            operator=operator,
            enabled=self.env.bool(
                "URL_DUPLICATE_TASK_FLAG",
                default=True
            )
        )

    async def _get_url_404_probe_task_operator(self) -> URLTaskEntry:
        operator = URL404ProbeTaskOperator(
            adb_client=self.adb_client,
            url_request_interface=self.url_request_interface
        )
        return URLTaskEntry(
            operator=operator,
            enabled=self.env.bool(
                "URL_404_PROBE_TASK_FLAG",
                default=True
            )
        )

    async def _get_url_auto_relevance_task_operator(self) -> URLTaskEntry:
        operator = URLAutoRelevantTaskOperator(
            adb_client=self.adb_client,
            hf_client=self.hf_inference_client
        )
        return URLTaskEntry(
            operator=operator,
            enabled=self.env.bool(
                "URL_AUTO_RELEVANCE_TASK_FLAG",
                default=True
            )
        )

    async def _get_url_probe_task_operator(self) -> URLTaskEntry:
        operator = URLProbeTaskOperator(
            adb_client=self.adb_client,
            url_request_interface=self.url_request_interface
        )
        return URLTaskEntry(
            operator=operator,
            enabled=self.env.bool(
                "URL_PROBE_TASK_FLAG",
                default=True
            )
        )

    async def load_entries(self) -> list[URLTaskEntry]:
        return [
            await self._get_url_probe_task_operator(),
            await self._get_url_html_task_operator(),
            await self._get_url_duplicate_task_operator(),
            await self._get_url_404_probe_task_operator(),
            await self._get_url_record_type_task_operator(),
            await self._get_agency_identification_task_operator(),
            await self._get_url_miscellaneous_metadata_task_operator(),
            await self._get_submit_approved_url_task_operator(),
            await self._get_url_auto_relevance_task_operator()
        ]
