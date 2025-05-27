from typing import Optional

from pydantic import BaseModel

from db.DTOs.URLWithHTML import URLWithHTML
from core.enums import RecordType


class URLRecordTypeTDO(BaseModel):
    url_with_html: URLWithHTML
    record_type: Optional[RecordType] = None
    error: Optional[str] = None

    def is_errored(self):
        return self.error is not None