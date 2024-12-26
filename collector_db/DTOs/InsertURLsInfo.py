from pydantic import BaseModel

from collector_db.DTOs.DuplicateInfo import DuplicateInfo
from collector_db.DTOs.URLMapping import URLMapping


class InsertURLsInfo(BaseModel):
    url_mappings: list[URLMapping]
    duplicates: list[DuplicateInfo]