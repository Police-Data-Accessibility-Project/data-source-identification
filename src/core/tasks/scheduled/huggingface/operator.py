from src.core.tasks.scheduled.templates.operator import ScheduledTaskOperatorBase
from src.db.client.async_ import AsyncDatabaseClient
from src.external.huggingface.hub.client import HuggingFaceHubClient


class PushToHuggingFaceTaskOperator(ScheduledTaskOperatorBase):


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
        if not valid_urls_updated:
            return

        # Otherwise, push to huggingface

        outputs = await self.adb_client.get_data_sources_raw_for_huggingface()
        self.hf_client.push_data_sources_raw_to_hub(outputs)