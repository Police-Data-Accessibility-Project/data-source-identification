from itertools import count

from src.core.tasks.scheduled.templates.operator import ScheduledTaskOperatorBase
from src.db.client.async_ import AsyncDatabaseClient
from src.db.enums import TaskType
from src.external.huggingface.hub.client import HuggingFaceHubClient


class PushToHuggingFaceTaskOperator(ScheduledTaskOperatorBase):

    @property
    def task_type(self) -> TaskType:
        return TaskType.PUSH_TO_HUGGINGFACE

    def __init__(
        self,
        adb_client: AsyncDatabaseClient,
        hf_client: HuggingFaceHubClient
    ):
        super().__init__(adb_client)
        self.hf_client = hf_client

    async def inner_task_logic(self):
        # Check if any valid urls have been updated
        valid_urls_updated = await self.adb_client.check_valid_urls_updated()
        print(f"Valid urls updated: {valid_urls_updated}")
        if not valid_urls_updated:
            print("No valid urls updated, skipping.")
            return


        # Otherwise, push to huggingface
        run_dt = await self.adb_client.get_current_database_time()
        for idx in count(start=1):
            outputs = await self.adb_client.get_data_sources_raw_for_huggingface(page=idx)
            if len(outputs) == 0:
                break
            self.hf_client.push_data_sources_raw_to_hub(outputs, idx=idx)

        await self.adb_client.set_hugging_face_upload_state(run_dt.replace(tzinfo=None))
