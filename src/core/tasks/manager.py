import logging

from src.api.endpoints.task.dtos.get.tasks import GetTasksResponse
from src.collectors.source_collectors.muckrock.api_interface.core import MuckrockAPIInterface
from src.core.tasks.operators.agency_identification.core import AgencyIdentificationTaskOperator
from src.core.tasks.operators.agency_sync.core import SyncAgenciesTaskOperator
from src.core.tasks.operators.base import TaskOperatorBase
from src.core.tasks.operators.submit_approved_url.core import SubmitApprovedURLTaskOperator
from src.core.tasks.operators.url_404_probe.core import URL404ProbeTaskOperator
from src.core.tasks.operators.url_duplicate.core import URLDuplicateTaskOperator
from src.core.tasks.operators.url_html.core import URLHTMLTaskOperator
from src.core.tasks.operators.url_html.scraper.parser.core import HTMLResponseParser
from src.core.tasks.operators.url_html.scraper.request_interface.core import URLRequestInterface
from src.core.tasks.operators.url_miscellaneous_metadata.core import URLMiscellaneousMetadataTaskOperator
from src.db.client.async_ import AsyncDatabaseClient
from src.api.endpoints.task.dtos.get.task import TaskInfo
from src.db.enums import TaskType
from src.core.tasks.dtos.run_info import TaskOperatorRunInfo
from src.core.tasks.enums import TaskOperatorOutcome
from src.core.function_trigger import FunctionTrigger
from src.core.tasks.operators.record_type.core import URLRecordTypeTaskOperator
from src.core.enums import BatchStatus
from src.core.tasks.operators.record_type.llm_api.record_classifier.openai import OpenAIRecordClassifier
from src.pdap_api.client import PDAPClient
from discord_poster import DiscordPoster

TASK_REPEAT_THRESHOLD = 20

class TaskManager:

    def __init__(
            self,
            adb_client: AsyncDatabaseClient,
            url_request_interface: URLRequestInterface,
            html_parser: HTMLResponseParser,
            discord_poster: DiscordPoster,
            pdap_client: PDAPClient,
            muckrock_api_interface: MuckrockAPIInterface
    ):
        # Dependencies
        self.adb_client = adb_client
        self.pdap_client = pdap_client
        self.url_request_interface = url_request_interface
        self.html_parser = html_parser
        self.discord_poster = discord_poster
        self.muckrock_api_interface = muckrock_api_interface

        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.StreamHandler())
        self.logger.setLevel(logging.INFO)
        self.task_trigger = FunctionTrigger(self.run_tasks)
        self.task_status: TaskType = TaskType.IDLE

    #region Task Operators
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
            pdap_client=self.pdap_client,
            muckrock_api_interface=self.muckrock_api_interface
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

    async def get_sync_agencies_task_operator(self):
        operator = SyncAgenciesTaskOperator(
            adb_client=self.adb_client,
            pdap_client=self.pdap_client
        )
        return operator

    async def get_task_operators(self) -> list[TaskOperatorBase]:
        return [
            await self.get_url_html_task_operator(),
            await self.get_url_duplicate_task_operator(),
            await self.get_url_404_probe_task_operator(),
            await self.get_url_record_type_task_operator(),
            await self.get_agency_identification_task_operator(),
            await self.get_url_miscellaneous_metadata_task_operator(),
            await self.get_submit_approved_url_task_operator(),
            await self.get_sync_agencies_task_operator()
        ]

    #endregion

    #region Tasks
    async def set_task_status(self, task_type: TaskType):
        self.task_status = task_type

    async def run_tasks(self):
        operators = await self.get_task_operators()
        for operator in operators:
            count = 0
            await self.set_task_status(task_type=operator.task_type)

            meets_prereq = await operator.meets_task_prerequisites()
            while meets_prereq:
                print(f"Running {operator.task_type.value} Task")
                if count > TASK_REPEAT_THRESHOLD:
                    message = f"Task {operator.task_type.value} has been run more than {TASK_REPEAT_THRESHOLD} times in a row. Task loop terminated."
                    print(message)
                    self.discord_poster.post_to_discord(message=message)
                    break
                task_id = await self.initiate_task_in_db(task_type=operator.task_type)
                run_info: TaskOperatorRunInfo = await operator.run_task(task_id)
                await self.conclude_task(run_info)
                if run_info.outcome == TaskOperatorOutcome.ERROR:
                    break
                count += 1
                meets_prereq = await operator.meets_task_prerequisites()
        await self.set_task_status(task_type=TaskType.IDLE)

    async def trigger_task_run(self):
        await self.task_trigger.trigger_or_rerun()


    async def conclude_task(self, run_info):
        await self.adb_client.link_urls_to_task(
            task_id=run_info.task_id,
            url_ids=run_info.linked_url_ids
        )
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
                    status=BatchStatus.READY_TO_LABEL
                )

    async def handle_task_error(self, run_info: TaskOperatorRunInfo):
        await self.adb_client.update_task_status(
            task_id=run_info.task_id,
            status=BatchStatus.ERROR)
        await self.adb_client.add_task_error(
            task_id=run_info.task_id,
            error=run_info.message
        )
        self.discord_poster.post_to_discord(
            message=f"Task {run_info.task_id} ({self.task_status.value}) failed with error.")

    async def get_task_info(self, task_id: int) -> TaskInfo:
        return await self.adb_client.get_task_info(task_id=task_id)

    async def get_tasks(
            self,
            page: int,
            task_type: TaskType,
            task_status: BatchStatus
    ) -> GetTasksResponse:
        return await self.adb_client.get_tasks(
            page=page,
            task_type=task_type,
            task_status=task_status
        )


    #endregion



