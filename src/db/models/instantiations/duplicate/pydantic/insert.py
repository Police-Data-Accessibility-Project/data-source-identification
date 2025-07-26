from pydantic import BaseModel


class DuplicateInsertInfo(BaseModel):
    original_url_id: int
    duplicate_batch_id: int

