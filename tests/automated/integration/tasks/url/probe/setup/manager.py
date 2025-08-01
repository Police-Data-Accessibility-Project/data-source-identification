from tests.helpers.data_creator.core import DBDataCreator


class TestURLProbeTaskSetupManager:

    def __init__(
        self,
        db_data_creator: DBDataCreator
    ):
        self.db_data_creator = db_data_creator

    async def setup(self):
