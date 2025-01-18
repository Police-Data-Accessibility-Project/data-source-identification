from pydantic import BaseModel

from collector_db.DTOs.URLMapping import URLMapping


class InsertURLsInfo(BaseModel):
    url_mappings: list[URLMapping]
    total_count: int = 0
    original_count: int = 0
    duplicate_count: int = 0
