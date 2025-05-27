from typing import List

from pydantic import BaseModel

from src.db.DTOs.DuplicateInfo import DuplicateInfo


class GetDuplicatesByBatchResponse(BaseModel):
    duplicates: List[DuplicateInfo]