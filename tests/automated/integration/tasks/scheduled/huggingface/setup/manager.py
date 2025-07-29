from src.core.tasks.scheduled.huggingface.queries.get.model import GetForLoadingToHuggingFaceOutput
from tests.automated.integration.tasks.scheduled.huggingface.setup.data import ENTRIES
from tests.automated.integration.tasks.scheduled.huggingface.setup.models.output import \
    TestPushToHuggingFaceURLSetupExpectedOutput
from tests.automated.integration.tasks.scheduled.huggingface.setup.models.record import \
    TestPushToHuggingFaceRecordSetupRecord as Record, TestPushToHuggingFaceRecordSetupRecord
from tests.automated.integration.tasks.scheduled.huggingface.setup.queries.setup import \
    SetupTestPushToHuggingFaceEntryQueryBuilder
from tests.helpers.data_creator.core import DBDataCreator


class PushToHuggingFaceTestSetupManager:

    def __init__(self, db_data_creator: DBDataCreator):
        self.db_data_creator = db_data_creator
        self.entries = ENTRIES
        # Connects a URL ID to the expectation that it will be picked up
        self._id_to_record: dict[int, TestPushToHuggingFaceRecordSetupRecord] = {}
        self._url_ids_not_picked_up = []

    async def setup(self) -> None:
        records: list[Record] = await self.db_data_creator.adb_client.run_query_builder(
            SetupTestPushToHuggingFaceEntryQueryBuilder(self.entries)
        )
        for record in records:

            if record.expected_output.picked_up:
                self._id_to_record[record.url_id] = record
            else:
                self._url_ids_not_picked_up.append(record.url_id)



    def check_results(self, outputs: list[GetForLoadingToHuggingFaceOutput]) -> None:


        for output in outputs:
            url_id = output.url_id
            expected_output = self._id_to_record[url_id]
            assert expected_output.picked_up

    def _check_expected_picked_up_results(self, outputs: list[GetForLoadingToHuggingFaceOutput]):
        # Check that both expected and actual results are same length
        length_expected = len(self._id_to_record.keys())
        length_actual = len(outputs)
        assert length_expected == length_actual

        # Check attributes of each URL match what is expected
        for output in outputs:
            url_id = output.url_id
            record = self._id_to_record[url_id]

            expected_output = record.expected_output
            assert output.relevant == expected_output.relevant
            assert output.record_type_coarse == expected_output.coarse_record_type
            assert output.record_type_fine == record.record_type_fine

    def check_for_results_not_picked_up(self):
        """Check that the expected URLs NOT picked up aren't picked up."""




