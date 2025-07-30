from pydantic import BaseModel

from src.core.enums import RecordType
from tests.automated.integration.tasks.scheduled.huggingface.setup.models.output import \
    TestPushToHuggingFaceURLSetupExpectedOutput


class TestPushToHuggingFaceRecordSetupRecord(BaseModel):
    expected_output: TestPushToHuggingFaceURLSetupExpectedOutput
    record_type_fine: RecordType | None
    url_id: int