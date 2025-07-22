from typing import List

from pydantic import BaseModel

from src.db.models.instantiations.duplicate.pydantic.info import DuplicateInfo


class GetDuplicatesByBatchResponse(BaseModel):
    duplicates: List[DuplicateInfo]