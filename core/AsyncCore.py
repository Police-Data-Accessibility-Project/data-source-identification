from collector_db.AsyncDatabaseClient import AsyncDatabaseClient
from collector_manager.enums import URLStatus
from label_studio_interface.LabelStudioAPIManager import LabelStudioAPIManager
from util.huggingface_api_manager import HuggingFaceAPIManager


class AsyncCore:

    def __init__(
            self,
            adb_client: AsyncDatabaseClient,
            label_studio_api_manager: LabelStudioAPIManager,
            huggingface_api_manager: HuggingFaceAPIManager
    ):
        self.adb_client = adb_client
        self.label_studio_api_manager = label_studio_api_manager
        self.huggingface_api_manager = huggingface_api_manager

    async def process(self):
        await self.relevant_to_label_studio()

    async def relevant_to_label_studio(self):
        """
        Pipelines url relevancy scores to Huggingface,
        then label studio,
        adding URL metadata to database
        """
        url_metadata = await self.adb_client.get_url_metadata_by_status(
            url_status=URLStatus.PENDING
        )