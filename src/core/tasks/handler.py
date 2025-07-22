import logging

from discord_poster import DiscordPoster

from src.core.enums import BatchStatus
from src.core.tasks.base.run_info import TaskOperatorRunInfo
from src.core.tasks.dtos.run_info import URLTaskOperatorRunInfo
from src.core.tasks.url.enums import TaskOperatorOutcome
from src.db.client.async_ import AsyncDatabaseClient
from src.db.enums import TaskType


class TaskHandler:

    def __init__(
        self,
        adb_client: AsyncDatabaseClient,
        discord_poster: DiscordPoster
    ):
        self.adb_client = adb_client
        self.discord_poster = discord_poster

        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.StreamHandler())
        self.logger.setLevel(logging.INFO)


    async def post_to_discord(self, message: str):
        self.discord_poster.post_to_discord(message=message)

    async def initiate_task_in_db(self, task_type: TaskType) -> int:  #
        self.logger.info(f"Initiating {task_type.value} Task")
        task_id = await self.adb_client.initiate_task(task_type=task_type)
        return task_id

    async def handle_outcome(self, run_info: TaskOperatorRunInfo):  #
        match run_info.outcome:
            case TaskOperatorOutcome.ERROR:
                await self.handle_task_error(run_info)
            case TaskOperatorOutcome.SUCCESS:
                await self.adb_client.update_task_status(
                    task_id=run_info.task_id,
                    status=BatchStatus.READY_TO_LABEL
                )

    async def handle_task_error(self, run_info: TaskOperatorRunInfo):  #
        await self.adb_client.update_task_status(
            task_id=run_info.task_id,
            status=BatchStatus.ERROR)
        await self.adb_client.add_task_error(
            task_id=run_info.task_id,
            error=run_info.message
        )
        self.discord_poster.post_to_discord(
            message=f"Task {run_info.task_id} ({run_info.task_type.value}) failed with error.")

    async def link_urls_to_task(self, task_id: int, url_ids: list[int]):
        await self.adb_client.link_urls_to_task(
            task_id=task_id,
            url_ids=url_ids
        )