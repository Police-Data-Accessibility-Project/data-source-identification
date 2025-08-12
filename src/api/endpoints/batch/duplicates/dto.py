from typing import List

from pydantic import BaseModel

from src.db.models.impl.duplicate.pydantic.info import DuplicateInfo


class GetDuplicatesByBatchResponse(BaseModel):
    duplicates: List[DuplicateInfo]