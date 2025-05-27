from pydantic import BaseModel

from src.db.DTOs.BatchInfo import BatchInfo


class GetBatchStatusResponse(BaseModel):
    results: list[BatchInfo]