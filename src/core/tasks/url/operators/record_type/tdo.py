from typing import Optional

from pydantic import BaseModel

from src.db.dtos.url.with_html import URLWithHTML
from src.core.enums import RecordType


class URLRecordTypeTDO(BaseModel):
    url_with_html: URLWithHTML
    record_type: RecordType | None = None
    error: str | None = None

    def is_errored(self):
        return self.error is not None