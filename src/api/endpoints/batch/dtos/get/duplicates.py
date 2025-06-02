from typing import List

from pydantic import BaseModel

from src.db.dtos.duplicate_info import DuplicateInfo


class GetDuplicatesByBatchResponse(BaseModel):
    duplicates: List[DuplicateInfo]