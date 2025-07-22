from typing import List

from pydantic import BaseModel

from src.db.dtos.duplicate import DuplicateInfo


class GetDuplicatesByBatchResponse(BaseModel):
    duplicates: List[DuplicateInfo]