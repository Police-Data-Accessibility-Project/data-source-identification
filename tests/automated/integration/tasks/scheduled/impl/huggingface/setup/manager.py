from src.core.tasks.scheduled.impl.huggingface.queries.get.model import GetForLoadingToHuggingFaceOutput
from src.db.client.async_ import AsyncDatabaseClient
from tests.automated.integration.tasks.scheduled.impl.huggingface.setup.data import ENTRIES
from tests.automated.integration.tasks.scheduled.impl.huggingface.setup.models.record import \
    TestPushToHuggingFaceRecordSetupRecord as Record, TestPushToHuggingFaceRecordSetupRecord
from tests.automated.integration.tasks.scheduled.impl.huggingface.setup.queries.setup import \
    SetupTestPushToHuggingFaceEntryQueryBuilder


class PushToHuggingFaceTestSetupManager:

    def __init__(self, adb_client: AsyncDatabaseClient):
        self.adb_client = adb_client
        self.entries = ENTRIES
        # Connects a URL ID to the expectation that it will be picked up
        self._id_to_record: dict[int, TestPushToHuggingFaceRecordSetupRecord] = {}

    async def setup(self) -> None:
        records: list[Record] = await self.adb_client.run_query_builder(
            SetupTestPushToHuggingFaceEntryQueryBuilder(self.entries)
        )
        for record in records:
            if not record.expected_output.picked_up:
                continue
            self._id_to_record[record.url_id] = record

    def check_results(self, outputs: list[GetForLoadingToHuggingFaceOutput]) -> None:
        # Check that both expected and actual results are same length
        length_expected = len(self._id_to_record.keys())
        length_actual = len(outputs)
        assert length_expected == length_actual, f"Expected {length_expected} results, got {length_actual}"

        # Check attributes of each URL match what is expected
        for output in outputs:
            url_id = output.url_id
            record = self._id_to_record[url_id]

            expected_output = record.expected_output
            assert output.relevant == expected_output.relevant
            assert output.record_type_coarse == expected_output.coarse_record_type, \
                f"Expected {expected_output.coarse_record_type} but got {output.record_type_coarse}"
            assert output.record_type_fine == record.record_type_fine

