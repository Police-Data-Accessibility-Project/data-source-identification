from typing import Optional

from pydantic import BaseModel

from collector_db.DTOs.URLWithHTML import URLWithHTML
from core.enums import RecordType


class URLRecordTypeTaskInfo(BaseModel):
    url_with_html: URLWithHTML
    record_type: Optional[RecordType] = None