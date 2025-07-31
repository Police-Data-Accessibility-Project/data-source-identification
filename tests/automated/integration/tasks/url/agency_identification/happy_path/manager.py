from tests.helpers.data_creator.core import DBDataCreator


class AgencyIdentificationTaskTestSetupManager:

    def __init__(
        self,
        db_data_creator: DBDataCreator
    ):
        pass

    async def setup(self):
        raise NotImplementedError

        # TODO: Set up pre-existing URLs