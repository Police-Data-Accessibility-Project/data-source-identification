from src.db.models.impl.duplicate.pydantic.insert import DuplicateInsertInfo


class DuplicateInfo(DuplicateInsertInfo):
    source_url: str
    original_batch_id: int
    duplicate_metadata: dict
    original_metadata: dict
