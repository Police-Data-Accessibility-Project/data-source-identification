from typing import List

from pydantic import BaseModel

from collector_db.DTOs.DuplicateInfo import DuplicateInfo


class GetDuplicatesByBatchResponse(BaseModel):
    duplicates: List[DuplicateInfo]