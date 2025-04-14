import logging
from typing import Optional

from agency_identifier.MuckrockAPIInterface import MuckrockAPIInterface
from collector_db.AsyncDatabaseClient import AsyncDatabaseClient
from collector_db.DTOs.TaskInfo import TaskInfo
from collector_db.enums import TaskType
from core.DTOs.GetTasksResponse import GetTasksResponse
from core.DTOs.TaskOperatorRunInfo import TaskOperatorRunInfo, TaskOperatorOutcome
from core.FunctionTrigger import FunctionTrigger
from core.classes.AgencyIdentificationTaskOperator import AgencyIdentificationTaskOperator
from core.classes.TaskOperatorBase import TaskOperatorBase
from core.classes.URLHTMLTaskOperator import URLHTMLTaskOperator
from core.classes.URLMiscellaneousMetadataTaskOperator import URLMiscellaneousMetadataTaskOperator
from core.classes.URLRecordTypeTaskOperator import URLRecordTypeTaskOperator
from core.classes.URLRelevanceHuggingfaceTaskOperator import URLRelevanceHuggingfaceTaskOperator
from core.enums import BatchStatus
from html_tag_collector.ResponseParser import HTMLResponseParser
from html_tag_collector.URLRequestInterface import URLRequestInterface
from hugging_face.HuggingFaceInterface import HuggingFaceInterface
from llm_api_logic.OpenAIRecordClassifier import OpenAIRecordClassifier
from pdap_api_client.AccessManager import AccessManager
from pdap_api_client.PDAPClient import PDAPClient
from util.DiscordNotifier import DiscordPoster
from util.helper_functions import get_from_env

TASK_REPEAT_THRESHOLD = 20

class TaskManager:

    def __init__(
            self,
            adb_client: AsyncDatabaseClient,
            huggingface_interface: HuggingFaceInterface,
            url_request_interface: URLRequestInterface,
            html_parser: HTMLResponseParser,
            discord_poster: DiscordPoster,
    ):
        self.adb_client = adb_client
        self.huggingface_interface = huggingface_interface
        self.url_request_interface = url_request_interface
        self.html_parser = html_parser
        self.discord_poster = discord_poster
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

    async def get_url_relevance_huggingface_task_operator(self):
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
    async def set_task_status(self, task_type: TaskType):
        self.task_status = task_type

    async def run_tasks(self):
        operators = await self.get_task_operators()
        count = 0
        for operator in operators:
            await self.set_task_status(task_type=operator.task_type)

            meets_prereq = await operator.meets_task_prerequisites()
            while meets_prereq:
                print(f"Running {operator.task_type.value} Task")
                if count > TASK_REPEAT_THRESHOLD:
                    self.discord_poster.post_to_discord(
                        message=f"Task {operator.task_type.value} has been run"
                                f" more than {TASK_REPEAT_THRESHOLD} times in a row. "
                                f"Task loop terminated.")
                    break
                task_id = await self.initiate_task_in_db(task_type=operator.task_type)
                run_info: TaskOperatorRunInfo = await operator.run_task(task_id)
                await self.conclude_task(run_info)
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
                    status=BatchStatus.COMPLETE
                )

    async def handle_task_error(self, run_info: TaskOperatorRunInfo):
        await self.adb_client.update_task_status(
            task_id=run_info.task_id,
            status=BatchStatus.ERROR)
        await self.adb_client.add_task_error(
            task_id=run_info.task_id,
            error=run_info.message
        )

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



