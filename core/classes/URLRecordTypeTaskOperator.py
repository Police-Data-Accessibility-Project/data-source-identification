from collector_db.AsyncDatabaseClient import AsyncDatabaseClient
from collector_db.enums import URLMetadataAttributeType
from llm_api_logic.DeepSeekRecordClassifier import DeepSeekRecordClassifier


class URLRecordTypeTaskOperator:

    def __init__(
            self,
            adb_client: AsyncDatabaseClient,
            classifier: DeepSeekRecordClassifier
    ):
        self.adb_client = adb_client
        self.classifier = classifier

    async def run_task(self):
        # Get pending urls from Source Collector
        # with HTML data and without Record Type Metadata
        task_infos = await self.adb_client.get_pending_urls_without_html_data(
            without_metadata_attribute=URLMetadataAttributeType.RECORD_TYPE
        )


    async def get_ml_classifications(self, task_infos: list[URLRecordTypeTaskInfo]):