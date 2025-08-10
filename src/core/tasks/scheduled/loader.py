from environs import Env

from src.core.core import AsyncCore
from src.core.tasks.scheduled.enums import IntervalEnum
from src.core.tasks.scheduled.impl.backlog.operator import PopulateBacklogSnapshotTaskOperator
from src.core.tasks.scheduled.impl.delete_logs.operator import DeleteOldLogsTaskOperator
from src.core.tasks.scheduled.impl.huggingface.operator import PushToHuggingFaceTaskOperator
from src.core.tasks.scheduled.impl.run_url_tasks.operator import RunURLTasksTaskOperator
from src.core.tasks.scheduled.impl.sync.agency.operator import SyncAgenciesTaskOperator
from src.core.tasks.scheduled.impl.sync.data_sources.operator import SyncDataSourcesTaskOperator
from src.core.tasks.scheduled.models.entry import ScheduledTaskEntry
from src.db.client.async_ import AsyncDatabaseClient
from src.external.huggingface.hub.client import HuggingFaceHubClient
from src.external.pdap.client import PDAPClient


class ScheduledTaskOperatorLoader:

    def __init__(
            self,
            async_core: AsyncCore,
            adb_client: AsyncDatabaseClient,
            pdap_client: PDAPClient,
            hf_client: HuggingFaceHubClient
    ):
        # Dependencies
        self.async_core = async_core
        self.adb_client = adb_client
        self.pdap_client = pdap_client
        self.hf_client = hf_client

        self.env = Env()
        self.env.read_env()


    async def load_entries(self) -> list[ScheduledTaskEntry]:
        scheduled_task_flag = self.env.bool("SCHEDULED_TASKS_FLAG", default=True)
        if not scheduled_task_flag:
            print("Scheduled tasks are disabled.")
            return []


        return [
            ScheduledTaskEntry(
                operator=RunURLTasksTaskOperator(async_core=self.async_core),
                interval=IntervalEnum.HOURLY,
                enabled=self.env.bool("RUN_URL_TASKS_TASK_FLAG", default=True)

            ),
            ScheduledTaskEntry(
                operator=DeleteOldLogsTaskOperator(adb_client=self.async_core.adb_client),
                interval=IntervalEnum.DAILY,
                enabled=self.env.bool("DELETE_OLD_LOGS_TASK_FLAG", default=True)
            ),
            ScheduledTaskEntry(
                operator=PopulateBacklogSnapshotTaskOperator(adb_client=self.async_core.adb_client),
                interval=IntervalEnum.DAILY,
                enabled=self.env.bool("POPULATE_BACKLOG_SNAPSHOT_TASK_FLAG", default=True)
            ),
            ScheduledTaskEntry(
                operator=SyncDataSourcesTaskOperator(
                    adb_client=self.async_core.adb_client,
                    pdap_client=self.pdap_client
                ),
                interval=IntervalEnum.DAILY,
                enabled=self.env.bool("SYNC_DATA_SOURCES_TASK_FLAG", default=True)
            ),
            ScheduledTaskEntry(
                operator=SyncAgenciesTaskOperator(
                    adb_client=self.async_core.adb_client,
                    pdap_client=self.pdap_client
                ),
                interval=IntervalEnum.DAILY,
                enabled=self.env.bool("SYNC_AGENCIES_TASK_FLAG", default=True)
            ),
            ScheduledTaskEntry(
                operator=PushToHuggingFaceTaskOperator(
                    adb_client=self.async_core.adb_client,
                    hf_client=self.hf_client
                ),
                interval=IntervalEnum.DAILY,
                enabled=self.env.bool(
                    "PUSH_TO_HUGGING_FACE_TASK_FLAG",
                    default=True
                )
            )

        ]
