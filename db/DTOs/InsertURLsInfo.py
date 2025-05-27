from pydantic import BaseModel

from db.DTOs.URLMapping import URLMapping


class InsertURLsInfo(BaseModel):
    url_mappings: list[URLMapping]
    url_ids: list[int]
    total_count: int = 0
    original_count: int = 0
    duplicate_count: int = 0
