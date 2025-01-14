from collector_db.AsyncDatabaseClient import AsyncDatabaseClient
from label_studio_interface.LabelStudioAPIManager import LabelStudioAPIManager


class URLRelevanceToLabelStudioCycler:

    def __init__(
            self,
            adb_client: AsyncDatabaseClient,
            label_studio_api_manager: LabelStudioAPIManager
    ):
        self.adb_client = adb_client
        self.label_studio_api_manager = label_studio_api_manager

    async def cycle(self):
        # Get max 100 Pending URLs from Source Collector
        # with URL Metadata Relevant
        # Attribute validation status Pending Label Studio

        # Pipe into label studio

        # Update relevant URLMetadata entry with validation status In Label Studio

        raise NotImplementedError
