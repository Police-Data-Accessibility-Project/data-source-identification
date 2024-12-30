from pydantic import BaseModel


class DuplicateInsertInfo(BaseModel):
    original_url_id: int
    duplicate_batch_id: int

class DuplicateInfo(DuplicateInsertInfo):
    source_url: str
    original_batch_id: int
    duplicate_metadata: dict
    original_metadata: dict