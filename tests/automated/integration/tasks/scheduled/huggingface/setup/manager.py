from tests.automated.integration.tasks.scheduled.huggingface.setup.data import ENTRIES
from tests.helpers.batch_creation_parameters.core import TestBatchCreationParameters
from tests.helpers.data_creator.core import DBDataCreator


class PushToHuggingFaceTestSetupManager:

    def __init__(self, db_data_creator: DBDataCreator):
        self.db_data_creator = db_data_creator
        self.entries = ENTRIES
        # Connects a URL ID to the expectation that it will be picked up
        self.id_to_picked_up: dict[int, bool] = {}

    async def setup(self):
        creation_infos = await self.db_data_creator.batch_v2(
            TestBatchCreationParameters(
                urls=self.entries
            )
        )



