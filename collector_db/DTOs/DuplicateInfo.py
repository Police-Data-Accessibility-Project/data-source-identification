from pydantic import BaseModel


class DuplicateInfo(BaseModel):
    source_url: str
    original_url_id: int
    duplicate_metadata: dict
    original_metadata: dict