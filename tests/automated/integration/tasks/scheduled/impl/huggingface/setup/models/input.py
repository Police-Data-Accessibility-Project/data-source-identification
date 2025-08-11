from pydantic import BaseModel

from src.collectors.enums import URLStatus
from src.core.enums import RecordType


class TestPushToHuggingFaceURLSetupEntryInput(BaseModel):
    status: URLStatus
    record_type: RecordType | None
    has_html_content: bool
