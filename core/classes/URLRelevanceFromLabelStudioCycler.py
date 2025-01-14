from collector_db.AsyncDatabaseClient import AsyncDatabaseClient
from label_studio_interface.LabelStudioAPIManager import LabelStudioAPIManager


class URLRelevanceFromLabelStudioCycler:

    def __init__(
            self,
            adb_client: AsyncDatabaseClient,
            label_studio_api_manager: LabelStudioAPIManager
    ):
        self.adb_client = adb_client
        self.label_studio_api_manager = label_studio_api_manager


    def cycle(self):
        raise NotImplementedError