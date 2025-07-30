from pydantic import BaseModel

from tests.automated.integration.tasks.scheduled.huggingface.setup.models.input import \
    TestPushToHuggingFaceURLSetupEntryInput
from tests.automated.integration.tasks.scheduled.huggingface.setup.models.output import \
    TestPushToHuggingFaceURLSetupExpectedOutput


class TestPushToHuggingFaceURLSetupEntry(BaseModel):
    input: TestPushToHuggingFaceURLSetupEntryInput
    expected_output: TestPushToHuggingFaceURLSetupExpectedOutput

